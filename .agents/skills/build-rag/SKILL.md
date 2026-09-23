---
name: rag-engine-setup
description: >
  Configura um corpus do Vertex AI RAG Engine (Agent Platform) em modo serverless e o conecta a um agente ADK. Use quando a pessoa quiser "criar um corpus de RAG", "construir um repositório de RAG", "fundamentar meu agente em documentos", "adicionar retrieval ao meu agente", ou encontrar erros de Spanner/allowlist ao criar um corpus. Cobre o upload para o Cloud Storage (GCS), a mudança para o modo serverless, o parser com LLM (prompt de parsing personalizado), a importação, testes de retrieval isolados e como expor o retrieval como uma function tool comum (necessário para que ele coexista com A2UI ou outras function tools no Gemini 2.5).
---

# Vertex AI RAG Engine — corpus serverless + integração com ADK

Um **corpus** do RAG Engine é um índice gerenciado: você o aponta para documentos no Cloud Storage (ou Drive), ele os divide em chunks, gera embeddings e armazena os vetores em um banco de dados vetorial gerenciado. Depois, um agente consulta o corpus em tempo de execução por meio de uma **retrieval tool** e fundamenta as respostas nos trechos retornados.

Esta skill constrói um corpus em **modo serverless** — a opção mais econômica, sem allowlists e totalmente gerenciada — e mostra como o agente o consome.

## Modelo mental (como funciona de ponta a ponta)

```
Ingestão (uma vez): documentos no GCS ──▶ LLM parser ──▶ chunking ──▶ gerar embeddings ──▶ Vector Search gerenciado
                                          (prompt personalizado)      (text-embedding-005)

Consulta (runtime): turno do usuário ─▶ LLM do agente decide chamar a retrieval tool
                                      ─▶ a tool executa retrieval_query(corpus, text) ─▶ chunks top-k
                                      ─▶ chunks injetados no contexto do modelo
                                      ─▶ o modelo redige uma resposta fundamentada (opcionalmente cita fontes)
```

Duas partes móveis: **o corpus** (construído uma única vez, abaixo) e a **retrieval tool** que o agente chama (última seção). O agente nunca fala diretamente com o banco vetorial — ele chama uma tool, e a tool chama o serviço de RAG.

## Modos de implantação — escolha serverless

| Modo | Backend | Precisa de allowlist? | Custo | Quando usar |
|------|---------|-----------|------|------|
| **Serverless** (preview) | Vector Search gerenciado | Não | Sem custo base de serviço | **Padrão / tutoriais** |
| Spanner (tier Basic/Scaled) | `RagManagedDb` (Spanner) | Sim em us-central1/-east1/-east4 | Infraestrutura do Spanner | CMEK, residência de dados, instâncias dedicadas |

O serverless está disponível **apenas em us-central1** e exige o namespace **`vertexai.preview.rag`** — o namespace GA `vertexai.rag` só expõe `tier=` para Spanner e não permite selecionar serverless. O serverless **não** suporta CMEK / residência de dados / Access Approval.

## Pré-requisitos (uma única vez)

```bash
PROJECT=seu-project-id
gcloud config set project "$PROJECT"

# Habilite as APIs. vectorsearch é obrigatório porque o serverless o usa como backend.
gcloud services enable aiplatform.googleapis.com vectorsearch.googleapis.com --project="$PROJECT"

# Coloque seus documentos de origem em um bucket do Cloud Storage (GCS) (suporta HTML/PDF/TXT/Google Docs).
gcloud storage cp ./meus_docs/*.txt gs://seu-bucket/rag/
```

**Versão do SDK:** use uma versão **recente** do `google-cloud-aiplatform` (≥ 1.90; testado na 1.163). A configuração do modo serverless e o `rag.RagRetrievalConfig` usados abaixo **não** existem em versões anteriores — por exemplo, a 1.71 lança `AttributeError: module 'vertexai.preview.rag' has no attribute 'RagRetrievalConfig'`. Instalar o `google-adk` pode fixar uma versão antiga do aiplatform, então atualize explicitamente: `pip install -U google-cloud-aiplatform`. (O `vertexai.preview.rag` agora emite um aviso de descontinuação apontando para o novo cliente `agentplatform`; o namespace preview continua funcionando perfeitamente hoje).

## Construir o corpus

`scripts/create_rag_corpus.py`:

```python
from vertexai.preview import rag                      # namespace preview = suporte a serverless
from vertexai.preview.rag.utils import resources as rr
import vertexai

PROJECT_ID = "seu-project-id"
LOCATION   = "us-central1"                             # serverless só está disponível em us-central1
GCS_PATH   = "gs://seu-bucket/rag/"                    # um arquivo ou um prefixo

# Instrução personalizada para o parser com LLM — extrai o relevante, elimina o ruído.
PARSING_PROMPT = (
    "Extract the individual useful facts and recipes described in this text. "
    "Ignore and omit all metadata, boilerplate, and image captions. "
    "Output clean, self-contained prose."
)

vertexai.init(project=PROJECT_ID, location=LOCATION)

# 1. Muda o banco gerenciado de RAG da região para o modo serverless (nível de projeto, uma vez).
cfg = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragEngineConfig"
rag.update_rag_engine_config(rag_engine_config=rag.RagEngineConfig(
    name=cfg,
    rag_managed_db_config=rag.RagManagedDbConfig(mode=rr.Serverless()),
))

# 2. Cria o corpus. O serverless seleciona automaticamente o backend do Vector Search gerenciado;
#    você só escolhe o modelo de embeddings.
corpus = rag.create_corpus(
    display_name="my-corpus",
    embedding_model_config=rag.EmbeddingModelConfig(
        publisher_model="publishers/google/models/text-embedding-005"),
)
print("corpus:", corpus.name)   # guarde isto — o agente precisa dele

# 3. Importar + fazer o parse + chunking + gerar embeddings. O parser com LLM aplica o PARSING_PROMPT por arquivo.
resp = rag.import_files(
    corpus_name=corpus.name,
    paths=[GCS_PATH],
    transformation_config=rag.TransformationConfig(
        chunking_config=rag.ChunkingConfig(chunk_size=512, chunk_overlap=100)),
    llm_parser=rag.LlmParserConfig(
        model_name="gemini-2.5-flash",
        custom_parsing_prompt=PARSING_PROMPT),
)
print("imported:", resp.imported_rag_files_count)
```

**Escolha do parser:** parser padrão (gratuito, texto limpo) < **LLM parser** (extração semântica via prompt — ideal para eliminar texto repetitivo ou irrelevante) < layout parser (Document AI, ideal para tabelas/gráficos). O chunking roda depois do parsing em todos os casos.

## Testar SEM mexer no código do agente

Somente retrieval — confirme que o índice devolve trechos adequados, sem invocar um LLM:

```python
from vertexai.preview import rag
import vertexai
vertexai.init(project="seu-project-id", location="us-central1")

resp = rag.retrieval_query(
    text="what is good for a cough?",
    rag_resources=[rag.RagResource(rag_corpus="projects/.../ragCorpora/NNN")],
    rag_retrieval_config=rag.RagRetrievalConfig(top_k=5),
)
for c in resp.contexts.contexts:
    print(c.score, c.text[:200])
```

Você também pode testar no **Cloud Console**: Vertex AI → RAG Engine → seu corpus → painel Retrieve. Depois da importação, dê um breve tempo de indexação (o retrieval pode devolver 404 por um instante mesmo quando o arquivo aparece como `ACTIVE`).

## Conectar ao agente (ADK) — exponha o retrieval como uma function tool comum

O agente acessa o corpus por meio de uma **retrieval tool**. Envolva o `rag.retrieval_query` em uma função Python padrão e registre *essa* função como a tool do agente. **Faça isso em vez de usar o `VertexAiRagRetrieval` do ADK** — veja o aviso de compatibilidade abaixo para entender por que isso é crucial.

```python
from google.adk.agents import Agent

CORPUS_NAME = "projects/.../ragCorpora/NNN"   # obtido do create_rag_corpus.py

def consult_docs(query: str) -> str:
    """Search the herbal corpus and return matched passages.

    Args:
        query: What to look up (a plant, ailment, or recipe).
    Returns:
        The matched passages, or a note that none was found.
    """
    from vertexai.preview import rag
    try:
        resp = rag.retrieval_query(
            text=query,
            rag_resources=[rag.RagResource(rag_corpus=CORPUS_NAME)],
            rag_retrieval_config=rag.RagRetrievalConfig(top_k=5),
        )
    except Exception as e:
        return f"Retrieval failed: {e}"
    contexts = getattr(resp.contexts, "contexts", [])
    passages = [c.text.strip() for c in contexts if getattr(c, "text", "").strip()]
    return "\n\n---\n\n".join(passages) or "No relevant passage found."

agent = Agent(
    model="gemini-2.5-flash",
    name="apothecary",
    instruction="Answer using the herbal corpus. Call consult_docs before answering.",
    tools=[consult_docs],   # junto com quaisquer outras tools, ex. o toolset do A2UI
)
```

Em tempo de execução, o modelo decide quando chamar `consult_docs`; a função executa o `retrieval_query` contra o corpus e devolve os melhores chunks (top-k) como resultado, que o modelo lê para redigir uma resposta fundamentada. A docstring da função é fundamental — ela é a declaração da função para a tool, então é assim que o modelo sabe quando usá-la.

### ⚠️ Compatibilidade: NÃO use `VertexAiRagRetrieval` junto com outras function tools

O `VertexAiRagRetrieval` do ADK (de `google.adk.tools.retrieval`) **não** é registrado como uma function tool normal — ele é registrado como a **built-in retrieval grounding tool** do Gemini. Os modelos Gemini 2.5 (`gemini-2.5-flash` e `gemini-2.5-pro`) **rejeitam qualquer requisição que combine a retrieval tool nativa com declarações de funções normais no turno que carrega um `functionResponse`**. Portanto, no instante em que seu agente tem *qualquer* outra function tool — por exemplo, o toolset do A2UI (`SendA2uiToClientToolset` / `send_a2ui_to_client`) — a combinação se torna inválida.

- **Sintoma:** a primeira requisição ao modelo funciona; a falha aparece no turno seguinte, logo depois que a primeira chamada de tool retorna — um erro direto `400 Bad Request ... INVALID_ARGUMENT` sem detalhamento de campos. Parece intermitente ou misterioso e consome muito tempo de depuração.
- **A solução é a function tool comum mostrada acima** — o retrieval vira apenas mais uma declaração de função, nenhuma built-in grounding tool é incluída na requisição e a combinação é totalmente válida em qualquer modelo ou versão.
- **Não** tente "resolver" trocando para um alias variável como `gemini-flash-latest`; hoje ele pode tolerar a combinação por acaso, mas não é confiável. Desenvolva sempre contra os modelos 2.5 fixados.
- Esta é uma regra geral, não uma peculiaridade do RAG: **nenhuma tool built-in** (retrieval, grounding com Google Search, execução de código) pode compartilhar uma requisição com declarações de funções normais. Exponha a capacidade como uma função comum sempre que você também precisar de function calling.

**Consideração de região (comum em produção):** um corpus serverless fica apenas em `us-central1`, mas o modelo do seu agente muitas vezes roda em outra região (por exemplo, `GOOGLE_CLOUD_LOCATION=global`). O `rag.retrieval_query` roda contra a região em que o **SDK do aiplatform** foi inicializado — se ela não coincidir com a região do corpus, você recebe um erro `MethodNotImplemented / 404`. O cliente do modelo genai (baseado em variáveis de ambiente) e os serviços de session/memory do ADK (com `location=` explícito) NÃO usam o inicializador do SDK do aiplatform, então você pode inicializar com segurança apenas o cliente de RAG na região do corpus:

```python
import vertexai
# região extraída de projects/<p>/locations/<region>/ragCorpora/<id>
vertexai.init(project="...", location="us-central1")  # antes da primeira chamada a retrieval_query
```

Para orientar o modelo sobre *como* responder, coloque isso na instrução do agente, por exemplo:
"When you rely on the Herbal's words, quote the passage verbatim in quotation marks and name it as Culpeper's Complete Herbal; otherwise paraphrase."

## Solução de problemas

- `INVALID_ARGUMENT ... Spanner mode ... restricted to allowlisted projects` → você está usando o namespace GA ou o modo Spanner. Use `vertexai.preview.rag` + `mode=rr.Serverless()`.
- `PERMISSION_DENIED ... Vector Search API has not been used` → habilite `vectorsearch.googleapis.com`, espere ~1 min e tente novamente.
- `NOT_FOUND No vertex rag corpus found` logo após importar → atraso de indexação; tente de novo após alguns segundos.
- Erro direto `400 ... INVALID_ARGUMENT` (sem detalhamento de campos) no turno imediatamente posterior ao retorno da primeira chamada de tool → você está combinando `VertexAiRagRetrieval` (built-in grounding tool) com function tools. Exponha o retrieval como uma function tool comum (ver o aviso de compatibilidade acima).
