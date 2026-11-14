# guarda os dados de uma orientação da base e exibe na tela

import re

AVISO = "este assistente não é um canal oficial."

class Orientacao:
    # um registro do json

    def __init__(self, id, categoria, titulo, palavras_chave, resposta, documentos, onde, fonte, verificado_em):
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave
        self.resposta = resposta
        self.documentos = documentos
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em      # Data em dd/mm/aaaa. Outro formato não é aceito

    def data_verificada(self):
        # 'True' se 'verificado_em' está no formato correto
        return bool(re.fullmatch(r"\d{2}/\d{2}/\d{4}", str(self.verificado_em)))

    def exibir(self):
        # Mostra a orientação completa
        print(f"\n>> {self.titulo} [{self.categoria}]")
        print(self.resposta)
        print("Documentos necessários: ")
        for doc in self.documentos:
            print(f"  - {doc}")
        print(f"Onde: {self.onde}")
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print(f"AVISO: {AVISO}")