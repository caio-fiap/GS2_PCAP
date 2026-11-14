# "conversa" com o usuário, guarda histórico e calcula indicadores

import os
import csv
import json
import time
from datetime import datetime

from orientacao import AVISO

CAMPOS_CSV = ["data", "origem", "pergunta", "orientacao_id", "encontrou", "ajudou", "tentativas", "tempo_segundos", "nota_facilidade"]

def entrada(texto):
    #trata o fim da entrada sem da rerro
    try:
        return input(texto).strip()
    except EOFError:
        raise KeyboardInterrupt

def ler_opcao(texto, minimo, maximo):
    # repete até o usuário digitar um número valido
    while True:
        valor = entrada(texto)
        if valor.isdigit() and minimo <= int(valor) <= maximo:
            return int(valor)
        print(f"Opção inválida. Digite um número de {minimo} a {maximo}.")

def ler_sim_nao(texto):
    # repete até o usuário digitar s ou n, e devolve True para 's'
    while True:
        valor = entrada(texto).lower()
        if valor in ("s", "n"):
            return valor == "s"
        print(f"Resposta inválida. Digite s ou n.")

def tem_dado_pessoal(texto):
    # 8 digitos ou mais, ou @
    digitos = sum(1 for letra in texto if letra.isdigit())
    return digitos >= 8 or "@" in texto

class Assistente:
    # quem "conversa" com o cidadão

    def __init__(self, nome, base, caminho_historico = "data/historico.json", caminho_csv = "data/atendimentos.csv"):
        self.nome = nome
        self.base = base
        self.caminho_historico = caminho_historico
        self.caminho_csv = caminho_csv
        self.historico - self._carregar_historico()
        self._inicio_sessao = len(self.historico)

    def _carregar_historico(self):
        try:
            with open(self.caminho_historico, "r", encoding = "utf-8") as arquivo:
                dados = json.load(arquivo)
            if isinstance(dados, list):
                return [d for d in dados if isinstance(d, dict)]
            print("Aviso: histórico em formato inesperado. Começando um novo.")
        except FileNotFoundError:
            pass
        except (json.JSONDecodeError, OSError):
            print("Aviso: histórico ilegível. Começando um novo.")
        return []

    def _salvar_historico(self):
        try:
            pasta = os.path.dirname(self.caminho_historico)
            if pasta:
                os.makedirs(pasta, exist_ok = True)
            with open(self.caminho_historico, "w", encoding = "utf-8") as arquivo:
                json.dump(self.historico, arquivo, ensure_ascii = False, indent = 2)
        except OSError as erro:
            print(f"Aviso: não consegui salvar o histórico ({erro}).")

    def registrar(self, origem, pergunta, orientacao_id, encontrou, ajudou, tentativas, tempo_segundos):
        #Guarda um atendimento e salva o histórico
        atendimento = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "origem": origem,       # pergunta
            "pergunta": pergunta,
            "orientacao_id": orientacao_id,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": tempo_segundos,
        }
        self.historico.append(atendimento)
        self._salvar_historico()

    def perguntar(self):
        # Atende perguntas em texto livre
        print("\n--- Perguntar ---")
        print("Dica: não digite dados pessoais, como CPF, telefone ou e-mail.")
        while self._atender_pergunta():
            pass

    def _atender_pergunta(self):
        # Repete até achar uma orientação ou o usuário voltar (0).
        # Devolve True se terminou ou False se o usuário digitou 0.

        inicio = None
        tentativas = 0
        ultima_pergunta = ""

        while True:
            texto = entrada("\nDigite sua dúvida (0 para voltar): ")

            if texto == "0":
                if tentativas > 0:     # desistiu: registra como não resolvido
                    self.registrar("pergunta", ultima_pergunta, None, False, False, tentativas, round(time.time() - inicio, 1))
                return False
            if texto == "":
                print("Escreva sua dúvida: ")
                continue
            if tem_dado_pessoal(texto):
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva.") # dado pessoal nunca é salvo
                continue

            if inicio is None:
                inicio = time.time()
            tentativas += 1
            ultima_pergunta = texto

            resultados = self.base.buscar(texto)
            melhor_pontos = resultados[0][0] if resultados else 0
            confianca = self.base.nivel_confianca(melhor_pontos)

            if confianca is None:
                self._mostrar_nao_encontrei()
                continue

            tempo = round(time.time() - inicio, 1)
            self._mostrar_resultado(resultados, confianca)
            ajudou = ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")
            self.registrar("pergunta", texto, resultados[0][1].id, True, ajudou, tentativas, tempo)
            return True

    def _mostrar_nao_encontrei(self):
        print("\nNão encontrei uma orientação para essa dúvida.")
        print("Tente outras palavras (por exemplo, o nome do documento) ou use")
        print("a navegação por categorias (opção 2 do menu).")
        print("Categorias disponíveis: " + ", ".join(self.base.categorias()))

    def _mostrar_resultado(self, resultados, confianca):
        melhor_pontos, melhor = resultados[0]
        print(f"\nConfiança da resposta: {confianca} ({melhor_pontos} pontos)")
        melhor.exibir()
        alternativas = [(p, o) for p, o in resultados[1:3] if self.base.nivel_confianca(p) is not None]
        if alternativas:
            print("\nOutras orientações que podem ajudar:")
            for pontos, orientacao in alternativas:
                print(f"  - {orientacao.titulo} ({pontos} pontos)")





    def executar(self):
        #Menu principal.
        print(f"\n=== {self.nome} ===")
        print("Orientação sobre documentos e serviços ao cidadão.")
        print(f"Aviso: {AVISO}")
        print("Nunca peço nome, CPF, telefone ou e-mail. Não os forneça")
        try:
            while True:
                print("\n--- Menu ---")
                print("  1) Perguntar (texto livre)")
                print("  2) Navegar por categorias")
                print("  3) Ver indicadores")
                print("  4) Exportar atendimentos (CSV)")
                print("  0) Sair")
                opcao = ler_opcao("Escolha uma opção: ", 0, 4)
                if opcao == 1:
                    self.perguntar()
                elif opcao == 2:
                    self.navegar()
                elif opcao == 3:
                    self.mostrar_indicadores()
                elif opcao == 4:
                    self.exportar_csv()
                else:
                    break
            self.encerrar()
        except KeyboardInterrupt:
            print("\nEncerrado pelo usuário.")
            self._salvar_historico()
