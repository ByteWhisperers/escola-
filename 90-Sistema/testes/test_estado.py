"""Testes das regras de transicao. Rodar da raiz do cofre:
    python -m unittest discover -s 90-Sistema/testes
"""
import datetime as dt
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
import estado  # noqa: E402

D = dt.date


def mapa_teste():
    # a -> b -> c ; c e limiar
    return {
        "dominios": {"X": "Teste"},
        "conceitos": [
            {"id": "a", "nome": "A", "dominio": "X", "descricao": "", "pre_requisitos": [], "limiar": None},
            {"id": "b", "nome": "B", "dominio": "X", "descricao": "", "pre_requisitos": ["a"], "limiar": None},
            {"id": "c", "nome": "C", "dominio": "X", "descricao": "", "pre_requisitos": ["b"],
             "limiar": {"estudo": "x", "link": "x", "porque": "x"}},
        ],
    }


def ev(quando, conceito, tipo, resultado="certo", ajuda="sem"):
    return {"quando": quando, "conceito": conceito, "tipo": tipo, "resultado": resultado, "ajuda": ajuda}


def dominar_a(dias=("2026-10-01", "2026-10-02")):
    d1, d2 = dias
    return [ev(f"{d1}T10:00", "a", "inicio"),
            ev(f"{d1}T10:05", "a", "exercicio"), ev(f"{d1}T10:10", "a", "exercicio"),
            ev(f"{d2}T10:00", "a", "exercicio"), ev(f"{d2}T10:05", "a", "explicacao")]


class Regras(unittest.TestCase):
    def setUp(self):
        self.m = mapa_teste()

    def test_sem_eventos_regra_1(self):
        r = estado.calcular(self.m, [], D(2026, 10, 1))
        self.assertEqual([r[i]["estado"] for i in "abc"], ["disponivel", "bloqueado", "bloqueado"])

    def test_inicio_regra_2(self):
        r = estado.calcular(self.m, [ev("2026-10-01T10:00", "a", "inicio")], D(2026, 10, 1))
        self.assertEqual(r["a"]["estado"], "em_estudo")
        self.assertEqual(r["a"]["etapa"], "gramatica")

    def test_primeiro_acerto_mesmo_com_dica_regra_3(self):
        eventos = [ev("2026-10-01T10:00", "a", "inicio"), ev("2026-10-01T10:05", "a", "exercicio", ajuda="dica")]
        r = estado.calcular(self.m, eventos, D(2026, 10, 1))
        self.assertEqual(r["a"]["estado"], "praticando")
        self.assertEqual(r["a"]["acertos"], 0)  # com dica nao conta para o portao

    def test_portao_exige_dois_dias_regra_4(self):
        eventos = [ev("2026-10-01T10:00", "a", "inicio")] + \
                  [ev(f"2026-10-01T10:0{k}", "a", "exercicio") for k in range(1, 5)] + \
                  [ev("2026-10-01T10:09", "a", "explicacao")]
        r = estado.calcular(self.m, eventos, D(2026, 10, 1))
        self.assertEqual(r["a"]["estado"], "praticando")  # 4 acertos, mas num dia so

    def test_portao_exige_explicacao(self):
        eventos = dominar_a()[:-1]
        r = estado.calcular(self.m, eventos, D(2026, 10, 2))
        self.assertEqual(r["a"]["estado"], "praticando")

    def test_portao_completo_libera_proximo(self):
        r = estado.calcular(self.m, dominar_a(), D(2026, 10, 2))
        self.assertEqual(r["a"]["estado"], "dominado")
        self.assertEqual(r["a"]["proxima_revisao"], D(2026, 10, 3))
        self.assertEqual(r["b"]["estado"], "disponivel")
        self.assertEqual(r["a"]["etapa"], "dialetica")

    def test_revisao_vencida_regra_5(self):
        r = estado.calcular(self.m, dominar_a(), D(2026, 10, 3))
        self.assertEqual(r["a"]["estado"], "revisar")
        self.assertEqual(r["b"]["estado"], "disponivel")  # revisar ainda conta como dominado

    def test_revisao_certa_aumenta_intervalo_regra_6(self):
        eventos = dominar_a() + [ev("2026-10-03T09:00", "a", "recuperacao")]
        r = estado.calcular(self.m, eventos, D(2026, 10, 3))
        self.assertEqual(r["a"]["estado"], "dominado")
        self.assertEqual(r["a"]["proxima_revisao"], D(2026, 10, 6))  # 3 dias

    def test_revisao_errada_volta_a_praticar_regra_7(self):
        eventos = dominar_a() + [ev("2026-10-03T09:00", "a", "recuperacao", resultado="errado")]
        r = estado.calcular(self.m, eventos, D(2026, 10, 3))
        self.assertEqual(r["a"]["estado"], "praticando")
        self.assertEqual(r["a"]["acertos"], 0)

    def test_revisao_com_ajuda_tambem_volta(self):
        eventos = dominar_a() + [ev("2026-10-03T09:00", "a", "recuperacao", ajuda="dica")]
        r = estado.calcular(self.m, eventos, D(2026, 10, 3))
        self.assertEqual(r["a"]["estado"], "praticando")

    def test_limiar_exige_4_acertos_em_3_dias(self):
        base = dominar_a() + [ev("2026-10-02T11:00", "b", "inicio")] + \
               [ev(f"2026-10-0{d}T12:00", "b", "exercicio") for d in (2, 3, 4)] + \
               [ev("2026-10-04T12:05", "b", "explicacao")]
        base += [ev("2026-10-04T13:00", "c", "inicio")] + \
                [ev(f"2026-10-0{d}T14:00", "c", "exercicio") for d in (4, 5, 6)] + \
                [ev("2026-10-06T14:05", "c", "explicacao")]
        r = estado.calcular(self.m, base, D(2026, 10, 6))
        self.assertEqual(r["b"]["estado"], "revisar")  # dominado dia 4, revisao venceu dia 5
        self.assertEqual(r["c"]["estado"], "praticando")  # so 3 acertos
        base.append(ev("2026-10-06T15:00", "c", "exercicio"))
        r = estado.calcular(self.m, base, D(2026, 10, 6))
        self.assertEqual(r["c"]["estado"], "dominado")

    def test_parcial_nao_conta(self):
        eventos = [ev("2026-10-01T10:00", "a", "inicio"), ev("2026-10-01T10:01", "a", "exercicio")] + \
                  [ev(f"2026-10-0{d}T10:02", "a", "exercicio", resultado="parcial") for d in (2, 3)] + \
                  [ev("2026-10-03T10:05", "a", "explicacao")]
        r = estado.calcular(self.m, eventos, D(2026, 10, 3))
        self.assertEqual(r["a"]["estado"], "praticando")

    def test_diagnostico_infere_pre_requisitos(self):
        r = estado.calcular(self.m, [ev("2026-10-01T10:00", "c", "diagnostico")], D(2026, 10, 1))
        self.assertEqual([r[i]["estado"] for i in "abc"], ["dominado"] * 3)
        self.assertTrue(r["a"]["inferido"])
        self.assertFalse(r["c"]["inferido"])
        self.assertGreaterEqual(r["a"]["proxima_revisao"], D(2026, 10, 8))  # inferidos revisam depois

    def test_erro_no_diagnostico_bloqueia_inferencia(self):
        eventos = [ev("2026-10-01T10:00", "a", "diagnostico", resultado="errado"),
                   ev("2026-10-01T10:05", "c", "diagnostico")]
        r = estado.calcular(self.m, eventos, D(2026, 10, 1))
        self.assertEqual(r["a"]["estado"], "disponivel")
        self.assertEqual(r["b"]["estado"], "dominado")

    def test_tutorial_e_ensaio_avancam_etapa(self):
        eventos = dominar_a() + [ev("2026-10-02T12:00", "a", "tutorial")]
        r = estado.calcular(self.m, eventos, D(2026, 10, 2))
        self.assertEqual(r["a"]["etapa"], "retorica")
        eventos.append(ev("2026-10-02T13:00", "a", "ensaio"))
        r = estado.calcular(self.m, eventos, D(2026, 10, 2))
        self.assertEqual(r["a"]["etapa"], "completa")

    def test_resultado_e_reproduzivel(self):
        e = dominar_a()
        self.assertEqual(estado.calcular(self.m, e, D(2026, 10, 2)), estado.calcular(self.m, list(e), D(2026, 10, 2)))


class MapaReal(unittest.TestCase):
    def test_mapa_do_cofre_e_valido(self):
        m = estado.carregar_mapa()
        ids = [c["id"] for c in m["conceitos"]]
        self.assertEqual(len(ids), len(set(ids)))
        vistos = set()
        for c in m["conceitos"]:  # ordem topologica: pre-requisito sempre antes
            for p in c["pre_requisitos"]:
                self.assertIn(p, vistos, f"{p} deveria vir antes de {c['id']}")
            vistos.add(c["id"])

    def test_frontmatter_preserva_corpo(self):
        texto = "---\nid: x\n---\n\n# X\n\nminhas notas\n"
        self.assertEqual(estado.separar(texto), "# X\n\nminhas notas\n")


if __name__ == "__main__":
    unittest.main()
