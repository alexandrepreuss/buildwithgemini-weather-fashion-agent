---
name: record-demo
description: Grava um vídeo de demonstração com captura de tela (.webm) do agente da pessoa controlando a interface de chat dela com o Playwright — abre a página, digita consultas, espera as respostas e salva o vídeo. Funciona com as duas interfaces do lab: o frontend de chat personalizado em FastAPI (localhost:8080, o padrão) e o ADK Playground / dev UI (porta 8000, pelo nome do app). Também pode gerar música de fundo instrumental com o modelo Lyria do Google (lyria-002 no Vertex AI) e mixá-la com o vídeo, ajustada à duração dele — use quando a pessoa pedir para adicionar música de fundo/trilha sonora/clima à demo (por exemplo, "adicione uma música lo-fi relaxante"). Use quando a pessoa quiser gravar uma demo, capturar um vídeo/gravação de tela do agente dela, fazer um clipe de demonstração do app dela ou mostrar o agente em ação. Escolha os prompts de demonstração a partir do pedido da pessoa, se fornecidos; caso contrário, gere prompts inteligentes a partir do project_brief.md. Inclui o ./record-agent.js. Não é para tirar capturas de tela estáticas nem para construir a UI em si.
---

# Gravar uma demo do seu agente

Gera uma breve **gravação de tela em formato `.webm`** do agente do participante controlando a interface de chat dele em um navegador headless: o script abre a página, digita cada consulta, espera a resposta e salva o vídeo. Ele vem incluído como **`./record-agent.js`** e funciona com **qualquer uma** das interfaces do lab — o frontend personalizado em FastAPI (padrão) ou a dev UI do ADK — adaptando-se à interface que o participante tiver rodando. Cada gravação inclui uma moldura característica do **"Gemini World Tour"** (uma borda em degradê + etiqueta de título) sobreposta, pode ser acelerada para manter o clipe curto e — quando solicitado — pode musicar o vídeo com **música de fundo gerada por IA** (modelo Lyria do Google) sincronizada com a duração exata do vídeo.

> **A regra principal:** não reescreva o gravador. Invoque o `./record-agent.js` com as flags correspondentes de `--url`/`--app` e `--query`. Ele já cuida da configuração do Playwright, da abertura do navegador, da digitação interativa, da moldura de marca e do salvamento do vídeo.

## O que faz uma boa demo (valores recomendados)

Mantenha-a **curta e dinâmica** — um ótimo clipe dura cerca de **20 a 40 segundos**. Os valores padrão foram ajustados para isso; os parâmetros principais são quantos turnos você grava e quanto tempo leva cada resposta:

- **2 ou 3 turnos.** Suficiente para contar uma história, curto o bastante para se manter interessante. Não grave mais do que 3.
- **Escolha prompts que destaquem as melhores capacidades** (uma chamada de tool, uma busca no Firestore, uma imagem gerada, um card A2UI) em vez de uma conversa informal simples.
- **Ajuste o `--wait` ao turno mais lento.** Respostas de texto chegam em poucos segundos (o padrão `--wait 12000` é suficiente); **geração de imagens ou vídeo exige `--wait 30000` ou mais**, ou o vídeo vai cortar no meio da resposta.
- **Acelere para cortar tempos mortos.** Se um turno tiver uma espera longa, adicione **`--speed 1.5`** (ou `2`) para que o clipe final fique ágil. Isso exige o `ffmpeg`; se ele não estiver instalado, o script salva o vídeo em velocidade normal.
- A moldura decorativa, uma breve pausa inicial na UI vazia e uma retenção final na última resposta são automáticas — você não precisa configurá-las manualmente.

## Passo 1 — Definir o que mostrar (os prompts / queries)

Escolha de 2 a 3 prompts de demonstração, seguindo esta ordem de prioridade:

1. **Use o que a pessoa indicou.** Se o pedido dela especificar temas concretos a perguntar/mostrar (por exemplo, "grave ele respondendo o que tem em estoque e depois gerando uma imagem"), converta-os diretamente em argumentos `--query`, na ordem.
2. **Caso contrário, leia o `project_brief.md`** no projeto e crie de 2 a 3 prompts caprichados que valorizem o agente — idealmente aqueles que exercitam as melhores funcionalidades dele (chamadas de tools, buscas no Firestore, imagens geradas, cards A2UI). Prefira prompts que garantam uma resposta visualmente rica para *este* agente.
3. **Caso contrário** (sem pedido e sem brief), deixe o script usar os prompts padrão embutidos nele.

Mantenha os prompts curtos e concretos. Para dar sensação de continuidade, faça um prompt posterior construir sobre o anterior (por exemplo, pergunte sobre um item e depois peça para ver uma imagem dele).

## Passo 2 — Apontar para a UI correta

Escolha o destino conforme o que o participante tiver rodando:

- **Frontend personalizado (padrão, recomendado para uma demo caprichada):** escuta em `http://localhost:8080`. Basta omitir o `--url` (ou passar `--url http://localhost:8080`). Certifique-se de que ele foi iniciado (`python main.py` a partir de `frontend/`, ver a skill `build-agent-frontend`).
- **ADK Playground / dev UI:** passe `--app <nome>`, onde `<nome>` é o diretório `app` ou o nome do agente (do `agents-cli-manifest.yaml`). O script gera `http://127.0.0.1:8000/dev-ui/?app=<nome>`. Certifique-se de que o playground está rodando. Você também pode passar uma `--url` completa se a porta for diferente.

Em qualquer um dos casos, confirme primeiro que a UI está realmente ativa e acessível — o script termina com um erro claro se a página ou o campo de entrada do chat não forem encontrados.

## Passo 3 — Executar o gravador

A partir da raiz do projeto:

```bash
# Frontend personalizado (URL padrão), prompts adaptados a este agente:
node .agents/skills/record-demo/record-agent.js \
  -q "Primeiro prompt de demonstração" \
  -q "Segundo prompt de demonstração" \
  -o agent_demo.webm
```

```bash
# Dev UI do ADK em vez disso, pelo nome do app:
node .agents/skills/record-demo/record-agent.js \
  --app meu_agente \
  -q "Primeiro prompt de demonstração" \
  -q "Segundo prompt de demonstração"
```

```bash
# Uma demo com geração de imagens: espere mais tempo e acelere o clipe:
node .agents/skills/record-demo/record-agent.js \
  -q "O que tem no inventário?" \
  -q "Gere uma imagem do primeiro produto" \
  --wait 30000 --speed 1.5
```

Ao concluir com sucesso, ele imprime `SUCCESS: Recording saved to <path>`.

## Dependências (Playwright + Chromium, instalados uma única vez, de forma global)

O gravador precisa do pacote npm `playwright` e do navegador Chromium dele. Ambos foram pensados para serem instalados **uma única vez e globalmente**, para que nunca sejam gravados no repositório do participante nem baixados a cada execução:

```bash
npm install -g playwright        # o pacote (global)
npx playwright install chromium  # o navegador (cache compartilhado por usuário)
```

Na imagem do lab, esses componentes já devem estar **pré-instalados**. Se estiverem faltando, o script os instala para você na primeira vez (pacote global + cache de navegador compartilhado) — essa primeira execução leva cerca de um minuto; as seguintes são instantâneas. O script resolve o pacote global via `npm root -g`, então funciona sem uma pasta `node_modules` local. (Se a instalação global não for permitida, ele recorre a uma local). O `ffmpeg` é necessário para `--speed` e `--music`; fora isso, é opcional. O `--music` exige adicionalmente uma sessão **autenticada no gcloud** (que o lab já tem) — consulte a seção de música abaixo.

## Referência de opções

| Flag | Significado | Valor padrão |
| --- | --- | --- |
| `-q, --query <texto>` | Mensagem a enviar; repita para múltiplos turnos | dois prompts neutros por padrão |
| `-u, --url <url>` | URL completa da UI de chat | `http://localhost:8080/` |
| `-a, --app <nome>` | Nome do app na dev UI do ADK (monta a URL da dev-ui quando `--url` não é informado) | — |
| `-o, --output <arquivo>` | Caminho do arquivo `.webm` resultante | `./<app>_demo.webm` ou `./agent_demo.webm` |
| `--delay <ms>` | Atraso de digitação por tecla em milissegundos | `40` |
| `--wait <ms>` | Tempo de espera por resposta (suba para 30000+ para geração de mídia) | `12000` |
| `--speed <fator>` | Acelerar o vídeo final (exige `ffmpeg`; ignorado se estiver ausente) | `1.0` |
| `--music <prompt>` | Gerar e mixar música de fundo com o Lyria (exige `ffmpeg` + gcloud) | desativado |
| `--music-negative <texto>` | Prompt negativo para o Lyria (elementos a excluir) | — |
| `--music-volume <0..1>` | Nível de mixagem da música | `0.6` |
| `--title <texto>` | Texto do título na moldura | `Gemini World Tour` |
| `--no-frame` | Desativar a moldura de marca | moldura ativada |
| `--headed` | Mostrar a janela gráfica do navegador | headless (oculto) |

Execute `node .agents/skills/record-demo/record-agent.js --help` para ver a mesma lista.

## Música de fundo (Lyria) — apenas quando a pessoa pedir

A música é **opcional**. Adicione-a somente quando o pedido da pessoa justificar — por exemplo: "adicione uma música lo-fi relaxante de fundo", "coloque uma trilha sonora", "dê um clima animado". Quando isso acontecer, traduza o desejo dela em um **prompt para o Lyria** e passe `--music`:

```bash
node .agents/skills/record-demo/record-agent.js \
  -q "O que tem no inventário?" \
  -q "Gere uma imagem do primeiro produto" \
  --wait 30000 --speed 1.5 \
  --music "lo-fi chill hip-hop, mellow Rhodes piano, soft vinyl crackle, relaxed downtempo beat"
```

Como funciona: o script gera uma faixa instrumental com o modelo **`lyria-002`** do Google no Vertex AI e depois a mixa por baixo do vídeo finalizado usando o ffmpeg. O áudio é **ajustado à duração do vídeo** — ele é cortado (ou reproduzido em loop, já que os clipes do Lyria duram ~30s) até a duração exata e recebe um fade-in de 1s e um fade-out de 2s que termina no último quadro, garantindo que a música comece e termine junto com o vídeo. A música é aplicada **depois** do `--speed`, então ela sempre corresponde à duração acelerada final.

Como escrever um bom prompt para o Lyria (converta o clima desejado pela pessoa nisto):
- **Somente instrumental** — o Lyria não gera vocais. Descreva gênero, clima, instrumentos e andamento. Exemplo: "upbeat corporate synth-pop, bright plucks, driving four-on-the-floor beat, optimistic" ou "ambient cinematic pad, warm strings, slow and hopeful".
- Alinhe o clima à demo (calma/produtividade → lo-fi ou ambiente; lançamento de produto empolgante → eletrônica animada).
- Use `--music-negative` para excluir elementos ("vocals, harsh distortion") e `--music-volume` para deixá-la mais sutil (ex. `0.4`) ou mais presente (`0.8`).

Requisitos: `ffmpeg` e uma sessão **autenticada no gcloud** com um projeto configurado — o ambiente do lab já tem os dois (`gcloud auth login` / ADC e projeto). O `lyria-002` roda em `us-central1`; o script aponta para essa região automaticamente e obtém o projeto de `GOOGLE_CLOUD_PROJECT` ou do `gcloud config`. Se a geração de música falhar por qualquer motivo, o script **ainda assim salva o vídeo** (sem música) e imprime a causa.

## A moldura decorativa (branded frame)

O gravador injeta uma moldura do **"Gemini World Tour"** na página antes de gravar: uma borda em degradê ao redor do viewport e uma etiqueta de título no topo. Ela é desenhada como uma camada com `pointer-events: none`, então nunca bloqueia a interface do agente, e é reaplicada se a aplicação for renderizada novamente. Os estilos ficam em `./assets/overlay.css` e o logotipo em `./assets/logo.svg` — edite-os para mudar o design. Altere o texto com `--title "…"` ou remova a moldura completamente com `--no-frame`.

## Ajuste de resultados

- **As respostas são cortadas / o vídeo termina no meio da resposta:** aumente o `--wait` (a geração de imagens ou vídeo pode demorar muito mais que a de texto — teste com `--wait 30000` ou mais).
- **O clipe parece lento ou longo demais:** adicione `--speed 1.5` (ou `2`) para reduzir tempos mortos e/ou grave menos turnos. Mire em um total de ~20 a 40 segundos.
- **A música está muito alta ou muito baixa:** ajuste o `--music-volume` (ex. `0.4` mais suave, `0.8` mais alto). Mude o clima reformulando o prompt do `--music`.
- **A digitação parece muito rápida ou muito lenta:** ajuste o `--delay`.
- **Nada é encontrado / não consegue conectar à UI:** o frontend ou o playground não estão rodando, ou estão em uma porta diferente — inicie-os ou informe a `--url` correta.
- **Acompanhar o processo ao vivo:** adicione `--headed` para ver o navegador interagindo com a interface em tempo real.

## Solução de problemas

- **"Could not load <url>":** a interface não está rodando ou a porta está errada. Inicie o frontend (`python main.py`) ou o playground, ou corrija `--url`/`--app`.
- **"Could not find a chat input":** a página carregou mas não é a UI de chat (URL errada), ou o campo de entrada dela é diferente dos suportados (`#input`, o textarea da dev UI ou um input genérico / contenteditable). Aponte para a página correta.
- **Falha na instalação do Playwright/Chromium:** o script instala ambos automaticamente (globalmente); se o ambiente bloquear isso, instale manualmente com `npm install -g playwright && npx playwright install chromium` e execute novamente.
- **`--speed` não teve efeito:** o `ffmpeg` não está instalado, então o vídeo foi salvo em velocidade normal. Instale o ffmpeg e execute de novo, ou mantenha como está.
- **A moldura não aparece no vídeo:** os arquivos de `./assets` estão faltando ou você passou `--no-frame`. A gravação continua funcionando — apenas sem a moldura decorativa.
- **A música não foi adicionada:** o script imprime o motivo e salva o vídeo mesmo assim. Causas comuns: falta o `ffmpeg`; o gcloud não está autenticado ou não há projeto configurado (`gcloud auth login` + `gcloud config set project …`); ou a conta não tem acesso ao `lyria-002` (Vertex AI / Agent Platform). Um erro `403`/`401` da API do Lyria indica problemas de autenticação ou permissões.

## Referência

- Script de gravação: `./record-agent.js`
- Recursos da moldura: `./assets/overlay.css`, `./assets/logo.svg`
- Modelo de música: Lyria `lyria-002` no Vertex AI (`us-central1`), instrumental, clipes de ~30s
- Frontend para o qual ele aponta por padrão: a skill `build-agent-frontend` (`localhost:8080`)
