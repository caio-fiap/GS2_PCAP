# lê o json e lista categorias

import json
from orientacao import Orientacao

# pontuação
PONTOS_PALAVRA_CHAVE = 3 # palavra-chave aparece na pergunta
PONTOS_PALAVRA_TITULO = 1 # palavra da pergunta aparece no título
MIN_LETRAS_TITULO = 4
LIMITE_ALTA = 6
LIMITE_MEDIA = 3 # 3 a 5 pontos: confiança média. Abaixo disso, baixa; cima, alta

CAMPOS_OBRIGATORIOS = ["id", "categoria", "titulo", "palavras_chave", "resposta", "documentos", "onde", "fonte", "verificado_em"]

ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "ê": "e",
           "í": "i", "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ç": "c",
           "ª": "a", "º": "o", "ü": "u"}

def normalizar(texto):
    # minúsculas, sem acentos, sem pontuação e com espaço nas pontas (para procura de palavras inteiras).
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in "?!.,;:()-/\"'":
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "

class BaseConhecimento:
    #conjunto de todas as orientacoes

    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []
        self.avisos = []

    def carregar(self):
        # lê o json e cria os objetos
        self.orientacoes = []
        self.avisos = []
        try:
            with open(self.caminho, "r", encoding = "utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            self.avisos.append(f"Arquivo não encontrado: {self.caminho}")
            return False
        except json.JSONDecodeError as erro:
            self.avisos.append(f"JSON corrompido({erro.msg}, linha {erro.lineno}).")
            return False
        except OSError as erro:
            self.avisos.append(f"Não foi possível ler o arquivo: {erro}")
            return False

        if not isinstance(dados, list):
            self.avisos.append("O JSOn deve ser uma lista de orientações")
            return False

        ids_usados = set()
        for posicao, item in enumerate(dados, start = 1):
            problema = self._validar_item(item, ids_usados)
            if problema:
                self.avisos.append(f"Item {posicao} ignorado: {problema}")
                continue
            ids_usados.add(item["id"])
            self.orientacoes.append(Orientacao(**{c: item[c] for c in CAMPOS_OBRIGATORIOS}))

        pendentes = [str(o.id) for o in self.orientacoes if not o.data_verificada()]
        if pendentes:
            self.avisos.append("Orientações com data de verificação pendente (ids): " + ", ".join(pendentes))
        return len(self.orientacoes) > 0

    @staticmethod   # Pertence à classe, mas não pede 'self'
    def _validar_item(item, ids_usados):
        # devolve um texto descrevendo o problema, ou None
        if not isinstance(item, dict):
            return "Não é um dicionário"
        faltando = [c for c in CAMPOS_OBRIGATORIOS if c not in item]
        if faltando:
            return "Faltam os campos " + ", ".join(faltando)
        if not isinstance(item["id"], int) or item["id"] in ids_usados:
            return "id inválido ou repetido"
        if not isinstance(item["palavras_chave"], list) or len(item["palavras_chave"]) < 3:
            return "precisa de pelo menos 3 palavras-chave"
        if not isinstance(item["documentos"], list):
            return "'documentos' deve ser uma lista"
        for campo in ("categoria", "titulo", "resposta", "onde", "fonte", "verificado_em"):
            if not isinstance(item[campo], str) or not item[campo].strip():
                return f"o campo '{campo}' está vazio"
        return None

    def categorias(self):
        # Lista de categorias
        resultado = []
        for o in self.orientacoes:
            if o.categoria not in resultado:
                resultado.append(o.categoria)
        return resultado

    def por_categoria(self, categoria):
        return [o for o in self.orientacoes if o.categoria == categoria]

    def pontuar(self, orientacao, pergunta_norm):
        #Calcula os pontos de uma orientação
        pontos = 0
        for palavra in orientacao.palavras_chave:
            palavra_norm = normalizar(palavra)
            if palavra_norm.strip() and palavra_norm in pergunta_norm:
                pontos += PONTOS_PALAVRA_CHAVE

        titulo_norm = normalizar(orientacao.titulo)
        for palavra in set(pergunta_norm.split()):      # set: cada palavra conta uma vez
            if len(palavra) >= MIN_LETRAS_TITULO and f" {palavra} " in titulo_norm:
                pontos += PONTOS_PALAVRA_TITULO
        return pontos

    def buscar(self, pergunta):
        #Devolve lista de tuplas (pontos, orientacao), da maior para a menor
        pergunta_norm = normalizar(pergunta)
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(orientacao, pergunta_norm)
            if pontos > 0:
                resultados.append((pontos, orientacao))
        resultados.sort(key=lambda tupla: tupla[0], reverse=True)
        return resultados

    @staticmethod
    def nivel_confianca(pontos):
        #alta, média ou None (abaixo do mínimo)
        if pontos >= LIMITE_ALTA:
            return "ALTA"
        if pontos >= LIMITE_MEDIA:
            return "MÉDIA"
        return None
