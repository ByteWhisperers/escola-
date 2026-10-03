"""Constroi e valida o mapa de conceitos de matematica (fundamentos ate algebra).

Fontes: Achieve the Core Coherence Map (pre-requisitos entre padroes), OpenStax
Prealgebra 2e (PA) e Elementary Algebra 2e (EA) (capitulos), OpenAlex (conceitos-limiar).
"""
import csv, json, collections, pathlib

AQUI = pathlib.Path(__file__).parent
SAIDA = AQUI / "saida"

DOMINIOS = {
    "N": "Numero e valor posicional",
    "O": "Operacoes com numeros naturais",
    "F": "Fracoes e decimais",
    "R": "Razao, proporcao e porcentagem",
    "I": "Numeros negativos e reais",
    "G": "Geometria e medida (apoio)",
    "E": "Expressoes e equacoes",
    "FN": "Funcoes e graficos",
    "P": "Potencias e polinomios",
}

LIMIARES = {
    "divisao": ("Siegler, Duncan e Davis-Kean, 2012", "https://doi.org/10.1177/0956797612440101",
                "Saber divisao no fundamental preve algebra e desempenho geral no ensino medio, mesmo controlando QI, memoria e renda"),
    "fracao_numero": ("Siegler, Thompson e Schneider, 2011; Siegler e outros, 2012", "https://doi.org/10.1016/j.cogpsych.2011.03.001",
                      "Fracoes preveem algebra 5 ou 6 anos depois; entender fracao como numero na reta é o centro da teoria"),
    "decimais": ("Rittle-Johnson, Siegler e Alibali, 2001; Lortie-Forgues, Tian e Siegler, 2015", "https://doi.org/10.1037/0022-0663.93.2.346",
                 "Entender decimais exige ligar conceito e procedimento; aritmetica de fracoes e decimais é notoriamente dificil"),
    "proporcionalidade": ("Tourniaire e Pulos, 1985; Hoyles, Noss e Pozzi, 2001", "https://doi.org/10.1007/bf02400937",
                          "Raciocinio proporcional é um marco do desenvolvimento e aparece em praticas profissionais como dosagem de remedios"),
    "negativos": ("Bofferding e Wessman-Enzinger, 2017; Bruno e Martinon, 1999", "https://doi.org/10.54870/1551-3440.1396",
                  "Passar dos naturais aos inteiros exige reorganizar o que se sabe sobre subtracao e a reta numerica"),
    "sinal_igual": ("Knuth, Stephens, McNeil e Alibali, 2006", "https://doi.org/10.2307/30034852",
                    "Entender o sinal de igual como equivalência esta associado ao sucesso em equacoes, mesmo controlando a habilidade"),
    "variavel": ("Knuth, Alibali, McNeil e outros, 2011; Asquith, Stephens, Knuth e Alibali, 2007", "https://doi.org/10.1007/978-3-642-17735-4_15",
                 "Equivalência e variavel sao os dois conceitos centrais da algebra escolar; professores subestimam a dificuldade"),
}

# id, nome, dominio, descricao, codigos Common Core, capitulo OpenStax, pre-requisitos
CONCEITOS = [
    ("valor_posicional", "Valor posicional", "N", "O valor de um algarismo depende da posicao; cada posicao vale 10 vezes a da direita", "4.NBT.A", "PA 1", []),
    ("estimativa", "Arredondamento e estimativa", "N", "Arredondar e estimar para checar se um resultado faz sentido", "3.NBT.A; 4.NBT.A", "PA 1", ["valor_posicional"]),
    ("adicao_subtracao", "Adicao e subtracao com varios digitos", "O", "Somar e subtrair usando valor posicional e reagrupamento", "4.NBT.B", "PA 1", ["valor_posicional"]),
    ("multiplicacao", "Significado da multiplicacao", "O", "Multiplicacao como grupos iguais, area e comparacao", "3.OA.A", "PA 1", ["adicao_subtracao"]),
    ("propriedades", "Propriedades das operacoes", "O", "Comutativa, associativa e distributiva como ferramentas de calculo", "3.OA.B", "PA 7", ["multiplicacao"]),
    ("divisao", "Significado da divisao", "O", "Divisao como partilha e como medida; inversa da multiplicacao", "3.OA.A; 3.OA.B", "PA 1", ["multiplicacao"]),
    ("mult_varios_digitos", "Multiplicacao com varios digitos", "O", "Algoritmo da multiplicacao explicado pelo valor posicional e pela distributiva", "4.NBT.B; 5.NBT.B", "PA 1", ["multiplicacao", "propriedades", "valor_posicional"]),
    ("divisao_longa", "Divisao com varios digitos", "O", "Algoritmo da divisao, quociente e resto", "4.NBT.B; 5.NBT.B; 6.NS.B", "PA 1", ["divisao", "mult_varios_digitos"]),
    ("fatores_multiplos", "Fatores, multiplos e primos", "O", "Divisores, multiplos, MDC, MMC e fatoracao em primos", "4.OA.B; 6.NS.B", "PA 2", ["divisao"]),
    ("ordem_operacoes", "Expressoes numericas e ordem das operacoes", "O", "Ler e calcular expressoes com parenteses e várias operacoes", "5.OA.A", "PA 2", ["propriedades"]),
    ("fracao_unitaria", "Fracao unitaria", "F", "1/b como uma parte de um todo dividido em b partes iguais", "3.NF.A", "PA 4", ["divisao"]),
    ("fracao_numero", "Fracao como numero na reta", "F", "a/b é um numero com lugar na reta, inclusive maior que 1", "3.NF.A", "PA 4", ["fracao_unitaria"]),
    ("fracoes_equivalentes", "Fracoes equivalentes e comparacao", "F", "Frações diferentes podem ser o mesmo numero; comparar e ordenar", "4.NF.A", "PA 4", ["fracao_numero", "fatores_multiplos"]),
    ("soma_fracoes", "Somar e subtrair fracoes", "F", "Somar com denominador comum; numeros mistos", "4.NF.B; 5.NF.A", "PA 4", ["fracoes_equivalentes"]),
    ("mult_fracoes", "Multiplicar fracoes", "F", "Fracao de uma quantidade; area de retangulos com lados fracionarios", "4.NF.B; 5.NF.B", "PA 4", ["fracoes_equivalentes", "mult_varios_digitos"]),
    ("div_fracoes", "Dividir fracoes", "F", "Quantas vezes uma fracao cabe na outra; divisao como inversa da multiplicacao", "5.NF.B; 6.NS.A", "PA 4", ["mult_fracoes", "divisao"]),
    ("decimais", "Decimais e valor posicional decimal", "F", "Decimais como fracoes de denominador 10, 100...; comparar decimais", "4.NF.C; 5.NBT.A", "PA 5", ["valor_posicional", "fracoes_equivalentes"]),
    ("operacoes_decimais", "Operacoes com decimais", "F", "Somar, subtrair, multiplicar e dividir decimais", "5.NBT.B; 6.NS.B", "PA 5", ["decimais", "divisao_longa"]),
    ("razao", "Razao e taxa", "R", "Comparar duas quantidades multiplicativamente", "6.RP.A", "PA 5", ["fracao_numero", "divisao"]),
    ("taxa_unitaria", "Taxa unitaria e tabelas de razoes", "R", "Quanto por 1; tabelas e retas duplas", "6.RP.A", "PA 5", ["razao", "operacoes_decimais"]),
    ("porcentagem", "Porcentagem", "R", "Porcentagem como razao por 100; aumentos e descontos", "6.RP.A; 7.RP.A", "PA 6", ["taxa_unitaria", "decimais"]),
    ("proporcionalidade", "Relacoes proporcionais (y = kx)", "R", "Reconhecer e usar a constante de proporcionalidade em tabelas, graficos e equacoes", "7.RP.A", "PA 6", ["taxa_unitaria", "mult_fracoes"]),
    ("unidades", "Grandezas e unidades", "G", "Converter unidades e raciocinar com elas", "5.MD.A; N-Q.A", "EA 1", ["taxa_unitaria"]),
    ("area", "Area e sua ligacao com a multiplicacao", "G", "Area de retangulos como produto dos lados", "3.MD.C", "PA 9", ["multiplicacao"]),
    ("area_volume", "Area de figuras e volume", "G", "Triangulos, poligonos, prismas; formulas como expressoes", "6.G.A; 7.G.B", "PA 9", ["area", "mult_fracoes"]),
    ("negativos", "Numeros negativos e a reta numerica", "I", "Numeros abaixo de zero, oposto e valor absoluto", "6.NS.C", "PA 3; EA 1", ["fracao_numero"]),
    ("soma_inteiros", "Somar e subtrair inteiros", "I", "Soma e subtracao com sinais, explicadas na reta", "7.NS.A", "PA 3; EA 1", ["negativos", "adicao_subtracao"]),
    ("mult_inteiros", "Multiplicar e dividir inteiros", "I", "Regras de sinal justificadas pela distributiva", "7.NS.A", "PA 3; EA 1", ["soma_inteiros", "divisao", "propriedades"]),
    ("racionais", "Operacoes com numeros racionais", "I", "As quatro operacoes com fracoes e decimais positivos e negativos", "7.NS.A", "PA 7; EA 1", ["mult_inteiros", "div_fracoes", "operacoes_decimais"]),
    ("plano_cartesiano", "Plano cartesiano", "I", "Localizar pontos nos quatro quadrantes", "5.G.A; 6.NS.C", "PA 11; EA 4", ["negativos"]),
    ("potencias", "Potencias e raiz quadrada", "I", "Potencias como multiplicacao repetida; quadrados e raizes", "6.EE.A; 8.EE.A", "PA 10; EA 6", ["ordem_operacoes", "mult_inteiros"]),
    ("irracionais", "Numeros irracionais e os reais", "I", "Numeros que nao sao fracoes; aproximacoes de raizes", "8.NS.A", "EA 1", ["decimais", "potencias"]),
    ("linguagem_algebra", "Linguagem da algebra", "E", "Escrever e ler expressoes com letras", "6.EE.A", "PA 2; EA 1", ["ordem_operacoes"]),
    ("variavel", "Variavel", "E", "Letra como numero desconhecido ou como quantidade que varia", "6.EE.A; 6.EE.B", "PA 2", ["linguagem_algebra"]),
    ("sinal_igual", "Sinal de igual como equivalência", "E", "= significa 'mesmo valor dos dois lados', nao 'o resultado é'", "6.EE.B", "PA 2", ["ordem_operacoes"]),
    ("expr_equivalentes", "Expressoes equivalentes", "E", "Distributiva, combinar termos semelhantes, fatorar numeros", "6.EE.A; 7.EE.A", "PA 2; EA 1", ["variavel", "propriedades", "mult_inteiros"]),
    ("eq_um_passo", "Equacoes de um passo", "E", "Resolver mantendo a igualdade dos dois lados", "6.EE.B", "PA 2; EA 2", ["variavel", "sinal_igual"]),
    ("inequacoes", "Inequacoes", "E", "Desigualdades com variavel e suas solucoes na reta", "6.EE.B; 7.EE.B", "EA 2", ["eq_um_passo", "negativos"]),
    ("eq_varios_passos", "Equacoes lineares de varios passos", "E", "Variavel dos dois lados, parenteses, fracoes", "7.EE.B; 8.EE.C; A-REI.B", "PA 8; EA 2", ["expr_equivalentes", "eq_um_passo", "racionais"]),
    ("formulas", "Resolver formulas", "E", "Isolar uma variavel numa formula", "A-CED.A", "EA 2", ["eq_varios_passos"]),
    ("modelagem", "Transformar problemas em equacoes", "E", "Escrever e resolver equacoes que descrevem situacoes", "7.EE.B; A-CED.A", "PA 9; EA 3", ["eq_varios_passos", "porcentagem"]),
    ("funcao", "Conceito de funcao", "FN", "Regra que associa a cada entrada uma unica saida", "8.F.A; F-IF.A", "", ["variavel", "plano_cartesiano"]),
    ("grafico_linear", "Grafico de equacoes lineares", "FN", "Tabela, grafico e equacao da mesma relacao", "8.EE.B; F-IF.C", "EA 4", ["plano_cartesiano", "eq_varios_passos"]),
    ("inclinacao", "Inclinacao como taxa de variacao", "FN", "Quanto y muda quando x aumenta 1", "8.EE.B; 8.F.B", "EA 4", ["grafico_linear", "proporcionalidade"]),
    ("reta", "Equacao da reta (y = mx + b)", "FN", "Construir e interpretar a equacao de uma reta", "8.F.B; F-LE.A", "EA 4", ["inclinacao", "funcao"]),
    ("interpretar_funcoes", "Interpretar funcoes em contexto", "FN", "Ler o que graficos e formulas dizem sobre uma situacao", "F-IF.B; F-LE.B", "", ["reta"]),
    ("sistemas", "Sistemas de equacoes lineares", "E", "Duas equacoes, duas incognitas: grafico, substituicao, eliminacao", "8.EE.C; A-REI.C", "EA 5", ["eq_varios_passos", "reta"]),
    ("linear_exponencial", "Crescimento linear e exponencial", "FN", "Somar sempre o mesmo valor ou multiplicar sempre pelo mesmo fator", "F-LE.A", "", ["reta", "potencias", "porcentagem"]),
    ("pitagoras", "Teorema de Pitagoras", "G", "Relacao entre os lados do triangulo retangulo", "8.G.B", "PA 9", ["area_volume", "potencias"]),
    ("regras_expoentes", "Propriedades dos expoentes", "P", "Produto, quociente e potencia de potencias; expoentes negativos e zero", "8.EE.A; N-RN.A", "EA 6", ["potencias", "mult_inteiros"]),
    ("polinomios", "Operacoes com polinomios", "P", "Somar, subtrair e multiplicar polinomios", "A-APR.A", "PA 10; EA 6", ["expr_equivalentes", "regras_expoentes"]),
    ("fatoracao", "Fatoracao", "P", "Fator comum, diferença de quadrados e trinômios", "A-SSE.A; A-SSE.B", "EA 7", ["polinomios", "fatores_multiplos"]),
    ("eq_segundo_grau", "Equacoes do 2o grau (introdução)", "P", "Resolver por fatoracao e entender as solucoes", "A-REI.B; A-SSE.B", "EA 10", ["fatoracao", "eq_varios_passos"]),
    ("radicais", "Raizes e radicais", "P", "Simplificar e operar com raizes", "8.EE.A; N-RN.B", "EA 9", ["potencias", "irracionais"]),
]

PONTES = {
    "proporcionalidade": "Dosagem de remedios (Hoyles e outros, 2001), receitas e escala de mapas",
    "porcentagem": "Juros, inflacao e descontos (economia)",
    "inclinacao": "Velocidade como variacao da posicao no tempo (fisica)",
    "variavel": "Variaveis em programacao e colunas em tabelas de dados",
    "funcao": "Funcoes em programacao: entrada, regra, saida",
    "linear_exponencial": "Juros compostos, crescimento populacional e epidemias",
    "fracao_numero": "Ritmo musical: semibreve, minima, seminima",
    "razao": "Mistura de cores e concentracao em quimica",
    "plano_cartesiano": "Mapas, latitude e longitude",
    "fatores_multiplos": "Engrenagens e ciclos que se repetem (calendarios)",
    "sinal_igual": "Balanca em equilibrio; equacoes químicas balanceadas",
    "pitagoras": "Distancia em mapas e em graficos",
}

DIAGNOSTICO = [
    # (ordem, conceito, pergunta, resposta, erro comum que revela)
    (1, "valor_posicional", "No número 4.705, quanto vale o algarismo 7?", "700", "Responder 7: não ligar o algarismo à posição"),
    (2, "divisao", "Três pizzas são divididas igualmente entre 4 pessoas. Quanto cada uma recebe? Explique.", "3/4 de pizza", "Dizer que não dá, ou responder 4/3: divisão só como 'maior por menor'"),
    (3, "fracao_numero", "Numa reta de 0 a 2, onde fica 5/4? É maior ou menor que 1?", "Entre 1 e 1,5 (1,25); maior que 1", "Achar que toda fração é menor que 1"),
    (4, "fracoes_equivalentes", "O que é maior: 3/8 ou 2/5? Como você sabe?", "2/5 (16/40 contra 15/40)", "Comparar numeradores ou denominadores separadamente"),
    (5, "decimais", "O que é maior: 0,45 ou 0,5?", "0,5", "Escolher 0,45 porque 45 é maior que 5"),
    (6, "div_fracoes", "Quantos pedaços de 3/4 de metro cabem em 6 metros?", "8", "Multiplicar 6 por 3/4 (4,5)"),
    (7, "proporcionalidade", "Uma receita usa 2 xícaras de farinha para 3 de leite. Com 7,5 xícaras de leite, quanta farinha?", "5 xícaras", "Responder 6,5: somar a diferença em vez de multiplicar"),
    (8, "porcentagem", "Um preço de R$ 80 sobe 25% e depois cai 25%. Quanto fica?", "R$ 75", "Responder R$ 80: tratar as porcentagens como se tivessem a mesma base"),
    (9, "soma_inteiros", "Quanto é −3 − (−8)? Mostre na reta numérica.", "5", "Responder −11: juntar os sinais"),
    (10, "sinal_igual", "Que número completa a igualdade: 8 + 4 = __ + 5?", "7", "Responder 12: ler '=' como 'dá o resultado'"),
    (11, "variavel", "O que é maior: 2n ou n + 2? Explique.", "Depende de n: 2n é maior se n > 2, iguais se n = 2, menor se n < 2", "Dizer que 2n é sempre maior: letra como número fixo"),
    (12, "eq_varios_passos", "Resolva 3(x − 2) = 2x + 5.", "x = 11", "Errar a distributiva (3x − 2) ou o sinal ao mudar de lado"),
    (13, "reta", "Um táxi cobra R$ 5 fixos mais R$ 3 por km. Escreva a regra. O que o 3 representa no gráfico?", "y = 3x + 5; o 3 é a inclinação (quanto sobe por km)", "Confundir a parte fixa com a taxa por km"),
    (14, "regras_expoentes", "Simplifique 2³ · 2⁴ e explique por que funciona.", "2⁷ = 128, porque são 3 + 4 fatores iguais a 2", "Multiplicar os expoentes (2¹²) ou as bases (4⁷)"),
]
REGRA_DIAGNOSTICO = ("Começar pela pergunta 7 (proporção). Acertou: seguir para 10, 11, 12, 13 e 14. "
                     "Errou: descer para 6, 5, 3, 2 e 1. Cada erro marca o conceito como em_estudo e "
                     "o cartógrafo testa os pré-requisitos dele com perguntas novas.")
REVISAO = ("Sugestão inicial, a ajustar com os dados: revisar 1, 3, 7, 21 e 60 dias depois do domínio. "
           "Cepeda e outros (2006) mostram que o melhor intervalo cresce com o tempo que se quer reter.")

CRITERIO = ("Dominado quando o aluno resolve 3 problemas novos sem ajuda, em pelo menos 2 dias diferentes, "
            "e explica o raciocinio de 1 deles em voz alta ou por escrito.")



ACENTOS = {
    "numero": "número", "numeros": "números", "numerica": "numérica", "numericas": "numéricas",
    "operacoes": "operações", "fracao": "fração", "fracoes": "frações", "adicao": "adição",
    "subtracao": "subtração", "digitos": "dígitos", "multiplicacao": "multiplicação", "divisao": "divisão",
    "expressoes": "expressões", "unitaria": "unitária", "comparacao": "comparação", "razao": "razão",
    "razoes": "razões", "proporcao": "proporção", "relacoes": "relações", "relacao": "relação",
    "area": "área", "ligacao": "ligação", "potencias": "potências", "algebra": "álgebra",
    "variavel": "variável", "variaveis": "variáveis", "equacoes": "equações", "equacao": "equação",
    "inequacoes": "inequações", "varios": "vários", "formulas": "fórmulas", "formula": "fórmula",
    "funcao": "função", "funcoes": "funções", "grafico": "gráfico", "graficos": "gráficos",
    "inclinacao": "inclinação", "variacao": "variação", "pitagoras": "Pitágoras", "polinomios": "polinômios",
    "fatoracao": "fatoração", "raizes": "raízes", "naturais": "naturais", "medicao": "medição",
    "posicao": "posição", "explicacao": "explicação", "reagrupamento": "reagrupamento", "comparacoes": "comparações",
    "rapido": "rápido", "e": "e", "ate": "até", "nao": "não", "sao": "são", "tambem": "também",
    "inversa": "inversa", "partilha": "partilha", "multiplos": "múltiplos", "multiplo": "múltiplo",
    "parenteses": "parênteses", "denominador": "denominador", "numeros mistos": "números mistos",
    "quantidade": "quantidade", "retangulos": "retângulos", "retangulo": "retângulo", "fracionarios": "fracionários",
    "decimal": "decimal", "taxa": "taxa", "porcentagem": "porcentagem", "constante": "constante",
    "graficos,": "gráficos,", "triangulos": "triângulos", "triangulo": "triângulo", "poligonos": "polígonos",
    "oposto": "oposto", "absoluto": "absoluto", "regras": "regras", "racionais": "racionais",
    "quadrantes": "quadrantes", "multiplicacao repetida": "multiplicação repetida", "aproximacoes": "aproximações",
    "incognitas": "incógnitas", "substituicao": "substituição", "eliminacao": "eliminação", "solucoes": "soluções",
    "situacoes": "situações", "situacao": "situação", "entrada": "entrada", "saida": "saída", "unica": "única",
    "construir": "construir", "fisica": "física", "programacao": "programação", "remedios": "remédios",
    "economia": "economia", "inflacao": "inflação", "populacional": "populacional", "musical": "musical",
    "seminima": "semínima", "minima": "mínima", "quimica": "química", "concentracao": "concentração",
    "calendarios": "calendários", "balanca": "balança", "equilibrio": "equilíbrio", "distancia": "distância",
    "raciocinio": "raciocínio", "dominado": "dominado", "voz": "voz", "dias": "dias", "diferentes": "diferentes",
    "pratica": "prática", "praticas": "práticas", "dosagem": "dosagem", "notoriamente": "notoriamente",
    "dificil": "difícil", "aritmetica": "aritmética", "centro": "centro", "teoria": "teoria",
    "memoria": "memória", "renda": "renda", "habilidade": "habilidade", "sucesso": "sucesso",
    "associado": "associado", "conceitos": "conceitos", "escolar": "escolar", "dificuldade": "dificuldade",
    "subestimam": "subestimam", "reorganizar": "reorganizar", "numerica,": "numérica,", "medio": "médio",
    "fundamental": "fundamental", "preve": "prevê", "preveem": "preveem", "depois": "depois",
    "marco": "marco", "profissionais": "profissionais", "reta": "reta", "medida": "medida",
    "geometria": "geometria", "apoio": "apoio", "mesmo": "mesmo", "dois": "dois", "lados": "lados",
    "calculo": "cálculo", "algarismo": "algarismo", "vale": "vale", "direita": "direita",
    "esta": "está", "sera": "será", "ja": "já", "so": "só", "tambem,": "também,", "voce": "você",
    "media": "média", "minimo": "mínimo", "maximo": "máximo", "semibreve": "semibreve",
    "2o": "2º", "geografica": "geográfica", "latitude": "latitude", "atencao": "atenção",
    "expoentes": "expoentes", "quociente": "quociente", "potencia": "potência", "propriedades": "propriedades",
    "simplificar": "simplificar", "raiz": "raiz", "irracionais": "irracionais", "frações": "frações",
}
import re as _re
def acentuar(t):
    if not t:
        return t
    def troca(m):
        w = m.group(0); low = w.lower()
        if low not in ACENTOS:
            return w
        r = ACENTOS[low]
        return r[0].upper() + r[1:] if w[0].isupper() else r
    return _re.sub(r"[A-Za-z0-9]+", troca, t)


def carregar_coherence():
    cm = json.load(open(AQUI / "brutos" / "cm_scope.json"))
    por_codigo = {c["code"]: cid for cid, c in cm["clusters"].items()}
    adj = collections.defaultdict(set)
    for a, b, _ in cm["edges"]:
        adj[a].add(b)
    return cm, por_codigo, adj


def clusters_do_conceito(codigos, por_codigo):
    out = set()
    for c in [x.strip() for x in codigos.split(";")]:
        if c in por_codigo:
            out.add(por_codigo[c])
    return out


def alcanca(adj, origens, destinos):
    vistos, pilha = set(origens), list(origens)
    while pilha:
        n = pilha.pop()
        if n in destinos:
            return True
        for m in adj[n]:
            if m not in vistos:
                vistos.add(m); pilha.append(m)
    return False


def main():
    ids = [c[0] for c in CONCEITOS]
    assert len(ids) == len(set(ids)), "ids repetidos"
    por_id = {c[0]: c for c in CONCEITOS}
    erros = []
    for c in CONCEITOS:
        for p in c[6]:
            if p not in por_id:
                erros.append(f"pre-requisito inexistente: {c[0]} <- {p}")
    for k in LIMIARES:
        if k not in por_id:
            erros.append(f"limiar sem conceito: {k}")

    # ordem topologica (Kahn), estavel pela ordem da lista
    grau = {i: len(por_id[i][6]) for i in ids}
    filhos = collections.defaultdict(list)
    for c in CONCEITOS:
        for p in c[6]:
            filhos[p].append(c[0])
    fila = [i for i in ids if grau[i] == 0]
    ordem = []
    while fila:
        n = fila.pop(0); ordem.append(n)
        for f in filhos[n]:
            grau[f] -= 1
            if grau[f] == 0:
                fila.append(f)
    for _, c, *_ in DIAGNOSTICO:
        if c not in por_id:
            erros.append(f"diagnostico sem conceito: {c}")
    if len(ordem) != len(ids):
        erros.append("ciclo detectado: " + ", ".join(sorted(set(ids) - set(ordem))))

    # checagem contra o Coherence Map
    cm, por_codigo, adj = carregar_coherence()
    sem_cluster, apoiadas, nao_apoiadas, mesmo_cluster = [], 0, [], 0
    apoio = {}
    for c in CONCEITOS:
        cc = clusters_do_conceito(c[4], por_codigo)
        if not cc:
            sem_cluster.append(c[0]); continue
        for p in c[6]:
            pc = clusters_do_conceito(por_id[p][4], por_codigo)
            if not pc:
                continue
            if pc & cc:
                mesmo_cluster += 1; apoio[(p, c[0])] = "mesmo_grupo_coherence_map"
            elif alcanca(adj, pc, cc):
                apoiadas += 1; apoio[(p, c[0])] = "coherence_map"
            else:
                nao_apoiadas.append(f"{p} -> {c[0]}"); apoio[(p, c[0])] = "julgamento_a_revisar"

    nivel = {}
    for n in ordem:
        nivel[n] = 1 + max([nivel[p] for p in por_id[n][6]], default=0)

    dados = {
        "nome": "Mapa de conceitos de Matemática: fundamentos até álgebra",
        "versao": "0.1",
        "data": "2026-10-02",
        "criterio_dominio": acentuar(CRITERIO),
        "estados_possiveis": ["nao_visto", "em_estudo", "dominado", "revisar"],
        "fontes": {
            "pre_requisitos": "Achieve the Core, Coherence Map (https://achievethecore.org/coherence-map/)",
            "capitulos": "OpenStax Prealgebra 2e (PA) e Elementary Algebra 2e (EA)",
            "limiares": "OpenAlex; ver campo limiar de cada conceito",
        },
        "dominios": {k: acentuar(v) for k, v in DOMINIOS.items()},
        "agenda_revisao": REVISAO,
        "diagnostico": {"regra": REGRA_DIAGNOSTICO, "perguntas": [
            {"ordem": o, "conceito": c, "pergunta": q, "resposta": r, "erro_comum": e} for o, c, q, r, e in DIAGNOSTICO]},
        "conceitos": [],
    }
    for n in ordem:
        c = por_id[n]
        lim = LIMIARES.get(n)
        dados["conceitos"].append({
            "id": n, "nome": acentuar(c[1]), "dominio": c[2], "descricao": acentuar(c[3]),
            "common_core": [x.strip() for x in c[4].split(";")],
            "openstax": c[5] or None,
            "pre_requisitos": c[6],
            "apoio_das_ligacoes": {p: apoio.get((p, n), "julgamento_a_revisar") for p in c[6]},
            "nivel": nivel[n],
            "limiar": ({"estudo": acentuar(lim[0]), "link": lim[1], "porque": acentuar(lim[2])} if lim else None),
            "ponte": acentuar(PONTES.get(n)),
            "estado_aluno": {"estado": "nao_visto", "acertos_sem_ajuda": [], "proxima_revisao": None},
        })

    SAIDA.mkdir(exist_ok=True)
    json.dump(dados, open(SAIDA / "mapa_matematica.json", "w"), ensure_ascii=False, indent=2)
    with open(SAIDA / "conceitos.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ordem", "id", "nome", "dominio", "nivel", "limiar", "common_core", "openstax", "pre_requisitos", "ponte"])
        for i, c in enumerate(dados["conceitos"], 1):
            w.writerow([i, c["id"], c["nome"], c["dominio"], c["nivel"], "sim" if c["limiar"] else "",
                        "; ".join(c["common_core"]), c["openstax"] or "", "; ".join(c["pre_requisitos"]), c["ponte"] or ""])
    with open(SAIDA / "ligacoes.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["de", "para", "apoio"])
        for c in dados["conceitos"]:
            for p in c["pre_requisitos"]:
                w.writerow([p, c["id"], c["apoio_das_ligacoes"][p]])

    # ligacoes entre dominios
    dom_edges = collections.Counter()
    for c in CONCEITOS:
        for p in c[6]:
            a, b = por_id[p][2], c[2]
            if a != b:
                dom_edges[(a, b)] += 1

    anc = {}
    for n in ordem:
        a = set()
        for p in por_id[n][6]:
            a |= {p} | anc[p]
        anc[n] = a
    clus = {c[0]: clusters_do_conceito(c[4], por_codigo) for c in CONCEITOS}
    sugest = set()
    for x in ids:
        for y in ids:
            if x != y and x not in anc[y] and y not in anc[x] and not (clus[x] & clus[y]):
                if any(b in clus[y] for a in clus[x] for b in adj[a]):
                    sugest.add((x, y))
    print(f"ligacoes diretas do Coherence Map ausentes do mapa (entre conceitos sem relacao): {len(sugest)}")
    # lista omitida: comparacao por grupo e grosseira demais para sugerir ligacoes
    total = sum(len(c[6]) for c in CONCEITOS)
    print(f"conceitos: {len(ids)} | ligacoes: {total} | limiares: {len(LIMIARES)} | pontes: {len(PONTES)} | niveis: {max(nivel.values())}")
    print("erros:", erros or "nenhum")
    print(f"Coherence Map: {apoiadas} ligacoes com caminho no mapa, {mesmo_cluster} dentro do mesmo grupo, "
          f"{len(nao_apoiadas)} sem caminho: {nao_apoiadas}")
    print("conceitos sem grupo do Coherence Map:", sem_cluster)
    print("por dominio:", collections.Counter(c[2] for c in CONCEITOS))
    print("ligacoes entre dominios:", sorted(dom_edges.items()))
    return 1 if erros else 0


if __name__ == "__main__":
    raise SystemExit(main())
