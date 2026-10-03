---
name: diagnostico
description: Aplica o diagnóstico inicial de matemática (até 14 perguntas adaptativas) para descobrir por onde o aluno começa no mapa. Use uma vez, no início, ou quando o aluno pedir /diagnostico.
---

# Diagnóstico inicial

Siga o `CLAUDE.md`.

1. Leia as perguntas em `90-Sistema/dados/gabaritos/diagnostico.json` (pergunta, resposta e erro comum).
   **Nunca mostre a resposta nem o erro comum antes de o aluno responder.**
2. Explique ao aluno em 3 linhas: são até 14 perguntas, sem calculadora e sem consulta, vale "não sei",
   e o objetivo é achar o ponto de partida, não dar nota.
3. Siga a regra do arquivo: comece pela pergunta 7. Acertou: vá para 10, 11, 12, 13 e 14. Errou: desça para
   6, 5, 3, 2 e 1. Pare de descer no primeiro acerto. As perguntas 8 e 9 servem para confirmar porcentagem e
   números negativos quando houver dúvida.
4. Faça uma pergunta por vez. Para as que pedem "explique", só conte como certa se o raciocínio estiver certo.
5. Registre cada resposta:
   `python 90-Sistema/scripts/estado.py registrar --conceito <conceito da pergunta> --tipo diagnostico --resultado <certo|errado> --ajuda sem --agente diagnostico --questao diag-<ordem>`
   "Não sei" conta como `errado`.
6. No fim, rode `python 90-Sistema/scripts/estado.py painel` e explique o resultado:
   - acertar uma pergunta marca aquele conceito e os pré-requisitos dele como dominados ("inferidos");
   - conceitos inferidos entram na revisão espaçada a partir de 7 dias: se ele errar a revisão, voltam à prática;
   - o próximo conceito disponível é onde a primeira `/sessao` começa.
7. Salve um resumo em `40-Diagnosticos/AAAA-MM-DD.md`: perguntas feitas, acertos, erros e o erro comum que
   apareceu em cada erro (agora pode citar o gabarito).
