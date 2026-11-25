import random
import unicodedata
import helpers
import requests
import json
import os
import sys
from dataclasses import dataclass

class Palavra():
    def __init__(self, arquivo: str, cache: str, tamanho: int):
        self.arquivo = arquivo
        self.cache = cache
        self.tamanho = tamanho

        self.lista_palavras = self._carregar_palavras()
        self.lista_palavras_sa = [self._tirar_acentos(palavra) for palavra in self.lista_palavras]

        print(sys.getsizeof(self.lista_palavras), sys.getsizeof(self.lista_palavras_sa))

        self._gerar_cache()

        

    
    def _carregar_palavras(self):
        lista = open(self.arquivo, "r", encoding="utf-8").read().splitlines()
        l_palavras = [palavra.lower() for palavra in lista if len(self._tirar_acentos(palavra)) == self.tamanho]
        print(f"Numero total: {len(l_palavras)}")

        return l_palavras


    def _tirar_acentos(self, palavra: str) -> str:
        nfkd = unicodedata.normalize('NFKD', palavra)
        return ''.join([c for c in nfkd if not unicodedata.combining(c)])


    def _gerar_cache(self):
        if not os.path.exists(self.cache):
            with open(self.cache, "w+", encoding="utf-8") as f:
                json.dump({}, f)


    def _atualizar_cache(self, palavra: str, is_substantivo: bool):
        with open(self.cache, "r+", encoding="utf-8") as f:
            cache_data = json.load(f)
            cache_data[palavra] = is_substantivo
            f.seek(0)
            json.dump(cache_data, f, ensure_ascii=False, indent=4)
            f.truncate()


    def _verificar_cache(self, palavra: str) -> bool | None:
        cache = json.load(open(self.cache, "r", encoding="utf-8"))

        return cache.get(palavra, None)
        

    def get_palavra_aleatoria(self, tentativa: int=1) -> str:
        print(f"Tentativa #{tentativa} de sortear palavra...")
        self.palavra_atual = random.choice(self.lista_palavras)

        try:
            if self._verificar_cache(self.palavra_atual) is not None:
                print("Encontrado no cache... ", end="")
                is_substantivo = self._verificar_cache(self.palavra_atual)
                if not is_substantivo:
                    print("Inválido.")
                    return self.get_palavra_aleatoria(tentativa=tentativa+1)
                else:
                    print("Válido.")
            else:
                print("Não encontrado no cache. Checando na API...", end="")
                req = helpers.request(self.palavra_atual)
                xml_list = helpers.get_xml_camp(req)

                if not any(helpers.is_substantivo(xml) for xml in xml_list):
                    self._atualizar_cache(self.palavra_atual, False)
                    print("Inválido.")
                    return self.get_palavra_aleatoria(tentativa=tentativa+1)
                else:
                    print("Válido.")
                    self._atualizar_cache(self.palavra_atual, True)
        except (ConnectionError, requests.exceptions.RequestException):
            print("Erro de conexão. Continuando com a palavra selecionada.")  # Se houver um erro de conexão, apenas continue com a palavra selecionada

        print("Palavra sorteada com sucesso!")
        return self.palavra_atual


    def comparar_palavras(self, alvo: str) -> dict:
        resultado = {}

        palavra_atual = self._tirar_acentos(self.palavra_atual)
        alvo = self._tirar_acentos(alvo)

        letras_restantes = [x for x in palavra_atual]

        for indice, char in enumerate(alvo):
            if char == palavra_atual[indice]:
                resultado[indice] = 2
                letras_restantes[indice] = ""
            else:
                resultado[indice] = 0

        for indice, char in enumerate(alvo):
            if resultado[indice] == 0 and char in letras_restantes:
                resultado[indice] = 1
                letras_restantes[letras_restantes.index(char)] = ""

        return resultado


    def chute(self, palavra: str) -> dict:
        palavra = palavra.lower()
        print(palavra, self._tirar_acentos(palavra), palavra in self.lista_palavras_sa, palavra in self.lista_palavras, palavra in self.lista_palavras_sa)
        if len(self._tirar_acentos(palavra)) != self.tamanho:
            raise ValueError(f"A palavra deve ter {self.tamanho} letras.")

        if self._tirar_acentos(palavra) not in self.lista_palavras_sa:
            raise ValueError("A palavra não está na lista de palavras válidas.")

        return self.comparar_palavras(palavra)


@dataclass(frozen=True)
class ResultadoPalpite:
    linha: int
    palpite: str
    status_letras: dict[int, int]
    restantes: int
    vitoria: bool
    palavra_revelada: str | None


class GameManager:
    def __init__(
        self,
        arquivo_palavras: str = "lista.txt",
        arquivo_cache: str = "cache.json",
        max_tentativas: int = 6,
    ):
        if max_tentativas < 1:
            raise ValueError("O jogo precisa permitir pelo menos uma tentativa.")

        self.arquivo_palavras = arquivo_palavras
        self.arquivo_cache = arquivo_cache
        self.max_tentativas = max_tentativas
        self.pontos = 0
        self.vitorias = 0
        self.derrotas = 0
        self.tentativa_atual = 0
        self._restantes_nas_vitorias: list[int] = []
        self._pontos_rodada = 0.0
        self._palavra: Palavra | None = None
        self._encerrado = False

    @property
    def aceita_palpites(self) -> bool:
        return self._palavra is not None and not self._encerrado

    @property
    def razao_vitorias_derrotas(self) -> float:
        return self.vitorias / self.derrotas if self.derrotas else float(self.vitorias)

    def iniciar_novo_jogo(self, tamanho: int):
        self._palavra = None
        self.tentativa_atual = 0
        self._encerrado = False
        self._pontos_rodada = 0.0

        palavra = Palavra(self.arquivo_palavras, self.arquivo_cache, tamanho)
        if not palavra.lista_palavras:
            raise ValueError(
                f"Nenhuma palavra com {tamanho} letras encontrada em '{self.arquivo_palavras}'."
            )
        palavra.get_palavra_aleatoria()
        self._palavra = palavra

    def enviar_palpite(self, texto: str) -> ResultadoPalpite:
        palavra = self._palavra
        if palavra is None or self._encerrado:
            raise ValueError("Não há uma partida em andamento.")

        palpite = texto.strip()
        status_letras = palavra.chute(palpite)
        linha = self.tentativa_atual
        self.tentativa_atual += 1
        restantes = self.max_tentativas - self.tentativa_atual
        vitoria = all(status == 2 for status in status_letras.values())
        derrota = restantes == 0 and not vitoria
        self._encerrado = vitoria or derrota

        self._pontuar(status_letras, vitoria, derrota)
        if vitoria:
            self._restantes_nas_vitorias.append(restantes)
            self.vitorias += 1
        elif derrota:
            self.derrotas += 1

        return ResultadoPalpite(
            linha=linha,
            palpite=palpite,
            status_letras=status_letras,
            restantes=restantes,
            vitoria=vitoria,
            palavra_revelada=palavra.palavra_atual if self._encerrado else None,
        )

    def _pontuar(self, status_letras: dict[int, int], vitoria: bool, derrota: bool):
        historico = self._restantes_nas_vitorias
        media_restantes = round(sum(historico) / len(historico)) if historico else 1
        pontos = 8 ** media_restantes
        peso_tentativa = self.max_tentativas / self.tentativa_atual
        for status in status_letras.values():
            pontos += 2 * status * peso_tentativa
        if vitoria:
            pontos = pontos + (self.pontos + self.pontos / 2) - self.pontos
        if not any(status_letras.values()):
            pontos = 0

        self._pontos_rodada += pontos
        self.pontos += round(pontos)
        if derrota:
            self.pontos = round(self.pontos - self._pontos_rodada)
