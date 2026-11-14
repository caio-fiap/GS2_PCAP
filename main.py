# Citizen Assist AI. Executar com: python main.py

import os

from base_conhecimento import BaseConhecimento
import assistente

# caminho da base de conhecimento
PASTA = os.path.dirname(os.path.abspath(__file__))
CAMINHO_BASE = os.path.join(PASTA, "data/base_conhecimento.json")

def main():
    base = BaseConhecimento(CAMINHO_BASE)
    carregou = base.carregar()

    for aviso in base.avisos:
        print(f"Aviso: {aviso}")
    if not carregou:
        print("Não foi possível carregar orientações. O assistente abrirá sem base")

if __name__ == "__main__":
    main()
