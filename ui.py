import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from game import Palavra


class JogoPalavrasUI(QMainWindow):
    CORES_STATUS = {
        2: "#538d4e",  # Verde: letra e posição corretas
        1: "#b59f3b",  # Amarelo: letra existe, posição errada
        0: "#3a3a3c",  # Cinza: letra não existe na palavra
    }

    def __init__(self, arquivo_palavras: str = "lista.txt", max_tentativas: int = 6):
        super().__init__()
        self.arquivo_palavras = arquivo_palavras
        self.max_tentativas = max_tentativas

        self.jogo: Palavra | None = None
        self.tentativa_atual = 0
        self.jogo_encerrado = False
        self.celulas: list[list[QLabel]] = []

        self._configurar_janela()
        self._criar_widgets()
        self.iniciar_novo_jogo()

    def _configurar_janela(self):
        self.setWindowTitle("Jogo de Palavras")
        self.setMinimumSize(460, 620)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121213;
            }
            QLabel {
                color: #ffffff;
            }
            QComboBox, QLineEdit, QPushButton {
                background-color: #272729;
                color: #ffffff;
                border: 1px solid #565758;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3a3a3c;
            }
            QPushButton:disabled, QLineEdit:disabled {
                background-color: #1a1a1b;
                color: #6e6e70;
                border-color: #3a3a3c;
            }
        """)

    def _criar_widgets(self):
        widget_central = QWidget()
        self.setCentralWidget(widget_central)

        self.layout_principal = QVBoxLayout(widget_central)
        self.layout_principal.setSpacing(16)
        self.layout_principal.setContentsMargins(24, 24, 24, 24)

        # Cabeçalho: Título + Seletor de Dificuldade
        layout_topo = QHBoxLayout()

        titulo = QLabel("TERMO")
        titulo.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        layout_topo.addWidget(titulo)

        layout_topo.addStretch()

        lbl_dificuldade = QLabel("Dificuldade:")
        lbl_dificuldade.setFont(QFont("Segoe UI", 11))
        layout_topo.addWidget(lbl_dificuldade)

        self.combo_dificuldade = QComboBox()
        self.combo_dificuldade.addItem("4 letras (Fácil)", 4)
        self.combo_dificuldade.addItem("5 letras (Normal)", 5)
        self.combo_dificuldade.addItem("6 letras (Difícil)", 6)
        self.combo_dificuldade.addItem("7 letras (Mestre)", 7)
        self.combo_dificuldade.setCurrentIndex(1)  # Padrão: 5 letras
        self.combo_dificuldade.currentIndexChanged.connect(self.iniciar_novo_jogo)
        layout_topo.addWidget(self.combo_dificuldade)

        self.btn_novo_jogo = QPushButton("Novo Jogo")
        self.btn_novo_jogo.clicked.connect(self.iniciar_novo_jogo)
        layout_topo.addWidget(self.btn_novo_jogo)

        self.layout_principal.addLayout(layout_topo)

        # Grade de Tentativas
        self.container_grade = QWidget()
        self.layout_grade = QGridLayout(self.container_grade)
        self.layout_grade.setSpacing(8)
        self.layout_grade.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout_principal.addWidget(self.container_grade, stretch=1)

        # Mensagem de status / feedback de erros
        self.lbl_status = QLabel("")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.lbl_status.setMinimumHeight(28)
        self.layout_principal.addWidget(self.lbl_status)

        # Área de entrada do palpite
        layout_entrada = QHBoxLayout()

        self.input_palpite = QLineEdit()
        self.input_palpite.setPlaceholderText("Digite sua palavra...")
        self.input_palpite.setFont(QFont("Segoe UI", 14))
        self.input_palpite.textChanged.connect(self._atualizar_linha_digitacao)
        self.input_palpite.returnPressed.connect(self.enviar_palpite)
        layout_entrada.addWidget(self.input_palpite)

        self.btn_enviar = QPushButton("Chutar")
        self.btn_enviar.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.btn_enviar.clicked.connect(self.enviar_palpite)
        layout_entrada.addWidget(self.btn_enviar)

        self.layout_principal.addLayout(layout_entrada)

    def _construir_grade(self, tamanho_palavra: int):
        # Remove células anteriores ao trocar de dificuldade
        while self.layout_grade.count():
            item = self.layout_grade.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.celulas = []
        tamanho_celula = 58 if tamanho_palavra <= 5 else 48

        for linha in range(self.max_tentativas):
            linha_celulas = []
            for coluna in range(tamanho_palavra):
                celula = QLabel("")
                celula.setFixedSize(tamanho_celula, tamanho_celula)
                celula.setAlignment(Qt.AlignmentFlag.AlignCenter)
                celula.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
                celula.setStyleSheet(self._estilo_celula("#121213", "#3a3a3c"))
                self.layout_grade.addWidget(celula, linha, coluna)
                linha_celulas.append(celula)
            self.celulas.append(linha_celulas)

    @staticmethod
    def _estilo_celula(cor_fundo: str, cor_borda: str) -> str:
        return f"""
            QLabel {{
                background-color: {cor_fundo};
                border: 2px solid {cor_borda};
                border-radius: 6px;
                color: #ffffff;
            }}
        """

    def iniciar_novo_jogo(self):
        tamanho = self.combo_dificuldade.currentData()

        try:
            self.jogo = Palavra(self.arquivo_palavras, tamanho)
            if not self.jogo.lista_palavras:
                raise ValueError(f"Nenhuma palavra com {tamanho} letras encontrada em '{self.arquivo_palavras}'.")
            self.jogo.get_palavra_aleatoria()
        except (FileNotFoundError, ValueError) as erro:
            QMessageBox.critical(self, "Erro ao carregar palavras", str(erro))
            self.input_palpite.setEnabled(False)
            self.btn_enviar.setEnabled(False)
            return

        self.tentativa_atual = 0
        self.jogo_encerrado = False
        self._construir_grade(tamanho)

        self.lbl_status.setText(f"Adivinhe a palavra de {tamanho} letras ({self.max_tentativas} tentativas).")
        self.lbl_status.setStyleSheet("color: #d7dadc;")

        self.input_palpite.clear()
        self.input_palpite.setMaxLength(tamanho)
        self.input_palpite.setEnabled(True)
        self.btn_enviar.setEnabled(True)
        self.input_palpite.setFocus()

    def _atualizar_linha_digitacao(self, texto: str):
        if self.jogo_encerrado or self.jogo is None:
            return

        texto_upper = texto.upper()
        linha = self.celulas[self.tentativa_atual]

        for i, celula in enumerate(linha):
            if i < len(texto_upper):
                celula.setText(texto_upper[i])
                celula.setStyleSheet(self._estilo_celula("#121213", "#818384"))
            else:
                celula.setText("")
                celula.setStyleSheet(self._estilo_celula("#121213", "#3a3a3c"))

    def enviar_palpite(self):
        if self.jogo_encerrado or self.jogo is None:
            return

        palpite = self.input_palpite.text().strip()

        try:
            resultado = self.jogo.chute(palpite)
        except ValueError as erro:
            self.lbl_status.setText(str(erro))
            self.lbl_status.setStyleSheet("color: #ff6b6b;")
            return

        # Pinta as células da tentativa realizada conforme o retorno de chute()
        linha = self.celulas[self.tentativa_atual]
        for indice, status in resultado.items():
            cor = self.CORES_STATUS[status]
            linha[indice].setText(palpite[indice].upper())
            linha[indice].setStyleSheet(self._estilo_celula(cor, cor))

        self.tentativa_atual += 1
        self.input_palpite.clear()

        # Verifica vitória ou fim das tentativas
        if all(status == 2 for status in resultado.values()):
            self.jogo_encerrado = True
            self.lbl_status.setText(f"Parabéns! Você acertou: {self.jogo.palavra_atual.upper()}")
            self.lbl_status.setStyleSheet("color: #6aaa64;")
            self._desabilitar_entrada()
        elif self.tentativa_atual >= self.max_tentativas:
            self.jogo_encerrado = True
            self.lbl_status.setText(f"Fim de jogo! A palavra era: {self.jogo.palavra_atual.upper()}")
            self.lbl_status.setStyleSheet("color: #ff6b6b;")
            self._desabilitar_entrada()
        else:
            restantes = self.max_tentativas - self.tentativa_atual
            self.lbl_status.setText(f"Tentativas restantes: {restantes}")
            self.lbl_status.setStyleSheet("color: #d7dadc;")

    def _desabilitar_entrada(self):
        self.input_palpite.setEnabled(False)
        self.btn_enviar.setEnabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = JogoPalavrasUI(arquivo_palavras="lista.txt", max_tentativas=6)
    janela.show()
    sys.exit(app.exec())
    