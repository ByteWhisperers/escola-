"""Estado de aprendizagem da escola.

Os agentes nunca escrevem estado. Eles registram eventos com `registrar`;
este script recalcula o estado de cada conceito a partir dos eventos e
reescreve as propriedades das notas em 10-Mapa/.

Uso (a partir da raiz do cofre):
    python 90-Sistema/scripts/estado.py painel
    python 90-Sistema/scripts/estado.py registrar --conceito proporcionalidade \
        --tipo exercicio --resultado certo --ajuda sem --agente tutor-demonstracao
    python 90-Sistema/scripts/estado.py recalcular
    python 90-Sistema/scripts/estado.py gerar-notas

So usa a biblioteca padrao do Python (3.10 ou mais nova).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[2]
MAPA = RAIZ / "90-Sistema" / "dados" / "mapa_matematica.json"
EVENTOS = RAIZ / "90-Sistema" / "dados" / "eventos.jsonl"
NOTAS = RAIZ / "10-Mapa" / "matematica"
HOJE_MD = RAIZ / "00-Painel" / "hoje.md"

TIPOS = {"inicio", "recuperacao", "exercicio", "explicacao", "tutorial", "ensaio", "diagnostico"}
RESULTADOS = {"certo", "parcial", "errado"}
AJUDAS = {"sem", "dica", "resolvido"}

# Agenda fixa de revisao (dias). Trocar por FSRS quando houver dados.
INTERVALOS = [1, 3, 7, 21, 60]
# Portao de dominio: (acertos sem ajuda, dias diferentes)
PORTAO = (3, 2)
PORTAO_LIMIAR = (4, 3)
# Conceitos inferidos pelo diagnostico: primeira revisao espalhada para nao lotar um dia
INFERIDO_BASE_DIAS, INFERIDO_ESPALHAR = 7, 14

TEXTO_ESTADO = {
    "bloqueado": "Bloqueado", "disponivel": "Disponível", "em_estudo": "Em estudo",
    "praticando": "Praticando", "dominado": "Dominado", "revisar": "Revisar",
}


# ---------------------------------------------------------------- dados

def carregar_mapa(caminho: pathlib.Path = MAPA) -> dict:
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def carregar_eventos(caminho: pathlib.Path = EVENTOS) -> list[dict]:
    if not caminho.exists():
        return []
    eventos = []
    with open(caminho, encoding="utf-8") as f:
        for n, linha in enumerate(f, 1):
            linha = linha.strip()
            if not linha:
                continue
            try:
                eventos.append(json.loads(linha))
            except json.JSONDecodeError as e:
                raise SystemExit(f"eventos.jsonl linha {n} invalida: {e}")
    eventos.sort(key=lambda e: e["quando"])
    return eventos


def dia(quando: str) -> dt.date:
    return dt.date.fromisoformat(quando[:10])


# ---------------------------------------------------------------- calculo

def ancestrais(conceitos: dict[str, dict]) -> dict[str, set[str]]:
    memo: dict[str, set[str]] = {}

    def anc(i: str) -> set[str]:
        if i not in memo:
            s: set[str] = set()
            for p in conceitos[i]["pre_requisitos"]:
                s |= {p} | anc(p)
            memo[i] = s
        return memo[i]

    for i in conceitos:
        anc(i)
    return memo


def novo_registro() -> dict:
    return {"estado": None, "acertos": 0, "dias": set(), "explicou": False, "nivel_revisao": 0,
            "dominado_em": None, "proxima_revisao": None, "inferido": False,
            "tutorial": False, "ensaio": False, "tentativas": 0, "erros": 0}


def zerar_portao(r: dict) -> None:
    r["acertos"], r["dias"], r["explicou"] = 0, set(), False


def dominar(r: dict, quando: dt.date, dias_ate_revisao: int) -> None:
    r["estado"] = "dominado"
    r["dominado_em"] = quando
    r["nivel_revisao"] = 0
    r["proxima_revisao"] = quando + dt.timedelta(days=dias_ate_revisao)


def calcular(mapa: dict, eventos: list[dict], hoje: dt.date) -> dict[str, dict]:
    """Aplica as 7 regras de transicao. Funcao pura: mesmos eventos, mesmo resultado."""
    conceitos = {c["id"]: c for c in mapa["conceitos"]}
    ordem = [c["id"] for c in mapa["conceitos"]]  # ja vem em ordem topologica
    anc = ancestrais(conceitos)
    reg = {i: novo_registro() for i in ordem}

    # Diagnostico: acerto em X infere dominio de X e dos seus pre-requisitos,
    # exceto os que tiveram erro explicito no diagnostico.
    erros_diag = {e["conceito"] for e in eventos if e["tipo"] == "diagnostico" and e["resultado"] != "certo"}
    inferidos: dict[str, dt.date] = {}
    for e in eventos:
        if e["tipo"] == "diagnostico" and e["resultado"] == "certo" and e["ajuda"] == "sem":
            for a in anc[e["conceito"]]:
                if a not in erros_diag:
                    inferidos.setdefault(a, dia(e["quando"]))

    for k, i in enumerate(ordem):
        if i in inferidos:
            r = reg[i]
            dominar(r, inferidos[i], INFERIDO_BASE_DIAS + k % INFERIDO_ESPALHAR)
            r["inferido"] = True

    for e in eventos:
        r = reg[e["conceito"]]
        d = dia(e["quando"])
        limiar = bool(conceitos[e["conceito"]].get("limiar"))
        meta_acertos, meta_dias = PORTAO_LIMIAR if limiar else PORTAO
        certo_sem_ajuda = e["resultado"] == "certo" and e["ajuda"] == "sem"
        r["tentativas"] += 1
        if e["resultado"] == "errado":
            r["erros"] += 1

        if e["tipo"] == "diagnostico":
            if certo_sem_ajuda:
                dominar(r, d, INTERVALOS[0])
                r["inferido"] = False
            continue
        if e["tipo"] == "tutorial" and e["resultado"] == "certo":
            r["tutorial"] = True
        if e["tipo"] == "ensaio" and e["resultado"] == "certo":
            r["ensaio"] = True

        estado = r["estado"]
        if estado is None:  # regra 2: primeiro evento abre o estudo
            r["estado"] = estado = "em_estudo"
        if estado == "em_estudo" and e["tipo"] in {"exercicio", "recuperacao"} and e["resultado"] == "certo":
            r["estado"] = estado = "praticando"  # regra 3
        if estado == "praticando":
            if e["tipo"] in {"exercicio", "recuperacao"} and certo_sem_ajuda:
                r["acertos"] += 1
                r["dias"].add(d)
            if e["tipo"] == "explicacao" and e["resultado"] == "certo":
                r["explicou"] = True
            if r["acertos"] >= meta_acertos and len(r["dias"]) >= meta_dias and r["explicou"]:
                dominar(r, d, INTERVALOS[0])  # regra 4: portao
                r["inferido"] = False
            continue
        if estado == "dominado" and e["tipo"] == "recuperacao":
            if certo_sem_ajuda:  # regra 6
                r["nivel_revisao"] = min(r["nivel_revisao"] + 1, len(INTERVALOS) - 1)
                r["proxima_revisao"] = d + dt.timedelta(days=INTERVALOS[r["nivel_revisao"]])
                r["inferido"] = False
            else:  # regra 7
                r["estado"] = "praticando"
                r["proxima_revisao"] = None
                zerar_portao(r)

    # regras 1 e 5, que dependem do dia de hoje e dos pre-requisitos
    dominados = set()
    for i in ordem:
        r = reg[i]
        if r["estado"] == "dominado":
            dominados.add(i)
            if r["proxima_revisao"] and r["proxima_revisao"] <= hoje:
                r["estado"] = "revisar"
        elif r["estado"] is None:
            prereq_ok = all(p in dominados for p in conceitos[i]["pre_requisitos"])
            r["estado"] = "disponivel" if prereq_ok else "bloqueado"
        if r["estado"] == "revisar":
            dominados.add(i)

    for i in ordem:
        r = reg[i]
        if r["estado"] in {"dominado", "revisar"}:
            r["etapa"] = "completa" if r["ensaio"] else "retorica" if r["tutorial"] else "dialetica"
        elif r["estado"] in {"em_estudo", "praticando"}:
            r["etapa"] = "gramatica"
        else:
            r["etapa"] = None
    return reg


# ---------------------------------------------------------------- notas

def _yaml(v) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, list):
        return "[" + ", ".join(_yaml(x) for x in v) + "]"
    if isinstance(v, dt.date):
        return v.isoformat()
    s = str(v)
    return json.dumps(s, ensure_ascii=False) if any(ch in s for ch in ':#[]{},"\'') or s != s.strip() else s


def frontmatter(c: dict, r: dict | None, dominios: dict) -> str:
    r = r or novo_registro()
    campos = [
        ("id", c["id"]), ("nome", c["nome"]), ("dominio", dominios[c["dominio"]]),
        ("pre_requisitos", c["pre_requisitos"]), ("limiar", bool(c.get("limiar"))),
        ("estado", r["estado"]), ("etapa", r.get("etapa")),
        ("acertos_sem_ajuda", r["acertos"]), ("dias_com_acerto", len(r["dias"])),
        ("explicou", r["explicou"]), ("dominado_em", r["dominado_em"]),
        ("proxima_revisao", r["proxima_revisao"]),
        ("intervalo_dias", INTERVALOS[r["nivel_revisao"]] if r["proxima_revisao"] else None),
        ("inferido_no_diagnostico", r["inferido"]),
        ("openstax", c.get("openstax")), ("common_core", c.get("common_core", [])),
    ]
    linhas = ["---"] + [f"{k}: {_yaml(v)}".rstrip() for k, v in campos] + ["---"]
    return "\n".join(linhas) + "\n"


def corpo_inicial(c: dict, nomes: dict[str, str]) -> str:
    partes = [f"# {c['nome']}", "", c["descricao"], ""]
    if c["pre_requisitos"]:
        partes += ["## Pré-requisitos", ""] + [f"- [[{p}|{nomes[p]}]]" for p in c["pre_requisitos"]] + [""]
    if c.get("limiar"):
        l = c["limiar"]
        partes += ["## Por que é um limiar", "", f"{l['porque']} ([{l['estudo']}]({l['link']}))", ""]
    if c.get("ponte"):
        partes += ["## Ponte com outras áreas", "", c["ponte"], ""]
    partes += ["## Onde estudar", "", f"OpenStax: {c.get('openstax') or 'a definir'}", "",
               "## Minhas anotações", "", ""]
    return "\n".join(partes)


def separar(texto: str) -> str:
    """Devolve o corpo de uma nota, sem o bloco de propriedades."""
    if texto.startswith("---"):
        fim = texto.find("\n---", 3)
        if fim != -1:
            return texto[fim + 4:].lstrip("\n")
    return texto


def escrever_notas(mapa: dict, reg: dict[str, dict] | None, criar: bool = False) -> int:
    NOTAS.mkdir(parents=True, exist_ok=True)
    nomes = {c["id"]: c["nome"] for c in mapa["conceitos"]}
    n = 0
    for c in mapa["conceitos"]:
        arq = NOTAS / f"{c['id']}.md"
        if arq.exists():
            corpo = separar(arq.read_text(encoding="utf-8"))
        elif criar:
            corpo = corpo_inicial(c, nomes)
        else:
            continue
        novo = frontmatter(c, (reg or {}).get(c["id"]), mapa["dominios"]) + "\n" + corpo
        if not arq.exists() or arq.read_text(encoding="utf-8") != novo:
            arq.write_text(novo, encoding="utf-8")
            n += 1
    return n


# ---------------------------------------------------------------- painel

def resumo(mapa: dict, reg: dict[str, dict], hoje: dt.date) -> str:
    nomes = {c["id"]: c["nome"] for c in mapa["conceitos"]}
    ordem = [c["id"] for c in mapa["conceitos"]]
    por = {s: [i for i in ordem if reg[i]["estado"] == s] for s in TEXTO_ESTADO}
    revisar = sorted(por["revisar"], key=lambda i: reg[i]["proxima_revisao"])
    atuais = por["praticando"] + por["em_estudo"]
    linhas = [f"# Painel de hoje — {hoje.isoformat()}", ""]
    linhas += ["Contagem: " + ", ".join(f"{TEXTO_ESTADO[s]} {len(v)}" for s, v in por.items()), ""]
    linhas += [f"## Revisões vencidas ({len(revisar)})", ""]
    linhas += [f"- [[{i}|{nomes[i]}]] (venceu em {reg[i]['proxima_revisao']})" for i in revisar[:15]] or ["- nenhuma"]
    if len(revisar) > 15:
        linhas.append(f"- e mais {len(revisar) - 15}")
    linhas += ["", "## Em andamento", ""]
    for i in atuais:
        r = reg[i]
        meta = PORTAO_LIMIAR if mapa_limiar(mapa, i) else PORTAO
        linhas.append(f"- [[{i}|{nomes[i]}]]: {TEXTO_ESTADO[r['estado']]}; acertos sem ajuda {r['acertos']}/{meta[0]}, "
                      f"dias {len(r['dias'])}/{meta[1]}, explicação {'sim' if r['explicou'] else 'não'}")
    if not atuais:
        linhas.append("- nenhum")
    linhas += ["", "## Próximos disponíveis", ""]
    linhas += [f"- [[{i}|{nomes[i]}]]" for i in por["disponivel"][:5]] or ["- nenhum"]
    if not any(reg[i]["tentativas"] for i in ordem):
        linhas += ["", "Nenhum evento ainda: comece pelo comando /diagnostico."]
    return "\n".join(linhas) + "\n"


def mapa_limiar(mapa: dict, i: str) -> bool:
    return any(c["id"] == i and c.get("limiar") for c in mapa["conceitos"])


# ---------------------------------------------------------------- comandos

def cmd_registrar(a) -> None:
    mapa = carregar_mapa()
    ids = {c["id"] for c in mapa["conceitos"]}
    erros = []
    if a.conceito not in ids:
        erros.append(f"conceito desconhecido: {a.conceito}")
    if a.tipo not in TIPOS:
        erros.append(f"tipo invalido: {a.tipo} (use {sorted(TIPOS)})")
    if a.resultado not in RESULTADOS:
        erros.append(f"resultado invalido: {a.resultado} (use {sorted(RESULTADOS)})")
    if a.ajuda not in AJUDAS:
        erros.append(f"ajuda invalida: {a.ajuda} (use {sorted(AJUDAS)})")
    if erros:
        raise SystemExit("; ".join(erros))
    quando = a.quando or dt.datetime.now().isoformat(timespec="minutes")
    ev = {"quando": quando, "sessao": a.sessao or quando[:10], "conceito": a.conceito, "tipo": a.tipo,
          "resultado": a.resultado, "ajuda": a.ajuda, "agente": a.agente, "questao": a.questao, "nota": a.nota}
    EVENTOS.parent.mkdir(parents=True, exist_ok=True)
    with open(EVENTOS, "a", encoding="utf-8") as f:
        f.write(json.dumps({k: v for k, v in ev.items() if v is not None}, ensure_ascii=False) + "\n")
    reg = calcular(mapa, carregar_eventos(), dt.date.today())
    r = reg[a.conceito]
    print(f"registrado: {a.conceito} {a.tipo} {a.resultado} ({a.ajuda}); estado agora: {TEXTO_ESTADO[r['estado']]}")


def recalcular(hoje: dt.date | None = None) -> tuple[dict, dict]:
    hoje = hoje or dt.date.today()
    mapa = carregar_mapa()
    reg = calcular(mapa, carregar_eventos(), hoje)
    escrever_notas(mapa, reg)
    HOJE_MD.parent.mkdir(parents=True, exist_ok=True)
    HOJE_MD.write_text(resumo(mapa, reg, hoje), encoding="utf-8")
    return mapa, reg


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("registrar", help="registra uma tentativa (unica forma de os agentes mexerem no progresso)")
    r.add_argument("--conceito", required=True)
    r.add_argument("--tipo", required=True)
    r.add_argument("--resultado", required=True)
    r.add_argument("--ajuda", required=True)
    r.add_argument("--agente", required=True)
    r.add_argument("--sessao")
    r.add_argument("--questao")
    r.add_argument("--nota", help="observacao curta, opcional")
    r.add_argument("--quando", help="AAAA-MM-DDTHH:MM (padrao: agora)")
    sub.add_parser("recalcular", help="recalcula estados e atualiza notas e painel")
    sub.add_parser("painel", help="recalcula e mostra o painel do dia (usado pelo hook)")
    sub.add_parser("gerar-notas", help="cria as notas de conceito que ainda nao existem")
    a = p.parse_args(argv)

    if a.cmd == "registrar":
        cmd_registrar(a)
        recalcular()
    elif a.cmd == "gerar-notas":
        mapa = carregar_mapa()
        reg = calcular(mapa, carregar_eventos(), dt.date.today())
        n = escrever_notas(mapa, reg, criar=True)
        print(f"{n} notas criadas ou atualizadas em {NOTAS.relative_to(RAIZ)}")
    elif a.cmd == "recalcular":
        recalcular()
        print("estados recalculados")
    elif a.cmd == "painel":
        _, _ = recalcular()
        print(HOJE_MD.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
