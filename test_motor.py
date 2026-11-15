"""Testes automatizados: python -m unittest -v"""
import unittest
from motor import Motor, carregar_base


def caso(**fatos):
    m = Motor(carregar_base())
    for nome, valor in fatos.items():
        m.informar(nome, valor)
    m.inferir()
    return m


def ids(m):
    return [d for d, _ in m.conclusoes()]


class TestSistema(unittest.TestCase):
    def test_base_tem_pelo_menos_20_regras(self):
        self.assertGreaterEqual(len(carregar_base()["regras"]), 20)

    def test_queda_com_tela_quebrada(self):
        m = caso(liga=1, caiu=1, tela_quebrada=1)
        self.assertEqual(ids(m)[0], "troca_tela")

    def test_bateria_inchada_e_risco(self):
        self.assertEqual(ids(caso(bateria_inchada=1))[0], "risco_bateria_inchada")

    def test_nao_liga_apos_liquido(self):
        self.assertIn("dano_liquido", ids(caso(liga=0, molhou=1)))

    def test_conector_folgado(self):
        self.assertIn("limpeza_conector", ids(caso(liga=1, carrega=0, conector_folgado=1)))

    def test_lento_e_cheio_indica_software(self):
        self.assertIn("atualizar_formatar", ids(caso(liga=1, lento=1, armazenamento_cheio=1)))

    def test_sem_conclusao(self):
        m = caso(liga=1, molhou=0, caiu=0, tela_quebrada=0, carrega=1, bateria_curta=0)
        self.assertEqual(ids(m), [])

    def test_combinacao_de_evidencias_aumenta_certeza(self):
        so_uma = caso(liga=1, bateria_curta=1, idade_alta=1).derivados["desgaste_bateria"]["cf"]
        duas = caso(liga=1, bateria_curta=1, idade_alta=1, esquenta=1).derivados["desgaste_bateria"]["cf"]
        self.assertGreater(duas, so_uma)

    def test_explicacao_cita_regra(self):
        m = caso(liga=1, caiu=1, tela_quebrada=1)
        self.assertIn("R02", "\n".join(m.como("troca_tela")))

    def test_por_que_lista_regras(self):
        m = Motor(carregar_base())
        self.assertIn("R01", "\n".join(m.por_que("molhou")))

    def test_entrada_invalida(self):
        m = Motor(carregar_base())
        pergunta = m.base["perguntas"][0]
        with self.assertRaises(ValueError):
            m.aplicar(pergunta, "abacaxi")
        m.aplicar(pergunta, "talvez")
        self.assertEqual(m.fatos["liga"], 0.5)

    def test_pergunta_numerica(self):
        m = Motor(carregar_base())
        idade = next(p for p in m.base["perguntas"] if p["fato"] == "tempo_uso")
        m.aplicar(idade, "3")
        self.assertEqual(m.fatos["idade_alta"], 1.0)
        with self.assertRaises(ValueError):
            m.aplicar(idade, "muito")


if __name__ == "__main__":
    unittest.main()
