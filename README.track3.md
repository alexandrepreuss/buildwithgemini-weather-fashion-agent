<div align="center">

<img src="assets/build-with-gemini-banner.png" alt="Build with Gemini" width="100%" />

# 🚀 Build with Gemini · Track 3

### O kit inicial do Track 3 do Build with Gemini World Tour, e uma amostra do que os participantes construíram com ele.

Clone este repositório, abra o [Antigravity](https://antigravity.google) e crie seu próprio app agent-first no Google Cloud. Cada projeto na [galeria abaixo](#-projetos-em-destaque) foi construído da mesma forma: prototipado com Antigravity e `agents-cli`, equipado com Memory, tools, storage e RAG, implantado na Agent Platform e com uma interface web no Cloud Run.

<br/>

![Build with Gemini](https://img.shields.io/badge/Build%20with%20Gemini-World%20Tour-4285F4?logo=google&logoColor=white)
![Track 3](https://img.shields.io/badge/Track%203-Agent--First%20Apps-EA4335)
![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Agent%20Platform-4285F4?logo=googlecloud&logoColor=white)
![Built with ADK](https://img.shields.io/badge/Built%20with-ADK%20%2B%20agents--cli-34A853)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)
![Projects](https://img.shields.io/badge/Projects-0-blue)

<sub>️ <a href="https://google.github.io/agents-cli/guide/getting-started/">agents-cli</a> · 🤖 <a href="https://google.github.io/adk-docs/">ADK</a></sub>

<br/>

**🌎 Idioma:** 🇧🇷 Português · [🇪🇸 Español](../../es/track-3/README.md) · [⬅️ Início](../../README.md)

</div>

---

## 📚 Índice

- [🧩 Anatomia de um projeto do Track 3](#-anatomia-de-um-projeto-do-track-3)
- [🏷️ Legenda de capacidades](#️-legenda-de-capacidades)
- [📂 Projetos em destaque](#-projetos-em-destaque)
  - [🛍️ Agentes de comércio e marketplace](#️-agentes-de-comércio-e-marketplace)
  - [🍳 Agentes de comida e receitas](#-agentes-de-comida-e-receitas)
  - [✈️ Agentes de viagem e locais](#️-agentes-de-viagem-e-locais)
  - [💪 Agentes de saúde, fitness e bem-estar](#-agentes-de-saúde-fitness-e-bem-estar)
  - [📚 Agentes de aprendizado e conhecimento](#-agentes-de-aprendizado-e-conhecimento)
  - [🎨 Agentes criativos e de mídia](#-agentes-criativos-e-de-mídia)
  - [🏢 Agentes de produtividade e corporativos](#-agentes-de-produtividade-e-corporativos)
  - [🧪 Experimentais e outros](#-experimentais-e-outros)
- [🧠 O que tem neste repositório](#-o-que-tem-neste-repositório)
- [🧰 Construa o seu](#-construa-o-seu)
- [📚 Recursos](#-recursos)
- [🤝 Contribuir](#-contribuir)
- [📄 Licença](#-licença)

---

## 🧩 Anatomia de um projeto do Track 3

Cada aplicação desta coleção é construída a partir do mesmo conjunto de blocos do Google Cloud apresentados no lab. Depois que você entender essa estrutura, conseguirá interpretar qualquer projeto daqui num piscar de olhos:

| Camada | O que faz | Powered by |
|---|---|---|
| 🤖 **O Agente** | O loop central de raciocínio | [ADK](https://google.github.io/adk-docs/) + [`agents-cli`](https://google.github.io/agents-cli/guide/getting-started/), estruturado com [Antigravity](https://antigravity.google) |
| 🧠 **Memory** | Lembra informações entre sessões | [Agent Platform Memory Bank](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank) |
| 🗄️ **Dados estruturados** | Inventário, registros, listas | [Firestore](https://console.cloud.google.com/firestore) |
| 🖼️ **Arquivos e blobs** | Imagens, conteúdo multimídia, recursos | [Cloud Storage](https://console.cloud.google.com/storage) |
| 🔧 **Tools** | Executam ações reais e buscam dados reais | ADK function tools |
| 📖 **RAG** | Respostas fundamentadas nos seus documentos | [Vertex AI RAG Engine](https://console.cloud.google.com/agent-platform/rag) |
| 🎨 **Geração de mídia** | Cria imagens (e vídeo) sob demanda | `gemini-3.1-flash-lite-image` (Nano Banana 2 Lite) · Omni (vídeo) |
| 🧪 **Code sandbox** | Executa código gerado com segurança | Execução de código na Agent Platform |
| 🪟 **UI agent-first** | Cards e tabelas em vez de texto puro | [A2UI](https://adk.dev/integrations/a2ui/) |
| 🌐 **Frontend** | Uma interface web para compartilhar | Proxy FastAPI no [Cloud Run](https://cloud.google.com/run) |

---

## 🏷️ Legenda de capacidades

Cada projeto abaixo é marcado com os blocos de construção que utiliza, para que você encontre exatamente o padrão que quer aprender:

`🧠 Memory` · `🗄️ Firestore` · `🖼️ Storage` · `🔧 Tools` · `📖 RAG` · `🎨 Image Gen` · `🎬 Video` · `🧪 Sandbox` · `🪟 A2UI` · `🌐 Cloud Run`

---

## 📂 Projetos em destaque

Uma amostra do que os participantes do workshop construíram com este lab. As entradas são adicionadas aqui a partir do formulário de envio para swag e galeria após cada evento, por isso as categorias abaixo começam vazias e vão sendo preenchidas com o tempo. Explore-as em busca de inspiração, ou [envie o seu](#-contribuir) assim que publicar seu projeto com a skill `publish-to-github`.

<!--
Adicione uma entrada por projeto, neste formato:
- 🌿 **[Nome do Projeto](https://github.com/seu-usuario/seu-repo)**: descrição de uma linha do que ele faz. <br/> <sub>`🗄️ Firestore` · `🎨 Image Gen` · `🪟 A2UI`, por [@usuario](https://github.com/usuario)</sub>

Escolha as tags da Legenda de capacidades acima. Incremente o contador do badge "Projects" no topo ao adicionar um projeto.
-->

### 🛍️ Agentes de comércio e marketplace

### 🍳 Agentes de comida e receitas

### ✈️ Agentes de viagem e locais

### 💪 Agentes de saúde, fitness e bem-estar

### 📚 Agentes de aprendizado e conhecimento

### 🎨 Agentes criativos e de mídia

### 🏢 Agentes de produtividade e corporativos

### 🧪 Experimentais e outros

---

## 🧠 O que tem neste repositório

A pasta `.agents/` ensina ao Antigravity como construir agentes no Google Cloud.

### Skills

Uma **skill** é um conjunto de instruções carregado automaticamente quando é relevante, permitindo que o agente execute o fluxo de trabalho corretamente em menos passos, em vez de ter que redescobri-lo a cada vez.

| Skill | O que faz |
| --- | --- |
| [`pick-your-agent-project`](.agents/skills/pick-your-agent-project/SKILL.md) | Faça um brainstorming da sua aplicação e escreva um brief do projeto |
| [`troubleshoot-lab-setup`](.agents/skills/troubleshoot-lab-setup/SKILL.md) | Verifique seu ambiente e resolva erros comuns de configuração |
| [`memory-bank-setup`](.agents/skills/setup-memory-bank/SKILL.md) | Adicione memória entre sessões ao seu agente com o Vertex AI Memory Bank |
| [`rag-engine-setup`](.agents/skills/build-rag/SKILL.md) | Fundamente seu agente em documentos com um corpus serverless do Vertex AI RAG Engine |
| [`enable-a2ui`](.agents/skills/enable-a2ui/SKILL.md) | Faça seu agente responder com cards visuais ricos (A2UI) na UI de desenvolvimento do ADK |
| [`build-agent-frontend`](.agents/skills/build-agent-frontend/SKILL.md) | Gere um frontend de chat com FastAPI e faça o deploy no Cloud Run |
| [`record-demo`](.agents/skills/record-demo/SKILL.md) | Grave um vídeo de demonstração com a identidade visual do seu agente, com trilha sonora opcional gerada por IA |
| [`publish-to-github`](.agents/skills/publish-to-github/SKILL.md) | Publique seu projeto finalizado no seu próprio GitHub e envie-o para ganhar swag |

### Tools pré-configuradas (MCP)

O [`.agents/mcp_config.json`](.agents/mcp_config.json) conecta dois servidores [Model Context Protocol](https://modelcontextprotocol.io/) que se autenticam com suas credenciais do gcloud, para que o agente possa consultar informações em vez de adivinhar:

- **Firebase**: trabalhe diretamente com o Firestore e outros serviços do Firebase
- **Google Developer Knowledge**: acesso fundamentado à documentação oficial do Google (Cloud, Firebase, ADK, Agent Platform)

### Estrutura

```text
.agents/
├── mcp_config.json    # Servidores MCP do Firebase + Developer Knowledge
└── skills/            # as skills do workshop listadas acima
```

---

## 🧰 Construa o seu

**Pré-requisitos** (a estação de trabalho do lab já vem com tudo isso pré-instalado; você vai precisar deles se estiver rodando na sua própria máquina):

- Um **projeto do Google Cloud** com faturamento habilitado
- **[Antigravity](https://antigravity.google)** (`agy`), o agente de programação que carrega as skills mencionadas acima
- **[agents-cli](https://google.github.io/agents-cli/guide/getting-started/)**, construído sobre o [Agent Development Kit (ADK)](https://google.github.io/adk-docs/)
- gcloud autenticado: `gcloud auth login` e `gcloud auth application-default login`
- Uma **conta pessoal do GitHub** para o passo final de publicação e envio

**Início rápido:**

```bash
git clone https://github.com/miohana/build-with-gemini
cd build-with-gemini/pt-br/track-3
agy
```

Ao iniciar, o Antigravity escaneia a pasta `.agents/` e carrega automaticamente as skills e tools acima. No prompt do AGY:

```text
/skills            # ver as skills instaladas
/mcp               # confirmar que as tools do firebase + google-developer-knowledge estão conectadas
```

```text
Verifique meu setup.   # executa a skill troubleshoot-lab-setup para validar seu ambiente
```

---

## 📚 Recursos

- [Antigravity](https://antigravity.google)
- [agents-cli](https://google.github.io/agents-cli/guide/getting-started/)
- [Agent Development Kit (ADK)](https://google.github.io/adk-docs/)
- [Gemini Enterprise Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform)

---

## 🤝 Contribuir

**Construiu alguma coisa?** Publique com a skill `publish-to-github` e envie pelo formulário que ela te fornece. Com seus envios você pode ganhar swag, e os projetos em destaque serão adicionados à galeria de [Projetos em destaque](#-projetos-em-destaque) acima.

**Encontrou um bug?** Se você encontrar algum problema em uma skill ou no lab, por favor [abra uma issue](https://github.com/miohana/build-with-gemini/issues).

---

## 📄 Licença

Este não é um produto com suporte oficial do Google e é fornecido exclusivamente para fins de demonstração no workshop Build with Gemini.
