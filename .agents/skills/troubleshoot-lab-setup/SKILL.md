---
name: troubleshoot-lab-setup
description: >-
  Verifica se o ambiente do lab do Gemini World está configurado corretamente e diagnostica ou resolve erros comuns. Use no INÍCIO do lab, logo depois do login, para confirmar que está tudo pronto ("verifique meu setup", "estou pronto para começar?", "checa meu ambiente", "fiz login corretamente?"), E SEMPRE que a pessoa encontrar um erro e não souber o motivo — permissão negada / 403 / PERMISSION_DENIED, "API not enabled", um deploy que falha, o frontend não consegue se comunicar com o agente, erros em /chat, falhas no code sandbox, falhas na geração de imagens, ou uma mensagem vaga como "não está funcionando". Revisa as causas mais comuns — ter feito login no Antigravity com a conta correta (fluxo de GCP/lab, não a conta pessoal do Google), se o projeto do GCP está configurado, se foram executados tanto o gcloud auth login quanto o application-default login, se a API está habilitada e se a identidade tem roles/aiplatform.user. Não use para programar funcionalidades do agente nem para dúvidas de desenvolvimento que não envolvam erros.
---

# Solução de problemas de configuração do lab

Quase todas as falhas neste lab vêm de um punhado de problemas de ambiente — não do código da pessoa. Esta skill tem **dois modos**:

- **Preflight (verificação prévia)** — roda no *início* do lab, logo depois do login, para confirmar que está tudo pronto antes de começar a construir. Detecta problemas cedo, em vez de no meio do módulo.
- **Error triage (diagnóstico de erros)** — roda quando a pessoa esbarra em um erro. Execute primeiro as verificações abaixo, corrija o que estiver errado e depois vá até o sintoma correspondente.

É melhor *verificar* o estado com um comando de leitura antes de *modificar* qualquer coisa, e informar à pessoa o que você encontrou.

## Preflight: verificação de estado no início do lab

Quando a pessoa pedir para verificar o setup dela (ou quando você estiver iniciando o lab), execute as **verificações 0 a 5 abaixo, em ordem**, e mostre um resumo claro de aprovado/reprovado, por exemplo:

```
Setup check:
✅ Antigravity signed in as <lab account>
✅ Project set to <qwiklabs project id>
✅ gcloud auth + ADC present
✅ Vertex AI / aiplatform API enabled
✅ roles/aiplatform.user granted
✅ agents-cli skills loaded in AGY
You're ready to start. ✅
```

Corrija qualquer item que falhar e execute aquela verificação de novo antes de continuar. Pule os sintomas de deploy/frontend/sandbox durante o preflight — esses aparecem mais adiante.

## As verificações (execute em praticamente QUALQUER erro e no preflight)

Estas são as causas mais comuns. Revise todas antes de se aprofundar.

**0. A pessoa fez login no Antigravity com a conta CERTA?** Uma pegadinha muito comum: fazer login no Antigravity com uma conta pessoal do **Google** (por exemplo, uma conta `@gmail.com` ou `@google.com`) em vez das credenciais do **lab do GCP / Qwiklabs**. Tudo *parece* estar bem, mas as chamadas ao projeto falham com erros de permissão porque o AGY está agindo sob a identidade errada.

- Pergunte à pessoa qual conta ela usou para entrar no Antigravity e confirme que é a **conta do lab do Qwiklabs**, não a conta pessoal do Google dela.
- Verifique se a conta ativa do gcloud é a mesma do lab:
  ```bash
  gcloud auth list        # a conta ATIVA (*) deve ser a conta do lab
  ```
- Se o AGY estiver logado com a conta errada, oriente a pessoa a sair do Antigravity e entrar novamente pelo fluxo de login de GCP/lab (conforme as instruções de configuração do lab), e depois execute o preflight novamente.

**1. O projeto correto está configurado?** O Cloud Shell / AGY podem silenciosamente adotar um projeto errado por padrão (por exemplo, `cloudshell-gca`), o que faz os comandos de habilitação ou deploy falharem.

```bash
gcloud config get-value project          # qual está ativo agora?
echo "$GOOGLE_CLOUD_PROJECT"             # o que o ambiente acha que é
```

Um ID de projeto do Qwiklabs configurado corretamente **contém a string `qwiklabs`** (por exemplo, `qwiklabs-gcp-01-abc123def456`). Se o projeto ativo não contém `qwiklabs`, é quase certo que seja o projeto errado — trate isso como um sinal de alerta.

Se algum estiver incorreto, vazio ou não contiver `qwiklabs`, **peça à pessoa o ID do projeto do Qwiklabs** (do painel do lab) e fixe-o executando:

```bash
export GOOGLE_CLOUD_PROJECT=<o project id do qwiklabs>
gcloud config set project "$GOOGLE_CLOUD_PROJECT"
```

Confirme também que o projeto está fixado dentro da configuração do AGY, para que ele não mude no meio da execução. Durante o preflight, sempre fixe o projeto dessa forma — não presuma que ele já está configurado.

**2. A pessoa está autenticada?** São necessários dois logins independentes — a falta do login de Application Default Credentials (ADC) é a principal causa de erros 403 vindos do código.

```bash
gcloud auth list                          # existe uma conta ativa?
```

Se não estiver autenticada, execute AMBOS:

```bash
gcloud auth login
gcloud auth application-default login
```

**3. A API necessária está habilitada?** Operações de deploy, sandbox e chamadas a modelos exigem que a API do Agent Platform / Vertex AI esteja ativada. Erros de "API not enabled" costumam vir disso ou de um projeto errado (ver #1).

```bash
gcloud services list --enabled | grep -i aiplatform
gcloud services enable aiplatform.googleapis.com   # habilitar se estiver faltando
```

**4. A identidade tem o papel de IAM correto?** Muitas funcionalidades exigem `roles/aiplatform.user`. Se uma chamada retornar `PERMISSION_DENIED`, verifique o papel na identidade que está fazendo a chamada (seu usuário, a service account do agente ou a service account do Cloud Run).

```bash
gcloud projects add-iam-policy-binding "$GOOGLE_CLOUD_PROJECT" \
  --member="user:<voce@exemplo.com>" \
  --role="roles/aiplatform.user"
```

Ajuste o papel ao que a identidade que chama realmente *faz*. Um **agente implantado** roda com a própria service account **sem acesso a Firestore nem a Cloud Storage por padrão**, então qualquer agente que leia o Firestore precisa ter `roles/datastore.user` concedido a essa service account — **conceda no momento do deploy** (ver "Depois do deploy" abaixo), não apenas `aiplatform.user` para o seu usuário.

**5. As skills do agents-cli estão carregadas no AGY?** Os passos de scaffolding, deploy, evaluation e Memory Bank do lab dependem de as skills `google-agents-cli-*` estarem registradas no Antigravity. Elas são **independentes** das skills do workshop incluídas no repositório em `.agents/skills/` — são instaladas pelo passo `agents-cli setup`, não automaticamente.

- No AGY, execute `/skills` e confirme que você vê as skills de ciclo de vida `google-agents-cli-*` (por exemplo, scaffold, deploy, adk-code) **além das** skills do workshop. Se aparecerem apenas as skills do workshop, as skills do agents-cli não estão carregadas.
- Se estiverem faltando, instale a partir do Cloud Shell:
  ```bash
  agents-cli setup --skip-auth
  ```
- Depois **reinicie o Antigravity** para que ele reconheça as novas skills instaladas (ver "Antigravity / MCP se comportando de forma estranha logo após a instalação" abaixo), e execute `/skills` novamente para confirmar que agora elas aparecem.

> Dica: se você tiver o **Developer Knowledge MCP** instalado, use-o para confirmar o nome exato da API, o papel e o comando de um produto em vez de adivinhar.

## Sintoma → Solução

### 403 / PERMISSION_DENIED / "permission denied"
Quase sempre é um destes motivos: ter feito login no Antigravity com a conta errada (pessoal) em vez da conta do lab (verificação #0), falta de ADC (verificação #2), falta do papel `roles/aiplatform.user` na identidade que faz a chamada (verificação #4), ou o projeto errado (verificação #1). Descarte nessa ordem.

### "API not enabled" / "SERVICE_DISABLED"
Ou você está no projeto errado (#1) ou a API está desativada (#3). Corrija o projeto primeiro e depois habilite a API.

### `adk web`/`adk run` falha ao iniciar / `cannot import name '<x>' from 'google.cloud'` / ModuleNotFound
Você executou um comando **`adk` direto**, que resolve para um Python *global* sem as dependências do seu projeto instaladas. Execute pelo `.venv` do projeto com **`uv run`**:

```bash
uv run adk web --port 8080 --allow_origins "*" --reload_agents
```

Sintomas reveladores: `cannot import name 'firestore' from 'google.cloud'`, ou um `ModuleNotFoundError` para um pacote que você *sabe* que está instalado (por exemplo, `a2ui-agent-sdk`). O comando `adk` direto usa um interpretador diferente; `uv run adk` usa o venv do projeto, onde estão as dependências reais.

### `agents-cli deploy` falha
1. O projeto está fixado? (#1) — esta é a causa mais comum.
2. As APIs estão habilitadas e autenticadas? (#2, #3)
3. Releia o erro exato; se ele mencionar uma permissão, vá para #4.
Liste os deploys existentes para ver o estado atual: `agents-cli deploy --list`.

### Depois do deploy: conceda à service account do agente os papéis de que as tools dele precisam
Faça isso como parte de **todo** deploy em que o agente leia Firestore ou Cloud Storage — de forma proativa, sem esperar que falhe. O agente implantado roda com a própria service account (por padrão a service agent do Reasoning Engine, `service-PROJECT_NUMBER@gcp-sa-aiplatform-re.iam.gserviceaccount.com`), que **não tem papéis de acesso a dados por padrão**. Para um agente com Firestore, conceda `roles/datastore.user` (este comando preenche automaticamente o número do seu projeto):

```bash
gcloud projects add-iam-policy-binding "$GOOGLE_CLOUD_PROJECT" \
  --member="serviceAccount:service-$(gcloud projects describe "$GOOGLE_CLOUD_PROJECT" --format='value(projectNumber)')@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \
  --role="roles/datastore.user"
```

Para um agente que grava arquivos no Cloud Storage (por exemplo, um que faz upload de imagens geradas), conceda à service account dele permissão de escrita no bucket. Limite o escopo da permissão ao bucket, não ao projeto inteiro:

```bash
gcloud storage buckets add-iam-policy-binding "gs://<seu-bucket-de-imagens>" \
  --member="serviceAccount:service-$(gcloud projects describe "$GOOGLE_CLOUD_PROJECT" --format='value(projectNumber)')@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"
```

Uma tool de Cloud Storage somente leitura precisa apenas de `roles/storage.objectViewer`.
Garanta também que você carregou os dados iniciais (seed) no mesmo projeto onde fez o deploy; caso contrário, o agente implantado vai ler um banco vazio.

### O frontend não consegue se comunicar com o agente / sem resposta / erros ao enviar
Execute todos os comandos do frontend a partir da pasta `frontend/`.
1. As dependências estão instaladas? `pip install -r requirements.txt`
2. A `AGENT_ENGINE_RESOURCE_NAME` está configurada e correta? Ela deve ser o nome do recurso vindo do `deployment_metadata.json` (escrito no passo de deploy). Configure também `AGENT_DIRECTORY` com o seu `agent_directory` do `agents-cli-manifest.yaml` (geralmente `app`), já que o caminho do endpoint A2A o inclui:
   ```bash
   echo "$AGENT_ENGINE_RESOURCE_NAME"
   export AGENT_ENGINE_RESOURCE_NAME="<cole do deployment_metadata.json>"
   export AGENT_DIRECTORY="app"
   ```
3. O ADC está presente localmente? (#2)
4. Teste de coerência: envie uma mensagem e depois pergunte "O que eu acabei de perguntar?" — se ele não conseguir lembrar, é a conexão com o agente implantado que está falhando, não a interface.
5. Se respostas em texto puro funcionam mas **respostas baseadas em tools não retornam nada**, não é problema da UI — veja "O agente implantado não responde" abaixo.

### Erros do frontend: `operation_schemas()` vazio, `no attribute 'stream_query'`, ou erros 500 do proxy antigo
Esta é a mudança do **agents-cli 1.1.0 (GA)**. O GA implanta agentes ADK no Agent Runtime como agentes A2A e não registra mais o schema de operações do reasoning-engine, então um frontend construído sobre `agent_engines.get(...).stream_query()` falha: `operation_schemas()` fica vazio e o handler não tem `stream_query`/`create_session`. Confirme primeiro que o agente funciona corretamente sobre A2A:
```bash
agents-cli run --url https://<LOCATION>-aiplatform.googleapis.com/v1/<RESOURCE> --mode a2a "hi"
```
Se ele responder, o agente está ok e o proxy está usando o caminho obsoleto do SDK. Use o template atual de `build-agent-frontend`, que se comunica via A2A (busca o agent card e envia mensagens com o cliente do a2a-sdk). Não tente forçar um deploy de ADK/`stream_query`. Todos os templates do ADK 1.1.0 são marcados para A2A, e o contêiner serve A2A independentemente de `is_a2a` ser verdadeiro ou falso.

### O agente implantado não responde / uma tool funciona no Playground mas não no deploy
Uma tool baseada em Firestore funciona no Playground (com o seu ADC local), mas o turno do agente implantado termina sem resposta. É quase certo que seja um destes pontos:

1. **Você esqueceu de conceder o papel.** Execute o passo "Depois do deploy" acima — a service account implantada precisa de `roles/datastore.user`.
2. **Você carregou os dados (seed) e fez o deploy em projetos diferentes.** O agente implantado lê o Firestore do *próprio* projeto; se você carregou os dados em outro lugar, ele vai ver um banco vazio. Compare e recarregue os dados no projeto de deploy se forem diferentes:
   ```bash
   gcloud config get-value project          # onde você carregou os dados
   echo "$AGENT_ENGINE_RESOURCE_NAME"        # o projeto em que o agente roda
   ```

Confirme que o banco do Firestore existe e contém dados no projeto de deploy (console do Firebase), e teste novamente. Se travar em silêncio = projeto errado/vazio; `PERMISSION_DENIED` = falta de papel.

### `NotFound: The database (default) does not exist` (agente Firestore implantado)
Seu código está construindo o cliente do Firestore a partir do **número** do projeto, não do ID. No Agent Engine, **tanto `google.auth.default()` quanto a variável de ambiente `GOOGLE_CLOUD_PROJECT` retornam o *número* do projeto** — mas o Firestore só resolve o banco `(default)` pelo **ID** do projeto. Por isso, este padrão comum gera um erro 404 no agente implantado mesmo funcionando localmente:

```python
# ERRADO no Agent Engine: GOOGLE_CLOUD_PROJECT é o NÚMERO do projeto lá
db = firestore.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT"))
```

Defina explicitamente o **ID** do projeto — nunca derive o projeto do Firestore de `google.auth.default()` ou de `GOOGLE_CLOUD_PROJECT`:

```python
FIRESTORE_PROJECT = "<seu-project-id>"           # o ID, NÃO o número
db = firestore.Client(project=FIRESTORE_PROJECT)
```

Use o mesmo ID no seu script de carga de dados (seed) e depois **faça o deploy novamente**. (Funciona localmente apenas porque o seu `GOOGLE_CLOUD_PROJECT`/ADC local já é o ID; o ambiente de execução implantado o define como o número).

### Erros em `/chat` depois de implantar o frontend no Cloud Run
O serviço do Cloud Run roda como uma **identidade diferente** da do seu usuário local, então a service account dele precisa de `roles/aiplatform.user`. Conceda isso à service account do Cloud Run (não à sua conta de usuário) e tente novamente.

### Falha no code sandbox / execução de código
1. A API do Agent Platform precisa estar habilitada (#3) e a identidade precisa ter `roles/aiplatform.user` (#4).
2. Existe mesmo um sandbox? Se não, crie um a partir do recurso de agent engine antes de executar código.

### Falha na geração de imagens ou a imagem não aparece
Se a tool lançar um erro durante a geração, geralmente é um problema de API/permissões (#3, #4) ou uma incompatibilidade de região/acesso ao modelo. Confirme que o modelo e a região estão disponíveis para o projeto e que a API está habilitada.

Se a imagem aparece no Playground mas não no agente implantado, ou se um card ou o frontend mostram uma imagem quebrada, lembre-se de que o agente faz upload das imagens geradas para um bucket público e exibe a URL pública. Duas condições precisam ser atendidas:

1. A service account implantada precisa conseguir gravar no bucket (`roles/storage.objectAdmin`, ver "Depois do deploy" acima). Funciona localmente porque você roda como você mesmo, mas o agente implantado roda sob a própria conta.
2. O bucket precisa servir objetos publicamente. Conceda a `allUsers` o papel `roles/storage.objectViewer` no bucket. Se essa concessão falhar com `public access prevention is enforced`, a organização do projeto bloqueia buckets públicos e a abordagem de URL pública não vai funcionar ali.

### Antigravity / MCP se comportando de forma estranha logo após a instalação
Se você acabou de instalar o agents-cli ou o Developer Knowledge MCP, **reinicie o Antigravity** para que ele carregue as novas skills/MCP e tente novamente.

## Regras gerais
- Confirme primeiro a **conta do Antigravity** — fazer login com uma conta pessoal do Google em vez do fluxo de lab/GCP quebra silenciosamente o acesso ao projeto.
- Corrija o **projeto** em seguida — um projeto errado provoca metade dos outros erros.
- Existem **dois** logins de autenticação (`login` e `application-default login`); pular o segundo quebra as chamadas feitas pelo código enquanto a CLI continua parecendo funcional.
- Atribua o papel de IAM à **identidade que realmente faz a chamada** — seu usuário localmente, mas a service account no Cloud Run.
- Na dúvida sobre um comando, papel ou nome exato de API, consulte o Developer Knowledge MCP em vez de adivinhar.
