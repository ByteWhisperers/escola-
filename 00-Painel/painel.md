# Painel

O resumo do dia está em [[hoje]] (gerado pelo script). Esta página usa o plugin **Dataview** para mostrar o
mapa inteiro; as propriedades das notas são escritas só pelo script de estado.

## Revisões vencidas

```dataview
TABLE nome AS "Conceito", proxima_revisao AS "Venceu em"
FROM "10-Mapa/matematica"
WHERE estado = "revisar"
SORT proxima_revisao ASC
```

## Em andamento

```dataview
TABLE nome AS "Conceito", estado AS "Estado", acertos_sem_ajuda AS "Acertos", dias_com_acerto AS "Dias", explicou AS "Explicou"
FROM "10-Mapa/matematica"
WHERE estado = "em_estudo" OR estado = "praticando"
```

## Disponíveis para começar

```dataview
LIST nome
FROM "10-Mapa/matematica"
WHERE estado = "disponivel"
```

## Progresso por domínio

```dataview
TABLE length(filter(rows, (r) => r.estado = "dominado" OR r.estado = "revisar")) AS "Dominados", length(rows) AS "Total"
FROM "10-Mapa/matematica"
GROUP BY dominio
```

## Conceitos-limiar

```dataview
TABLE nome AS "Conceito", estado AS "Estado"
FROM "10-Mapa/matematica"
WHERE limiar = true
```
