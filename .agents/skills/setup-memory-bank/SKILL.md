---
name: memory-bank-setup
description: >
  Adiciona memória de longo prazo entre sessões a um agente ADK usando o Vertex AI Memory Bank do Agent Platform, e o conecta ao agente. Use quando a pessoa quiser "adicionar memória", "adicionar um Memory Bank", "lembrar dados/preferências entre sessões", "fazer meu agente se lembrar de mim entre conversas", ou perguntar por que as memórias não persistem ou não aparecem no Cloud Console. Cobre a conexão do lado do agente (PreloadMemoryTool + um callback de geração de memória), a criação da instância gerenciada do Memory Bank, como apontar o serviço de memória do runtime para ela (ADK Web local e Agent Runtime implantado), a verificação no Console, e o ponto importante de que o `agents-cli deploy` NÃO configura um serviço de memória sozinho.
---

# Vertex AI Memory Bank — memória entre sessões + integração com ADK

As **sessions** lembram uma conversa. O **Memory Bank** lembra fatos e preferências *ao longo de várias* conversas (por exemplo, "a pessoa é intolerante a glúten", "me chame de Dr. Vance", "responda sempre no sistema métrico"). A cada turno, o Memory Bank lê a conversa, extrai trechos duradouros e os armazena associados a um `user_id`, para que sessões futuras possam lembrá-los.

Esta skill adiciona o Memory Bank a um agente ADK (incluindo projetos estruturados com `agents-cli`) e faz a conexão de ponta a ponta.

## Modelo mental (como funciona de ponta a ponta)

```
Escrita (por turno): eventos de sessão ─▶ after_agent_callback ─▶ add_session_to_memory()
                                        ─▶ Memory Bank extrai e armazena fatos duradouros

Leitura (por turno): PreloadMemoryTool ─▶ search_memory(user_id) no início do turno
                                        ─▶ memórias relevantes injetadas na instrução de sistema
```

Duas partes móveis:
1. **O código do agente** — uma *tool* de memória (leitura) + um *callback* (escrita). É idêntico para qualquer ambiente de execução.
2. **Um serviço de memória** apontando para uma **instância de Memory Bank**. Esta é a parte que muda entre o ambiente local e o implantado, e a parte que o `agents-cli` **não** configura automaticamente.

## O detalhe principal que costuma confundir

**Uma "instância de Memory Bank" é simplesmente uma instância de Agent Engine (Reasoning Engine).** Ela é criada com `client.agent_engines.create()`; o nome do recurso é `projects/<p>/locations/<loc>/reasoningEngines/<ID>` e `<ID>` é o ID do Memory Bank que você passa em todo lugar como `agentengine://<ID>`.

Consequências:
- O Memory Bank é um **recurso gerenciado na nuvem** — você não consegue ver memórias reais e persistentes em uma execução local puramente em memória. O ADK usa `InMemoryMemoryService` por padrão, a menos que você o aponte explicitamente para uma instância de Memory Bank.
- **O `agents-cli deploy` não conecta um serviço de memória.** Ele configura um serviço de *sessions* no Agent Runtime, mas deixa o serviço de memória com o valor padrão do ADK. Adicionar a tool + callback é necessário, mas **não suficiente** — você também precisa apontar um serviço de memória para uma instância de Memory Bank (passos abaixo).
- Como é um recurso na nuvem, faça o trabalho de memória **depois** (ou em paralelo) de um primeiro deploy, ou crie uma instância independente para testes locais — não antes de existir algum Agent Engine.

## Pré-requisitos (uma única vez)

```bash
PROJECT=seu-project-id
LOCATION=us-central1          # use uma região compatível com o Memory Bank
gcloud config set project "$PROJECT"
gcloud services enable aiplatform.googleapis.com --project="$PROJECT"
gcloud auth application-default login   # já feito se você entrou pelo `agy`
```

O Memory Bank funciona em regiões específicas — consulte
https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/agent-locations.
Mantenha `GOOGLE_CLOUD_LOCATION` alinhada com a região em que você criar a instância.

## Passo 1 — Conectar o agente (tool + callback)

Edite a definição do agente (em um projeto `agents-cli`, é o `app/agent.py`).
Adicione um **callback de geração de memória** e uma **tool de memória**:

```python
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
# Tool alternativa: from google.adk.tools.load_memory_tool import LoadMemoryTool


# ESCRITA: depois de cada turno, envia a sessão ao Memory Bank para extração.
async def generate_memories_callback(callback_context: CallbackContext):
    await callback_context.add_session_to_memory()
    return None


root_agent = Agent(
    model="gemini-2.5-flash",
    name="root_agent",
    instruction=(
        "You are a helpful assistant. You remember the user's stated "
        "preferences and facts from previous conversations and use them to "
        "personalize your responses."
    ),
    # LEITURA: PreloadMemoryTool recupera memórias no início de cada turno e
    # as injeta na instrução de sistema (não requer chamada explícita à tool).
    # Use LoadMemoryTool() no lugar se preferir que o modelo as consulte sob demanda.
    tools=[PreloadMemoryTool()],
    after_agent_callback=generate_memories_callback,
)
```

Essa é toda a mudança no código do agente. Ela independe do runtime — o mesmo código funciona localmente e implantado. **`add_session_to_memory()` e as tools não têm efeito diante de um serviço em memória**, então elas só geram memórias persistentes quando uma instância real de Memory Bank é conectada (próximos passos).

> Envie para a memória apenas os turnos relevantes. `add_session_to_memory()` ao final de um turno é a forma mais simples; para um controle mais fino, use `callback_context.add_events_to_memory(events=...)` com um subconjunto de eventos.

## Passo 2 — Criar uma instância de Memory Bank

Se você **já fez o deploy** com o `agents-cli`, já tem um Agent Engine — você pode reutilizar o ID dele como ID do Memory Bank (pule para o Passo 3). Caso contrário, crie uma instância independente (`scripts/create_memory_bank.py`):

```python
import vertexai

PROJECT_ID = "seu-project-id"
LOCATION   = "us-central1"

client = vertexai.Client(project=PROJECT_ID, location=LOCATION)

# Uma instância de Memory Bank É uma instância de Agent Engine. A configuração
# padrão é adequada para o lab; ela extrai dados e preferências gerais do usuário automaticamente.
memory_bank = client.agent_engines.create()

resource_name = memory_bank.api_resource.name       # projects/.../reasoningEngines/NNN
memory_bank_id = resource_name.split("/")[-1]        # NNN  ← use isto em todo lugar
print("MEMORY_BANK_ID:", memory_bank_id)
print("resource name :", resource_name)
```

Guarde o `MEMORY_BANK_ID` impresso. (Para personalizar *quais* temas são extraídos — `USER_PERSONAL_INFO`, `USER_PREFERENCES`, `EXPLICIT_INSTRUCTIONS`, `KEY_CONVERSATION_DETAILS` — consulte a seção "Configure your Memory Bank instance" na documentação; a configuração padrão não exige ajustes).

## Passo 3 — Apontar um serviço de memória para a instância

É preciso fornecer ao serviço de memória o URI `agentengine://<MEMORY_BANK_ID>`. Escolha a linha que corresponde à forma como o agente roda:

| Runtime | Como conectar o serviço de memória |
|---|---|
| **ADK Web local** (o mais rápido para testar) | `adk web --memory_service_uri=agentengine://MEMORY_BANK_ID` |
| **Implantado no Agent Runtime** | Configure o serviço de memória no app (abaixo) para que o contêiner implantado use o Memory Bank e não o padrão em memória |
| **`Runner` / script local** | `VertexAiMemoryBankService(project=..., location=..., agent_engine_id=MEMORY_BANK_ID)` passado ao `Runner(memory_service=...)` |

### Teste local (recomendado primeiro)

```bash
export GOOGLE_CLOUD_PROJECT="seu-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
# Execute a partir da pasta que contém o pacote do agente (por exemplo, a raiz do projeto
# com app/ dentro). Isso sobrescreve o padrão em memória do ADK.
adk web --memory_service_uri=agentengine://MEMORY_BANK_ID
```

O `agents-cli playground` executa o `adk web`, mas não repassa o `--memory_service_uri`, então, para testar um Memory Bank *real* localmente, execute o `adk web` diretamente com a flag.

### Implantado no Agent Runtime (projeto agents-cli)

O `agents-cli deploy` não vai anexar um serviço de memória, então você precisa definir um explicitamente no app para que o contêiner implantado use o Memory Bank. Na definição do app ADK (a configuração de `AdkApp` / `get_fast_api_app` — consulte as skills `google-agents-cli-deploy` e `google-agents-cli-adk-code` para localizar o arquivo exato conforme a versão do projeto), forneça um builder de serviço de memória:

```python
from google.adk.memory import VertexAiMemoryBankService

def memory_bank_service_builder():
    return VertexAiMemoryBankService(
        project="seu-project-id",
        location="us-central1",
        agent_engine_id="MEMORY_BANK_ID",   # reutilize o ID do engine implantado, ou um independente
    )
# Passe memory_service_builder=memory_bank_service_builder para AdkApp,
# ou --memory_service_uri=agentengine://MEMORY_BANK_ID para o comando de deploy do ADK.
```

Depois faça o deploy novamente. Confirme que o agente implantado realmente persiste as memórias (Passo 4) — não presuma que a configuração padrão fez isso.

## Passo 4 — Verificar

1. **Converse com o agente** (no ADK Web local ou no playground implantado): mencione um fato duradouro, por exemplo, *"Lembre-se de que eu sou alérgico a penicilina."*
2. **Inicie uma NOVA sessão** e pergunte algo que dependa desse dado — o agente deve lembrar sem que você precise repetir.
3. **Veja a memória armazenada no Cloud Console:**
   https://console.cloud.google.com/agent-platform/memory-bank
   (Vertex AI → Agent Engines → sua instância → Memory Bank.) Espere alguns segundos — a extração roda em segundo plano depois do turno.

## Solução de problemas

- **As memórias nunca persistem / não há nada no Console** → você está usando o padrão `InMemoryMemoryService`. A tool + callback sozinhos não criam um bank; você precisa passar `--memory_service_uri=agentengine://<ID>` (local) ou configurar o `VertexAiMemoryBankService` no app implantado. Esta é a causa nº 1.
- **Funciona localmente mas não quando implantado** → o `agents-cli deploy` não conectou um serviço de memória; adicione `memory_service_builder` / `memory_service_uri` e faça o deploy novamente (Passo 3, linha de implantado).
- **Lembra dentro da mesma sessão mas não entre sessões diferentes** → você está vendo o *estado da sessão*, não a memória de longo prazo. Confirme que `PreloadMemoryTool` está em `tools` e que `after_agent_callback` está configurado, além de que ambas as sessões usam o **mesmo `user_id`** (as memórias têm escopo definido por `user_id` + `app_name`).
- **`NOT_FOUND` / erros de permissão no serviço de memória** → a região do `MEMORY_BANK_ID` precisa coincidir com `GOOGLE_CLOUD_LOCATION` e ser uma região suportada pelo Memory Bank; a conta que faz a chamada ou a service account precisa de `roles/aiplatform.user`.
- **`'await' outside function` em um script independente** → envolva as chamadas assíncronas em `asyncio.run(...)`; o ADK é assíncrono desde a base.
