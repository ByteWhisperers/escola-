---
name: sessao
description: Conduz a sessão diária de estudo (45 a 60 minutos) - revisão espaçada, estudo guiado do conceito atual, prática intercalada e fechamento com nota da sessão. Use quando o aluno pedir /sessao ou disser que quer estudar hoje.
---

# Sessão diária

Siga o `CLAUDE.md`. Tempos são sugestões; pergunte ao aluno quanto tempo ele tem hoje e ajuste.

## 0. Preparar

1. Rode `python 90-Sistema/scripts/estado.py painel` e leia o resultado.
2. Se nenhum evento existe ainda, proponha começar pelo `/diagnostico` e pare aqui se ele aceitar.
3. Defina o identificador da sessão: `AAAA-MM-DD-a` (use `b`, `c`... se já houver sessão no dia em `20-Sessoes/`).
   Passe `--sessao <id>` em todos os `registrar` desta sessão.
4. Diga ao aluno, em 3 linhas: quantas revisões vencidas, qual o conceito atual, qual o plano de hoje.

## 1. Recuperação (cerca de 10 min)

Siga a skill `agente-memoria` (leia `.claude/skills/agente-memoria/SKILL.md`).

## 2. Estudo guiado (cerca de 20 min)

Escolha o conceito:
- se houver um conceito em `praticando` ou `em_estudo`, continue nele;
- senão, o primeiro da lista "Próximos disponíveis" do painel.

Siga a skill `tutor-demonstracao` (leia `.claude/skills/tutor-demonstracao/SKILL.md`).

## 3. Prática intercalada (cerca de 15 min)

Ainda com o `tutor-demonstracao`: exercícios do conceito atual misturados com 1 ou 2 de conceitos dominados
parecidos. Registre cada tentativa.

## 4. Fechamento (cerca de 5 min)

1. Rode `python 90-Sistema/scripts/estado.py painel` de novo e mostre ao aluno o que mudou.
2. Pergunte: "o que você aprendeu hoje, em uma frase?" e "o que ficou difícil?".
3. Crie a nota da sessão em `20-Sessoes/AAAA/<id>.md` a partir de `90-Sistema/templates/sessao.md`,
   com as respostas dele nas palavras dele e um resumo factual do que foi feito.
4. Lembre que o Obsidian Git envia tudo para o GitHub (ou sugira `git add -A && git commit -m "sessao <id>"`).

## Se o aluno travar ou se frustrar

Reduza o passo, volte a um exemplo resolvido, ou troque para revisão de algo que ele domina. Diga com
clareza que errar faz parte do método. Nunca resolva por ele para "salvar" a sessão.
