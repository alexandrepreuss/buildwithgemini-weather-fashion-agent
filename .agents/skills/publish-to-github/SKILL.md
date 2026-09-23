---
name: publish-to-github
description: >-
  Publica o projeto finalizado do participante no GitHub pessoal DELE e entrega um formulário pré-preenchido para resgatar swag e participar da galeria. Use no fim do lab quando a pessoa quiser "publicar meu projeto no GitHub", "subir meu código para o GitHub", "fazer upload do meu agente/projeto", "colocar meu código no meu próprio GitHub", "entregar meu projeto", "enviar meu projeto para o swag", ou "entrar na galeria". Faz login no GitHub pessoal da pessoa pelo device flow da CLI gh (um código de uso único, sem precisar colar chaves SSH nem tokens), cria um repositório PÚBLICO e faz push — mas SEMPRE pede que a pessoa confirme o nome do repositório e a conta antes do push. Depois imprime um link do Google Forms com a URL do repositório pré-preenchida. Inclui o ./publish.sh para as partes determinísticas. Não é para implantar o agente (agents-cli) nem o frontend (Cloud Run) — isto publica o código-fonte no GitHub.
---

# Publicar o projeto no GitHub pessoal do participante

O lab roda dentro de uma **workstation efêmera** — quando o lab termina, a máquina e o código que estão nela desaparecem. Esta skill leva o projeto do participante com segurança para o **GitHub pessoal dele** (para que ele guarde e possa compartilhar), e depois entrega um **formulário de envio pré-preenchido** para resgatar swag e participar da galeria de projetos.

A chave para eliminar o atrito é o **device flow do GitHub CLI**: o participante digita um código de uso único em `github.com/login/device` a partir de *qualquer* dispositivo — sem chaves SSH nem tokens para copiar e colar. O token do `gh` vive e morre com a workstation; o repositório permanece para sempre na conta dele.

> **A regra principal — nunca faça push sem confirmação explícita.** Isto cria um repositório no GitHub *pessoal* do participante. Antes de criar o repositório ou fazer push, PARE e obtenha um "sim" explícito sobre o nome do repositório e a confirmação de que é a conta dele. Não aceite aprovações às cegas — mencione o nome e a conta com clareza primeiro.

## Como funciona

```
arquivos do projeto ─▶ publish.sh prep ─▶ gh auth login (código de dispositivo) ─▶ publish.sh commit
                    ─▶ [CONFIRMAR com a pessoa] ─▶ gh repo create --public --push ─▶ URL do repo
                    ─▶ publish.sh formlink <repo_url> ─▶ formulário de envio pré-preenchido
```

O `./publish.sh` cuida das partes determinísticas e não interativas (instalar o `gh`, escrever o `.gitignore`, escanear em busca de segredos, iniciar um histórico de git limpo, montar o link do formulário). As partes **interativas** — o login por device flow e o push — são conduzidas pelo agente, para que o participante aprove explicitamente o push.

Execute tudo a partir da **raiz do projeto** (onde ficam `app/`, `project_brief.md`, `agents-cli-manifest.yaml`). O ideal é que o participante já tenha concluído o passo "Compartilhe o que você construiu", de modo que já existam um `README.md` e um GIF de demonstração no repositório.

## Passo 1 — Preparação (instalar o gh, fazer stage, escanear). Sem commit, sem push.

```bash
bash .agents/skills/publish-to-github/publish.sh prep
export PATH="$HOME/.local/bin:$PATH"   # caso o prep tenha acabado de instalar o gh ali
```

Isso instala o `gh` se ele não estiver presente (em `~/.local/bin`, sem sudo), escreve um `.gitignore` (ignora `.venv/`, `__pycache__/`, `node_modules/`, `*.webm`, segredos; **mantém o GIF de demonstração**), escaneia os arquivos em stage em busca de segredos acidentais (cancela se encontrar algum), inicia um **histórico de git limpo** se a pasta ainda for o repositório clonado do lab, e adiciona tudo ao stage. Ele **NÃO** faz commit nem push.

Se o escaneamento de segredos parar, remova ou adicione ao `.gitignore` o arquivo apontado e execute novamente.

## Passo 2 — Fazer login no GitHub DO PRÓPRIO participante (device flow)

Verifique primeiro e só faça login se for necessário:

```bash
gh auth status >/dev/null 2>&1 || printf 'y\n' | gh auth login --hostname github.com --git-protocol https --web
```

O `printf 'y\n'` responde antecipadamente à única pergunta interativa do `gh` — *"Authenticate Git with your GitHub credentials? (Y/n)"* — que, de outra forma, travaria uma execução não interativa (responder sim configura o credential helper do git para que o push posterior funcione). O `gh auth login` vai imprimir um **código de uso único** e a URL `https://github.com/login/device`.
Repasse ambos ao participante e oriente:

> Abra **github.com/login/device** em qualquer dispositivo, entre com a **sua conta pessoal do GitHub** (não a conta do lab do Qwiklabs) e insira este código: `XXXX-XXXX`.

O comando **fica bloqueado enquanto espera a autorização**, então dê um tempo razoável e peça que a pessoa autorize logo. Confirme o sucesso com `gh auth status` (mostra a conta autenticada — verifique que é a conta pessoal dela, e não uma conta compartilhada ou do lab).

## Passo 3 — Commit (autor = a identidade do GitHub dela)

```bash
bash .agents/skills/publish-to-github/publish.sh commit
```

Isso define o autor do commit a partir do login do GitHub dela (usando o e-mail de preservação de privacidade `<login>@users.noreply.github.com`) e faz o commit do projeto preparado em stage.

## Passo 4 — CONFIRMAR, depois criar o repositório e fazer push

Escolha um nome de repositório. Obtenha o nome padrão com:

```bash
bash .agents/skills/publish-to-github/publish.sh reponame
```

Isso imprime `buildwithgemini-<nome-da-pasta-do-projeto>` (em formato slug) — a convenção de nomenclatura que a equipe do credenciamento procura ao resgatar o swag. Proponha este nome primeiro. O participante pode alterá-lo, mas, se o fizer, oriente que mantenha o prefixo `buildwithgemini-` para que seja reconhecido no balcão de credenciamento.

Depois **peça confirmação explícita** antes de realizar qualquer ação remota, por exemplo:

> Estou prestes a criar um repositório **público** **`<nome>`** na sua conta do GitHub **`<login>`** e subir seu projeto para lá. Deseja continuar?

Somente depois que a pessoa responder afirmativamente:

```bash
gh repo create <name> --public --source=. --remote=origin --push
gh repo view --json url -q .url    # imprime a URL do repositório
```

- Ele precisa obrigatoriamente ser **público** para a galeria e para o compartilhamento em redes sociais.
- Se o nome já estiver ocupado na conta dela, o `gh` vai retornar um erro — escolha outro nome (por exemplo, adicione um sufixo curto) e confirme novamente.

## Passo 5 — Entregar o formulário de envio pré-preenchido

```bash
bash .agents/skills/publish-to-github/publish.sh formlink "<repo_url>"
```

Isso imprime um link do Google Forms com a **URL do repositório** (e, se estiverem presentes no `project_brief.md`, o **título** e a **descrição do projeto**) já preenchidos.
Oriente o participante a abri-lo e preencher os campos que só ele pode responder — o **nome e e-mail de inscrição** dele, se ele já **resgatou o badge GDP**, e se ele **autoriza que o projeto dele seja destacado** — e depois enviar.

Explique os benefícios:

- **Todos que enviarem o formulário** são elegíveis a receber swag (um moletom tipo crewneck) e ao resgate do badge GDP.
- **Os projetos em destaque** são selecionados pela equipe e publicados (com um link para o repositório) na **galeria do GitHub do Track 3 do Build with Gemini**. Esta skill não altera o repositório da galeria — a equipe o gerencia a partir dos envios recebidos.

## Solução de problemas

| Sintoma | Solução |
| --- | --- |
| `gh: command not found` depois do prep | `export PATH="$HOME/.local/bin:$PATH"`; se ainda estiver faltando, instale manualmente: https://github.com/cli/cli#installation |
| A autoinstalação do gh falha | Não há `curl`/acesso à internet, ou a imagem tem restrições — instale o `gh` manualmente (link acima) e execute novamente a partir do Passo 2 |
| O login para em `Authenticate Git with your GitHub credentials? (Y/n)` | Use o comando do Passo 2 (ele inclui `printf 'y\n'`) ou simplesmente responda `Y`. O código do dispositivo aparece logo depois |
| O código do dispositivo expirou / o login travou | Execute novamente `gh auth login --hostname github.com --git-protocol https --web`; autorize o novo código rapidamente |
| Fez login com a conta errada do GitHub | `gh auth logout`, depois faça login novamente com a conta pessoal (ou `gh auth switch`). Verifique com `gh auth status` |
| `git commit` falha: nenhuma identidade configurada | A pessoa ainda não fez login — faça o Passo 2 primeiro, depois `publish.sh commit` |
| `repo create` falha: o nome já existe | Escolha um nome de repositório diferente (adicione um sufixo) e confirme novamente antes do push |
| `remote origin already exists` | A pasta não foi reinicializada (já é o repositório dela). Faça push para o remoto existente (`git push -u origin main`) ou aponte o remoto para o novo repositório |
| Escaneamento de segredos cancelado | Há uma credencial/chave em stage — remova-a ou adicione-a ao `.gitignore`, e execute novamente. Nunca faça commit de `application_default_credentials.json`, `.env` ou chaves de service account |
| Erro de permissão / 403 durante o push | Consulte a skill `troubleshoot-lab-setup`; confirme que a conta autenticada do GitHub tem permissão para criar repositórios |

## Referência

- Script auxiliar: `./publish.sh` (`prep`, `commit`, `reponame`, `formlink`)
- Formulário de envio: "Build with Gemini: Project Submission and Gallery Entry"
- Device flow do gh: https://cli.github.com/manual/gh_auth_login
