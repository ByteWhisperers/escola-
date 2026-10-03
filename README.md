# Escola

Uma escola de uma pessoa só: um autodidata adulto estudando com agentes de IA, a partir da pesquisa sobre
currículos de elite (documento de pesquisa:
https://claude.ai/code/artifact/66b16813-6632-4226-a1dd-e4b133d8baae).

**O Obsidian guarda tudo, o Claude Code ensina e um script em Python cuida do estado.** Os agentes decidem
como ensinar; só o script decide o que você já domina, a partir do registro de cada tentativa.

## Instalação no Windows (uma vez)

1. **Python 3.10 ou mais novo.** No terminal: `python --version`. Se abrir a Microsoft Store ou der erro,
   instale pelo site python.org marcando "Add python.exe to PATH". O script só usa a biblioteca padrão.
2. **Git** e **Claude Code** instalados e funcionando no terminal.
3. **Obsidian** (obsidian.md). Abra esta pasta como cofre ("Open folder as vault").
4. Em *Settings → Community plugins*, ative os plugins da comunidade e instale:
   - **Dataview** (painéis em `00-Painel/painel.md`);
   - **Obsidian Git** (backup automático; configure "Auto commit-and-sync interval", por exemplo 10 minutos).
5. Teste o script, na raiz desta pasta:
   ```
   python 90-Sistema/scripts/estado.py painel
   python -m unittest discover -s 90-Sistema/testes
   ```
   Se `python` não funcionar mas `py` funcionar, troque `python` por `py` em `.claude/settings.json`
   e no `CLAUDE.md`.

## Uso

Abra o terminal nesta pasta e rode `claude`. Ao abrir, um hook mostra o painel do dia.

| Comando | Quando | O que faz |
| --- | --- | --- |
| `/diagnostico` | Uma vez, no começo | Até 14 perguntas para achar seu ponto de partida |
| `/sessao` | Todo dia, 45 a 60 min | Revisão, estudo guiado, prática e fechamento |
| `/tutorial` | Uma vez por semana | Tutorial no modelo de Oxford e tarefa de ensaio |

No Obsidian, veja `00-Painel/hoje.md` (resumo do dia) e `00-Painel/painel.md` (mapa inteiro). O grafo do
Obsidian mostra o mapa de conceitos, porque cada nota liga os seus pré-requisitos.

## Como o progresso funciona

Cada tentativa vira uma linha em `90-Sistema/dados/eventos.jsonl`, sempre pelo comando
`python 90-Sistema/scripts/estado.py registrar ...`. O script recalcula os estados:

bloqueado → disponível → em estudo → praticando → **dominado** → revisar → (dominado ou praticando)

- **Dominado:** 3 acertos sem ajuda em 2 dias diferentes e 1 explicação correta (limiares: 4 acertos em 3 dias).
- **Revisão:** 1, 3, 7, 21 e 60 dias depois do domínio. Errou ou precisou de ajuda: volta a praticar.
- **Diagnóstico:** um acerto marca o conceito e seus pré-requisitos como dominados; os inferidos entram na
  revisão a partir de 7 dias.

Nunca edite à mão o `eventos.jsonl` nem as propriedades das notas de conceito: o script reescreve as
propriedades a cada cálculo. A seção "Minhas anotações" de cada nota é sua e nunca é apagada.

## Pastas

| Pasta | Conteúdo |
| --- | --- |
| `.claude/skills/` | As skills dos agentes: `sessao`, `diagnostico`, `tutorial`, `agente-memoria`, `tutor-demonstracao` |
| `00-Painel/` | Painel do dia (gerado) e painel Dataview |
| `10-Mapa/matematica/` | Os 54 conceitos, de valor posicional a equações do 2º grau |
| `20-Sessoes/` | Uma nota por sessão |
| `30-Ensaios/` | Ensaios semanais |
| `40-Diagnosticos/` | Resultados do diagnóstico |
| `50-Banco-de-questoes/` | Questões criadas pelos agentes |
| `60-Fontes/` | Pesquisa e novas fontes |
| `70-Estudo-de-aula/` | Propostas mensais de melhoria, que só valem com a sua aprovação |
| `90-Sistema/` | Script de estado, testes, dados, gabaritos, modelos e a origem do mapa |

## O que ainda não existe

- Os outros 9 agentes do desenho (entram conforme o estudo de aula mostrar a necessidade).
- O comando `/estudo-de-aula` e o `/div`.
- Celular (depois, via Git ou Obsidian Sync).
- Troca da agenda fixa de revisão pelo algoritmo FSRS (biblioteca `py-fsrs`), quando houver dados.

## Origem do mapa

`90-Sistema/mapa-fonte/construir_mapa.py` gera o mapa a partir dos dados do Coherence Map da Achieve the Core
(`brutos/cm_scope.json`), dos livros abertos da OpenStax e de estudos do OpenAlex. A versão do cofre
(`90-Sistema/dados/mapa_matematica.json`) separa as respostas do diagnóstico em `dados/gabaritos/`.
