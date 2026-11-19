import random
import unicodedata

class Palavra():
    def __init__(self, arquivo: str, tamanho: int):
        self.arquivo = arquivo
        self.tamanho = tamanho

        self.lista_palavras = self._carregar_palavras()
        self.lista_palavras_sa = [self._tirar_acentos(palavra) for palavra in self.lista_palavras]

    
    def _carregar_palavras(self):
        with open(self.arquivo, "r", encoding="utf-8") as f:
            palavras = f.read().splitlines()
        return [palavra.lower() for palavra in palavras if len(self._tirar_acentos(palavra)) == self.tamanho]


    def _tirar_acentos(self, palavra: str) -> str:
        nfkd = unicodedata.normalize('NFKD', palavra)
        return ''.join([c for c in nfkd if not unicodedata.combining(c)])


    def get_palavra_aleatoria(self) -> str:
        self.palavra_atual = random.choice(self.lista_palavras)
        return self.palavra_atual


    def comparar_palavras(self, alvo: str) -> dict:
        resultado = {}

        palavra_atual = self._tirar_acentos(self.palavra_atual)
        alvo = self._tirar_acentos(alvo)

        letras_restantes = list(palavra_atual)

        for indice, char in enumerate(alvo):
            if char == palavra_atual[indice]:
                resultado[indice] = 2
                letras_restantes[indice] = None
            else:
                resultado[indice] = 0

        for indice, char in enumerate(alvo):
            if resultado[indice] == 0 and char in letras_restantes:
                resultado[indice] = 1
                letras_restantes[letras_restantes.index(char)] = None

        return resultado


    def chute(self, palavra: str) -> dict:
        palavra = palavra.lower()
        if len(self._tirar_acentos(palavra)) != self.tamanho:
            raise ValueError(f"A palavra deve ter {self.tamanho} letras.")

        if self._tirar_acentos(palavra) not in self.lista_palavras_sa:
            raise ValueError("A palavra não está na lista de palavras válidas.")

        return self.comparar_palavras(palavra)


if __name__ == "__main__":
    palavra = Palavra("lista.txt", 5)
    print(palavra.get_palavra_aleatoria())
    print(palavra.chute("lápis"))