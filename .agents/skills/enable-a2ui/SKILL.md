---
name: enable-a2ui
description: Faz um agente ADK emitir A2UI para que as respostas dele sejam renderizadas como uma interface visual rica (cards, tabelas construídas a partir de linhas/colunas e imagens a partir de uma URL pública) na interface de desenvolvimento do ADK (adk web) em vez de texto puro. Use quando a pessoa quiser adicionar A2UI ao agente dela, renderizar cards ou tabelas no adk web, exibir uma imagem dentro de um card, ou quando o A2UI aparecer como JSON bruto ou como um card em branco. Inclui um a2ui_utils.py pronto para usar (o after_model_callback de que o renderizador do adk web precisa) em ./template. Apenas para visualização no adk web (botões, ações e modais não funcionam); enviar A2UI para um frontend personalizado de produção é um processo separado.
---

# Habilitar A2UI (renderização no adk web)

Faça um agente ADK retornar **A2UI** para que o `adk web` renderize cards em vez de texto puro.
Você precisa de **ambos** os elementos, ou só vai ver JSON bruto:

1. Um **system prompt** que ensine o modelo a emitir JSON de A2UI (`A2uiSchemaManager`).
2. Um **`after_model_callback`** que reempacote esse JSON no formato que o renderizador do adk web detecta — incluído pronto para usar como **`./template/a2ui_utils.py`**. Copie, não reescreva.

> **Use a versão `0.8` em todos os lugares.** O callback reage a mensagens da v0.8 (`beginRendering`, `surfaceUpdate`). Saídas na v0.9 não serão renderizadas.

## Passo 0 — Instalar o SDK

`A2uiSchemaManager` / `BasicCatalog` (Passo 2) vêm do pacote **`a2ui-agent-sdk`**:

```bash
uv add "a2ui-agent-sdk>=0.4.0,<0.5.0"
```

- **Pegadinha do nome:** o pacote se chama `a2ui-agent-sdk`, mas você o **importa** como `a2ui` (`from a2ui.schema.manager import ...`). Não execute `pip install a2ui` nem adicione uma dependência direta `a2ui`; ela não existe e o `uv sync` vai falhar com *"a2ui was not found"*.
- **Use `uv add`, não `uv pip install`.** O `uv add` registra a dependência no `pyproject.toml`/`uv.lock`, o que o `agents-cli deploy` exige. O `uv pip install` afeta apenas o venv: vai funcionar no playground, mas depois o agente implantado falha com `ModuleNotFoundError: No module named 'a2ui'`.
- Não é necessário sobrescrever o índice, listar manualmente o `a2ui-core` nem clonar o repositório com `git clone`. Fixe a versão `0.4.x`; versões maiores posteriores mudam os caminhos de importação usados abaixo.

## Passo 1 — Copiar o callback

Copie o `./template/a2ui_utils.py` para junto do seu arquivo `agent.py`. Ele é autocontido (requer apenas `google-adk` / `google-genai`).

## Passo 2 — Construir o system prompt

```python
from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description="<o que é / o que faz o seu agente>",
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)
```

## Passo 3 — Conectar o callback no agente

```python
from google.adk.agents import Agent
from .a2ui_utils import a2ui_callback

root_agent = Agent(
    model="<seu modelo>",
    name="<seu agente>",
    instruction=instruction,
    tools=[...],
    after_model_callback=a2ui_callback,   # <- é isto que faz o adk web renderizar
)
```

## Passo 4 — Testar no adk web

```bash
uv run adk web --port 8080 --allow_origins "*" --reload_agents
```

> Use **`uv run`**, não um comando `adk web` direto. Um `adk` direto usa um Python global que não tem as dependências do seu projeto e vai falhar ao iniciar (`cannot import name 'firestore' from 'google.cloud'` / `ModuleNotFound`). O `uv run` usa o `.venv` do projeto.

Inicie uma **Nova Sessão (New Session)** e peça algo visual — você deve ver um card, não JSON. **Desative o Token Streaming** primeiro (ícone de engrenagem na UI de desenvolvimento): se estiver ativo, o adk web mostra o JSON transmitido bruto e nunca o substitui pelo card.

## Limites do renderizador do adk web (projete considerando isso)

- **Somente visualização.** Botões, ações e formulários são renderizados mas não fazem nada. Para interatividade real, use um frontend personalizado (`build-agent-frontend`).
- **Componentes suportados:** `Card, Column, Row, Text, Divider, List, Icon, Image`. Sem suporte a `Table` ou `Heading`: construa tabelas a partir de linhas/colunas de `Text`, e use `Text` + `usageHint` para os cabeçalhos.
- **Imagens exigem uma URL pública `http(s)`.** Um componente `Image` é renderizado inline apenas se a url dele for um link `https` acessível. Se o seu agente faz upload de uma imagem gerada para um bucket público e passa essa URL para o `Image`, ela será renderizada inline dentro do card. Uma imagem salva apenas como artefato local não tem uma URL acessível, então um `Image` apontado para esse nome de arquivo vai mostrar um ícone quebrado; o callback substitui imagens sem `http(s)` por uma breve nota de texto, e a imagem ainda aparece no painel de Artifacts. Consulte `build-agent-frontend` para exibir imagens em um frontend personalizado.
- **Estruturas pequenas e planas renderizam melhor.** Aninhamentos profundos e cards grandes renderizam em branco. O callback descarta surfaces corrompidas (JSON inválido, raiz não definida, referências soltas) e mostra uma mensagem alternativa curta.
- **O renderizador é instável:** mesmo uma surface válida pode, às vezes, renderizar em branco. Isso é um detalhe do renderizador do adk-web, não uma falha do seu agente.

## Solução de problemas

| O que você vê | Solução mais provável |
| --- | --- |
| `ModuleNotFoundError: No module named 'a2ui'` (localmente) | O SDK não está instalado — execute `uv add "a2ui-agent-sdk>=0.4.0,<0.5.0"` (Passo 0). A importação é `a2ui`, o pacote é `a2ui-agent-sdk` |
| Funciona localmente mas o agente **implantado** lança `No module named 'a2ui'` | Você usou `uv pip install` (só no venv). Execute `uv add "a2ui-agent-sdk>=0.4.0,<0.5.0"` para registrá-lo no `pyproject.toml` e faça o deploy novamente |
| `uv sync` falha: `a2ui was not found in the package registry` | Você adicionou o nome errado. Remova `a2ui` das dependências; use `a2ui-agent-sdk` no lugar (Passo 0) |
| JSON sem formatação enquanto ele escreve | O Token Streaming está ATIVADO — desative-o (engrenagem), recarregue a página (hard-refresh) e inicie uma Nova Sessão |
| JSON sem formatação (sem streaming) | O callback não está conectado (`after_model_callback=a2ui_callback`), ou está sendo usada uma versão incorreta (use `0.8`) |
| Card em branco | A surface é grande/complexa demais — peça algo mais simples; ou o estado da UI travou — recarregue a página + Nova Sessão |

## Referência

- Template: `./template/a2ui_utils.py` (o `after_model_callback`)
- Integração de A2UI no ADK: https://adk.dev/integrations/a2ui/
- Especificação do A2UI (opcional): https://a2ui.org/
