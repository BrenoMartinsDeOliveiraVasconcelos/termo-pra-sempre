# Termo pra Sempre

Jogo de palavras para desktop inspirado no Wordle, sem limite diário.

## Instalação e execução

Necessário Python 3.10 ou superior e acesso ao comando pip. Instale os modulos especificados em requirements.txt

## Como jogar

1. Escolha o tamanho da palavra no controle **Letras**. O jogo começa com cinco letras e permite selecionar de 1 a 19.
2. Digite uma palavra do tamanho indicado e pressione **Enter** ou clique em **Chutar**. O jogo ignora acentos e diferenças entre maiúsculas e minúsculas. Palpites inválidos não consomem tentativas.
3. Use as cores da grade para orientar o próximo palpite.

| Cor | Significado |
| --- | --- |
| Verde | A letra está na posição certa. |
| Amarelo | A letra aparece na palavra, mas em outra posição. |
| Cinza | A letra não aparece na palavra ou suas ocorrências já foram marcadas em outras posições do palpite. |

A palavra secreta é revelada ao vencer ou esgotar as tentativas. Clique em **Novo Jogo** para iniciar outra partida. O placar acumula pontos, vitórias e derrotas enquanto o aplicativo estiver aberto.

## Estrutura do projeto

| Arquivo | Função |
| --- | --- |
| `ui.py` | Abre a janela e controla a grade, a entrada de palpites e o placar. |
| `game.py` | Sorteia palavras, valida palpites, compara letras e calcula a pontuação. |
| `helpers.py` | Consulta a API do Dicionário Aberto e carrega os arquivos do tema. |
| `lista.txt` | Contém as palavras usadas para o sorteio e a validação de palpites, uma por linha em UTF-8. |
| `theme/style.css` e `theme/status.json` | Definem o estilo da janela e as cores da grade. |
| `requirements.txt` | Lista as dependências PySide6 e Requests. |

Ao sortear uma palavra, o jogo usa o Dicionário Aberto para verificar se ela é um substantivo. O arquivo `cache.json` é criado automaticamente e guarda os resultados dessas consultas para partidas futuras.


## Disclaimer de uso de IA

Foi ultilizado IA generativa em tarefas como autocomplete, organização de código escrito a mão, automatização de código repetitivo e ajuda na escrita da documentação. A idealização do jogo e a lógica interna foi feita puramente por seres humanos.