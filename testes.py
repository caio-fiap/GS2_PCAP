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

