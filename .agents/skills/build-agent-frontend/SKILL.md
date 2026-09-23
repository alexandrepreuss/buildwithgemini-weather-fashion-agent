---
name: build-agent-frontend
description: Constrói um frontend web de chat para um agente ADK / Agent Engine implantado e o conecta (navegador -> proxy FastAPI -> agente via protocolo A2A), e depois faz o deploy no Cloud Run. Pensado para deploys de Agent Runtime com agents-cli 1.1.0 (GA), em que o proxy se comunica via A2A (o caminho antigo de stream_query / operation_schemas não está mais disponível). A interface de chat mostra respostas em texto puro E TAMBÉM renderiza nativamente os cards A2UI do agente por meio de um pequeno renderizador integrado, então funciona tanto se o agente tiver A2UI habilitado quanto se não tiver. Use quando a pessoa quiser construir um frontend, uma interface de chat ou uma interface web para o agente implantado dela, conectar uma interface de usuário ao agente, configurar o proxy FastAPI, resolver a autenticação navegador-proxy-agente, ou depurar um frontend que não consegue se comunicar com um deploy 1.1.0. A2UI é um recurso do lado do agente (ver a skill enable-a2ui); esta skill o renderiza no frontend personalizado. Inclui um template completo e funcional (proxy FastAPI + UI de chat + renderizador A2UI) em ./template. Não use para lógica do lado do agente que não tenha relação com a UI.
---

# Construir um frontend de chat

Dê a um agente implantado uma **interface de chat web** simples e conecte-a ao agente. A
estrutura usa um **proxy FastAPI** leve: o navegador se comunica exclusivamente com o proxy,
e o proxy se autentica junto ao agente implantado. A interface mostra **respostas em texto puro**
e também **renderiza os cards A2UI do agente** de forma nativa (por meio de um pequeno renderizador integrado),
então funciona tanto se o agente tiver `enable-a2ui` quanto se não tiver. Um frontend completo
e funcional está incluído em **`./template`** — copie, não reconstrua do zero.

> **A regra principal:** copie o `./template` para dentro do projeto como `frontend/` e faça
> o mínimo de mudanças possível. **NÃO** construa um app em React, não configure um novo
> framework de UI e não copie um projeto de exemplo grande. O template é suficiente.

## Como funciona

```
Navegador (chat UI)  ->  Proxy FastAPI (main.py)  ->  Agente implantado
```

- O navegador só se comunica com o proxy (mesma origem, sem CORS, sem credenciais de nuvem no cliente).
- O proxy se autentica via Application Default Credentials e se comunica com o
  agente implantado pelo protocolo A2A. O agents-cli 1.1.0 (GA) implanta agentes ADK
  no Agent Runtime como agentes A2A e não registra mais o schema de operações do reasoning-engine,
  então o caminho antigo `agent_engines.get(...).stream_query()` ficou obsoleto
  (o método `operation_schemas()` dele fica vazio). O proxy busca o agent card A2A
  uma vez e depois envia cada mensagem usando o cliente do a2a-sdk (o mesmo caminho que
  o `agents-cli run --mode a2a` usa). Isso funciona tanto para deploys A2A quanto para deploys ADK 1.1.0
  padrão, já que o contêiner serve A2A nos dois casos.
- Ele reutiliza um contexto A2A por usuário, para que o agente lembre a conversa.
- O proxy devolve partes estruturadas (`text` ou `a2ui`); a interface mostra respostas de texto
  e renderiza os cards A2UI.

## Passo 1 — Copiar o template

Copie o `./template` para dentro do projeto como `frontend/`. Não reescreva — o `main.py`
(o proxy) e o `static/index.html` (a UI de chat) já foram feitos para funcionar juntos.

## Passo 2 — Executar localmente

A partir da pasta `frontend/`:

```bash
pip install -r requirements.txt
export AGENT_ENGINE_RESOURCE_NAME="<cole do deployment_metadata.json>"
export AGENT_DIRECTORY="app"   # o seu agent_directory do agents-cli-manifest.yaml
python main.py     # -> http://localhost:8080
```

Envie uma mensagem e depois pergunte *"O que eu acabei de perguntar?"* para confirmar que a sessão funciona.

## Passo 3 — Fazer deploy no Cloud Run

O agente permanece no Agent Engine; apenas o frontend vai para o Cloud Run. A
service account dele roda sob uma identidade diferente da do seu usuário local, então ela precisa de
**`roles/aiplatform.user`** ou o `/chat` vai retornar erro 403:

```
Deploy the frontend to Cloud Run pointing at my AGENT_ENGINE_RESOURCE_NAME, and grant the Cloud Run service account roles/aiplatform.user.
```

## Quer mais do que um chat simples?

Faça o deploy do chat básico primeiro. Para adicionar controles depois (um painel de entrada, botões de
ação rápida, filtros), adicione-os dentro do `static/index.html` como um pequeno bloco autocontido
que monta uma mensagem e a envia pelo fluxo de chat existente. Dessa forma, a interface
cresce sem exigir um novo framework nem um passo de build adicional.

## E o A2UI (cards)?

A2UI é um recurso **do lado do agente** (consulte a skill **`enable-a2ui`**). Este frontend
**o renderiza**: via A2A, o agente devolve o A2UI dele como partes de dados marcadas como
`application/json+a2ui`, o proxy converte cada uma em uma parte `a2ui` e um pequeno renderizador
integrado no `static/index.html` as desenha como cards.

- Componentes suportados: `Card, Column, Row, Text` (com `usageHint`), `Divider`,
  `List`, `Image`, `Icon`. Qualquer outro componente **mostra um texto alternativo sem quebrar**, então
  uma resposta nunca fica em branco. (`Icon` usa a web font Material Symbols; se ela não
  conseguir carregar, o ícone mostra o nome dele como texto).
- `Image` é renderizada inline quando a url dela é um link `http(s)` público. Se o agente fizer upload de uma
  imagem gerada para um bucket público e colocar essa URL no `Image`, a imagem vai aparecer no chat.
  Um simples nome de arquivo de artefato local não tem uma URL acessível e vai aparecer como imagem quebrada.
- É **somente visualização**, igual ao `enable-a2ui`: botões/ações não estão conectados.
- Por você ter controle direto deste renderizador, ele é mais confiável do que o `adk web` (sem anomalias de
  streaming nem travamentos de tela em branco).
- Mantenha as saídas A2UI do agente pequenas e planas (seguindo a orientação do `enable-a2ui`) para que o
  renderizador tenha menos margem de erro.

## Se algo der errado

- **Erro 403 vindo do `/chat`:** falta o ADC localmente, ou a service account do Cloud Run não tem o papel
  `roles/aiplatform.user`. (Consulte a skill `troubleshoot-lab-setup`).
- **O agente esquece a conversa (falha no "O que eu acabei de perguntar?"):** o proxy precisa reutilizar um
  contexto A2A por usuário, o que o dicionário `_contexts` do template resolve mantendo
  o `task.contextId` entre turnos.
- **Nada é renderizado / erro de CORS:** o navegador está chamando o agente diretamente; ele deve chamar
  exclusivamente o proxy (mesma origem).
- **`operation_schemas()` vazio, ou o código antigo de `stream_query` não devolve nada:** trata-se de
  um deploy de Agent Runtime GA 1.1.0 (A2A, sem schema de reasoning-engine). Este template já se
  comunica via A2A, então use-o em vez do caminho antigo do SDK.
- **As respostas não chegam:** confirme primeiro que o agente responde via A2A com
  `agents-cli run --url <resource-url> --mode a2a "hi"`. A estrutura das partes de resposta do A2A
  pode variar conforme a versão do a2a-sdk; ajuste o `_extract_parts` em `main.py` se necessário.
- **O card A2UI aparece como texto puro:** o renderizador encontrou um componente não
  suportado (ou uma surface com erros) e recorreu ao texto de fallback — isso é um comportamento
  esperado, não uma falha crítica. Mantenha as surfaces do agente dentro do subconjunto suportado.
- **`(The agent didn't return a reply.)`:** o turno não gerou texto nem UI — geralmente o agente apenas
  executou tools ou uma tool parou no servidor (um problema do agente/deploy, não do
  frontend). Verifique os logs do agente.

## Referência

- Template: `./template` (`main.py`, `requirements.txt`, `static/index.html`)
- A2UI (lado do agente): a skill `enable-a2ui` · https://adk.dev/integrations/a2ui/
