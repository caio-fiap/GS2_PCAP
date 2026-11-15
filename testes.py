# testes automaticos. excecutar: python testes.py

import json
import os
import tempfile
import unittest
from base_conhecimento import BaseConhecimento, normalizar
from assistente import tem_dado_pessoal

CAMINHO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/base_conhecimento.json")

class TesteNormalizar(unittest.TestCase):
    def teste_acento_pontuacao(self):
        self.assertEqual(normalizar(" Como. FAÇO o Cartão, do SUS?    "), " como faco o cartao do sus ")

    def test_ordinal(self):
        self.assertEqual(normalizar("2ª via"), " 2a via ")

class TesteBusca(unittest.TestCase):
    def setUp(self):
        self.base = BaseConhecimento(CAMINHO)
        self.assertTrue(self.base.carregar())

    def teste_req_minimos(self):
        self.assertGreaterEqual(len(self.base.orientacoes), 10)
        self.assertGreaterEqual(len(self.base.categorias()), 3)
        for o in self.base.orientacoes:
            self.assertGreaterEqual(len(o.palavras_chave), 3)

    def teste_devolve_tuplas(self):
        res = self.base.buscar("como tirar o passaporte na policia federal")
        self.assertIsInstance(res[0], tuple)
        pontos = [p for p, _ in res]
        self.assertEqual(pontos, sorted(pontos, reverse=True))
        self.assertEqual(res[0][1].id, 8)

    def teste_pontos_rg(self):
        # rg (+3) + segunda via do rg (+3) + "segunda" no título (+1)
        res = self.base.buscar("Como tiro a segunda via do RG?")
        pontos, orientacao = res[0]
        self.assertEqual(orientacao.id, 1)
        self.assertEqual(pontos, 7)  # 3 + 3 + 1
        self.assertEqual(self.base.nivel_confianca(pontos), "ALTA")

    def teste_sem_resposta(self):
        res = self.base.buscar("qual a previsao do tempo amanha")
        melhor = res[0][0] if res else 0
        self.assertIsNone(self.base.nivel_confianca(melhor))

    def teste_confianca_media(self):
        self.assertEqual(self.base.nivel_confianca(3), "MÉDIA")
        self.assertEqual(self.base.nivel_confianca(5), "MÉDIA")
        self.assertEqual(self.base.nivel_confianca(6), "ALTA")
        self.assertIsNone(self.base.nivel_confianca(2))

class TesteDadosPessoais(unittest.TestCase):
    def teste_bloqueia_dados(self):
        self.assertTrue(tem_dado_pessoal("meu cpf é 123.456.789-00"))
        self.assertTrue(tem_dado_pessoal("liga 11 98765 4321"))
        self.assertTrue(tem_dado_pessoal("joao@email.com"))

    def teste_libera_pergunta(self):
        self.assertFalse(tem_dado_pessoal("como tirar a 2 via do rg"))

class TesteArquivos(unittest.TestCase):
    def teste_arquivo_ausente(self):
        # nao trava
        base = BaseConhecimento("nao_existe.json")
        self.assertFalse(base.carregar())
        self.assertTrue(base.avisos)

    def teste_json_corrompido(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            f.write("{ isso nao e json")
            nome = f.name
        try:
            base = BaseConhecimento(nome)
            self.assertFalse(base.carregar())
        finally:
            os.remove(nome)

    def teste_item_invalido(self):
        itens = [{"id": 1, "categoria": "X"}, {"id": 2, "categoria": "C", "titulo": "Titulo", "palavras_chave": ["a", "b", "c"],"resposta": "r", "documentos": [], "onde": "o", "fonte": "f","verificado_em": "2026-11-12"}]
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(itens, f)
            nome = f.name
        try:
            base = BaseConhecimento(nome)
            self.assertTrue(base.carregar())
            self.assertEqual(len(base.orientacoes), 1)
        finally:
            os.remove(nome)

if __name__ == "__main__":
    unittest.main(verbosity=2)