import random
import unicodedata
import helpers
import requests
import json
import os
import sys

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
