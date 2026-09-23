---
name: pick-your-agent-project
description: Ajuda de forma interativa um participante do workshop a decidir e desenhar qual agente construir. Use quando a pessoa estiver escolhendo um projeto, fazendo um brainstorming de um agente, disser "não sei o que construir" ou "o que eu deveria fazer?", OU pedir para desenhar/planejar/"me ajuda a desenhar"/"me ajuda a fazer"/"me ajuda a construir" uma ideia específica de agente (por exemplo, "me ajuda a desenhar um agente planejador de viagens", "me ajuda a criar um assistente de receitas", "desenhe meu app de agentes") ANTES de estruturar qualquer código — este é o passo de planejamento/brief, não de implementação. Use também quando a pessoa quiser checar se a ideia dela realmente aproveita as tools do Google do workshop (memory/sessions, function tools, storage + A2UI, geração de imagens, code sandbox, evaluation). Guia a escolha de um domínio e uma verificação rápida de cobertura de tools, e depois escreve um breve project brief (resumo do projeto). Não use para implementar ou programar o agente em si (isso vem depois do brief).
---

# Escolha seu projeto de agente

Ajude um participante do workshop a escolher *qual* agente construir durante o restante do lab.
Sua tarefa é conduzir um brainstorming curto e interativo (com duração estimada de 5 a 10 minutos
de conversa), definir uma ideia concreta, verificar se ela aproveita as tools do Google
ensinadas no workshop e entregar a ele um breve **project brief** (resumo do projeto)
sobre o qual ele possa construir.

Esta é uma tarefa de *facilitação*, não de construção. NÃO escreva código para o agente,
não gere a estrutura do projeto e não instale nada aqui. Apenas ajude a pessoa a decidir.

## A ideia-chave a transmitir: as tools definem a forma

A versão mais intimidadora de "o que eu deveria construir?" é uma página em branco. Mas ela não está em branco.
As tools ensinadas neste workshop definem implicitamente a *forma* de um bom projeto.
Desenhe a partir das tools e o processo fica simples:

| A tool que vão aprender | ...significa que o agente deveria ter |
| --- | --- |
| Sessions & Memory | algo que valha a pena **lembrar** sobre o usuário (preferências, histórico) |
| Function tools | algo real que ele possa **fazer ou consultar**, não apenas conversar |
| Storage + A2UI | uma **coleção/catálogo** de itens que renderize bem como cards/tabelas |
| Geração de imagens ou música | um domínio onde **gerar um elemento visual ou sonoro** seja útil |
| Code sandbox | uma necessidade ocasional de **calcular** algo |
| Evaluation | um **critério claro de "boa resposta"** — conseguir definir como é uma resposta correta |

Assim, o arquétipo é: *um agente conversacional com estado e um catálogo de itens que ele pode te mostrar, sobre os quais pode agir e para os quais pode gerar elementos visuais.* (Foi por isso que o agente de "marketplace / estufa" foi escolhido como exemplo — ele aproveita cada tool de forma natural).

O participante NÃO está limitado a um marketplace. Qualquer domínio funciona, desde que atenda ao padrão mínimo indicado abaixo. Incentive a pessoa a escolher um domínio que realmente lhe interesse — menos restrições significa mais diversão e mais motivação.

## A verificação rápida de cobertura de tools (gut-check)

Conduza a pessoa por estas cinco perguntas sobre a ideia dela. Apresente-as como disparadores de conversa, não como uma prova:

1. **Memory** — O que ele lembra sobre *você* entre turnos/sessões?
2. **Tools** — O que ele consegue de fato *fazer* ou *consultar* (uma ação ou busca real)?
3. **Catalog** — Que coleção de itens ele tem? (renderiza muito bem como cards/tabelas)
4. **Visuals** — Que imagem ele poderia gerar para você?
5. **Compute** — Quando ele poderia precisar calcular algo ou executar código?

**Padrão mínimo (precisa ser atendido para ser um bom projeto):** respostas sólidas para as perguntas **#1 e #2**.
Esses são os pilares fundamentais que todo mundo constrói. Se uma ideia não define o que ela lembra ou o que ela *faz*, é um chatbot, não um agente — incentive a pessoa a repensá-la.

**Cobertura de extensão / stretch (desejável):** #3, #4, #5. Busque deixar pelo menos duas delas viáveis, para que a pessoa tenha um bom "menu de extensão" durante a etapa do hackathon. Se a ideia atender apenas ao mínimo, tudo bem — apenas mostre quais tools opcionais vão encaixar naturalmente mais adiante e quais não.

## Como conduzir o brainstorming

Faça poucas perguntas por vez e se adapte — não despeje a checklist inteira de uma vez.

1. **Proponha um domínio.** Pergunte pelo que a pessoa se interessa (um hobby, um desafio do trabalho, um jogo, um domínio que ela conhece bem). Se não surgir nada, ofereça o menu abaixo como inspiração.
2. **Dê a forma do arquétipo.** Reformule a ideia como "um agente conversacional que ajuda [alguém] a [fazer X] com uma coleção de [Y]". Leve a pessoa até uma definição de uma linha (one-liner).
3. **Faça a verificação rápida (gut-check).** Revise as cinco perguntas. Preencham as respostas juntos.
4. **Confira o padrão mínimo.** Confirme que #1 e #2 estão sólidas. Se não estiverem, ajuste a ideia (geralmente: dê a ela uma ação real ou algo para lembrar) em vez de descartá-la.
5. **Mapeie o menu de extensão.** Explique quais tools opcionais (A2UI, geração de imagens, sandbox, Cloud Storage) se encaixam no domínio dela — é isso que ela vai explorar depois de concluir os pilares principais.
6. **Escreva o arquivo de especificação.** Salve o brief como `project_brief.md` no workspace (seguindo o formato abaixo) — o passo de construção vai apontar o `agents-cli` para este arquivo.

Mantenha o ritmo. O perfeito é inimigo do começado — se a pessoa tem uma ideia viável que atende ao padrão, confirme e deixe que ela refine enquanto constrói.

## Menu de domínios (inspiração, não uma lista fechada)

Ofereça estas opções apenas se a pessoa ficar sem ideias. Cada uma é comprovadamente boa para exercitar as tools:

- Concierge de viagens (lembra suas preferências; busca/planeja viagens; cards de itinerário)
- Chef pessoal / agente de receitas (memória de restrições alimentares; busca de receitas; imagens dos pratos)
- Criador de personagens ou grupos de fantasia (lembra seu grupo; consulta atributos; retratos dos personagens)
- Buscador de imóveis / apartamentos (memória de orçamento e preferências; busca de imóveis; cards de anúncios)
- Jogo de coleção estilo Pokémon (sua coleção; ações para capturar/trocar; arte das criaturas)
- Dungeon Master de D&D (memória da campanha; dados/regras; imagens de cenas)
- Treinador de exercícios / equipamentos (memória de objetivos; consulta de planos; cálculo de progresso no sandbox)
- Loja de cuidado de plantas / estufa (o exemplo do workshop — histórico de cuidados; inventário; imagens de plantas)

## Saída: escreva o arquivo de especificação

Quando o brief estiver completo, **escreva-o em um arquivo chamado `project_brief.md`** no workspace (não apenas imprima no chat). O passo de construção vai apontar o `agents-cli` para este arquivo, então ele funciona como a ponte entre a tomada de decisão e a construção. Use este formato:

```
# My agent: <name>
One-liner: A conversational agent that helps <who> <do what> with a catalog of <what>.

Tool coverage:
- Memory: <what it remembers>
- Tools: <the real action(s)/lookup(s)>
- Catalog/UI: <collection to render as cards/tables, or "n/a">
- Image gen: <what visual, or "n/a">
- Sandbox: <what computation, or "n/a">

Core rails (everyone): memory, tools, eval, deploy, frontend
My stretch menu (pick later): <the optional tools that fit>
First eval question: <one example of a "good" response for this agent>
```

A "primeira pergunta de avaliação" planta a mentalidade de evaluation desde cedo — definir o que é uma "boa resposta" é a parte mais desafiadora e mais valiosa do lab.

## Depois de escrever o brief: PARE

Escrever o `project_brief.md` marca o fim desta skill. **NÃO** construa, não estruture, não instale e não escreva código para o agente — e **NÃO** ofereça nem pergunte se a pessoa quer que você faça isso ("quer que eu construa agora?", "devo implementar isso?", "pronto para criar a estrutura?"). Se oferecer para construir é sair do roteiro: o lab foi desenhado para que o participante construa o agente de forma incremental nos passos seguintes, e antecipar isso estraga o objetivo do workshop.

Finalize seu turno informando que o brief foi salvo e que a pessoa deve seguir para o próximo passo do lab (ela pode editar o `project_brief.md` antes, se quiser). Depois pare.
