import sys
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from game import GameManager
from helpers import load_css, load_json

class JogoPalavrasUI(QMainWindow):
    CORES_STATUS = load_json("theme/status.json")

    def __init__(self, arquivo_palavras: str = "lista.txt", max_tentativas: int = 6):
        super().__init__()
        self.titulo = "Termo"
        self.game = GameManager(
            arquivo_palavras=arquivo_palavras, max_tentativas=max_tentativas
        )
        self.celulas: list[list[QLabel]] = []

        self._configurar_janela()
        self._criar_widgets()
        self.iniciar_novo_jogo()

    def _configurar_janela(self):
        self.setWindowTitle(self.titulo)
        self.setStyleSheet(load_css("theme/style.css"))

    def _ajustar_janela(self):
        self.layout_principal.activate()
        self.adjustSize()

    def _criar_widgets(self):
        widget_central = QWidget()
        self.setCentralWidget(widget_central)

        self.layout_principal = QVBoxLayout(widget_central)
        self.layout_principal.setSpacing(16)
        self.layout_principal.setContentsMargins(24, 24, 24, 24)

        # Cabeçalho: Título + Barra de Rolagem de Dificuldade
        layout_topo = QHBoxLayout()

        titulo = QLabel("TERMO")
        titulo.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        layout_topo.addWidget(titulo)

        layout_topo.addStretch()

        lbl_dificuldade = QLabel("Letras:")
        lbl_dificuldade.setFont(QFont("Segoe UI", 11))
        layout_topo.addWidget(lbl_dificuldade)

        self.slider_dificuldade = QSlider(Qt.Orientation.Horizontal)
        self.slider_dificuldade.setRange(1, 19)
        self.slider_dificuldade.setValue(5)  # Padrão: 5 letras
        self.slider_dificuldade.setFixedWidth(120)
        self.slider_dificuldade.valueChanged.connect(self._ao_mover_slider)
        self.slider_dificuldade.sliderReleased.connect(self.iniciar_novo_jogo)
        layout_topo.addWidget(self.slider_dificuldade)

        self.lbl_valor_letras = QLabel("5")
        self.lbl_valor_letras.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.lbl_valor_letras.setFixedWidth(22)
        self.lbl_valor_letras.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_topo.addWidget(self.lbl_valor_letras)

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

        # Pontuação
        self.point_label = QLabel("")
        self.point_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.point_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Normal))
        self.point_label.setMinimumHeight(28)
        self.layout_principal.addWidget(self.point_label)
        self._atualizar_placar()

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

    def _ao_mover_slider(self, valor: int):
        self.lbl_valor_letras.setText(str(valor))
        # Se mudou por clique direto na trilha ou teclas de seta (sem arrastar), inicia na hora
        if not self.slider_dificuldade.isSliderDown():
            self.iniciar_novo_jogo()

    def _atualizar_placar(self):
        self.point_label.setText(
            f"Pontos: {self.game.pontos} ({self.game.vitorias}/{self.game.derrotas}) "
            f"(Ratio: {self.game.razao_vitorias_derrotas:.2f})"
        )

    def _construir_grade(self, tamanho_palavra: int):
        while self.layout_grade.count():
            item = self.layout_grade.takeAt(0)
            widget = item.widget()
            if widget:
                widget.hide()
                widget.setParent(None)
                widget.deleteLater()

        self.celulas = []

        tela = self.screen() or QApplication.primaryScreen()
        largura_tela = int(tela.availableGeometry().width() * 0.85)

        espacamento = self.layout_grade.spacing()  # 8px
        margens_laterais = 48  # 24px de cada lado
        espaco_util = largura_tela - margens_laterais - (espacamento * (tamanho_palavra - 1))

        tamanho_ideal = 58 if tamanho_palavra <= 5 else 48
        tamanho_celula = max(26, min(tamanho_ideal, espaco_util // tamanho_palavra))
        tamanho_fonte = max(11, min(18, int(tamanho_celula * 0.38)))

        for linha in range(self.game.max_tentativas):
            linha_celulas = []
            for coluna in range(tamanho_palavra):
                celula = QLabel("")
                celula.setFixedSize(tamanho_celula, tamanho_celula)
                celula.setAlignment(Qt.AlignmentFlag.AlignCenter)
                celula.setFont(QFont("Segoe UI", tamanho_fonte, QFont.Weight.Bold))
                celula.setStyleSheet(self._estilo_celula("#121213", "#3a3a3c"))
                self.layout_grade.addWidget(celula, linha, coluna)
                linha_celulas.append(celula)
            self.celulas.append(linha_celulas)

    def iniciar_novo_jogo(self):
        texto_original = "Novo Jogo"
        self.btn_novo_jogo.setEnabled(False)
        self.slider_dificuldade.setEnabled(False)
        self.btn_novo_jogo.setText("Aguarde")
        QApplication.processEvents()  # Força a atualização visual antes do carregamento

        tamanho = self.slider_dificuldade.value()

        try:
            self.game.iniciar_novo_jogo(tamanho)
            self._construir_grade(tamanho)

            self.lbl_status.setText(f"Adivinhe a palavra de {tamanho} letras ({self.game.max_tentativas} tentativas).")
            self.lbl_status.setStyleSheet("color: #d7dadc;")

            self.input_palpite.clear()
            self.input_palpite.setMaxLength(tamanho)
            self.input_palpite.setEnabled(True)
            self.btn_enviar.setEnabled(True)
            self.input_palpite.setFocus()

        except (FileNotFoundError, ValueError) as erro:
            QMessageBox.critical(self, "Erro ao carregar palavras", str(erro))
            self.input_palpite.setEnabled(False)
            self.btn_enviar.setEnabled(False)

        finally:
            self.btn_novo_jogo.setEnabled(True)
            self.slider_dificuldade.setEnabled(True)
            self.btn_novo_jogo.setText(texto_original)

        QTimer.singleShot(0, self._ajustar_janela)

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

    def _atualizar_linha_digitacao(self, texto: str):
        if not self.game.aceita_palpites:
            return

        texto_upper = texto.upper()
        linha = self.celulas[self.game.tentativa_atual]

        for i, celula in enumerate(linha):
            if i < len(texto_upper):
                celula.setText(texto_upper[i])
                celula.setStyleSheet(self._estilo_celula("#121213", "#818384"))
            else:
                celula.setText("")
                celula.setStyleSheet(self._estilo_celula("#121213", "#3a3a3c"))

    def enviar_palpite(self):
        if not self.game.aceita_palpites:
            return

        try:
            resultado = self.game.enviar_palpite(self.input_palpite.text())
        except ValueError as erro:
            self.lbl_status.setText(str(erro))
            self.lbl_status.setStyleSheet("color: #ff6b6b;")
            return

        linha = self.celulas[resultado.linha]
        for indice, status in resultado.status_letras.items():
            cor = self.CORES_STATUS[str(status)]
            linha[indice].setText(resultado.palpite[indice].upper())
            linha[indice].setStyleSheet(self._estilo_celula(cor, cor))

        self.input_palpite.clear()
        self._atualizar_placar()

        if resultado.palavra_revelada is None:
            self.lbl_status.setText(f"Tentativas restantes: {resultado.restantes}")
            self.lbl_status.setStyleSheet("color: #d7dadc;")
            return

        palavra = resultado.palavra_revelada.upper()
        if resultado.vitoria:
            self.lbl_status.setText(f"Parabéns! Você acertou: {palavra}")
            self.lbl_status.setStyleSheet("color: #6aaa64;")
        else:
            self.lbl_status.setText(f"Fim de jogo! A palavra era: {palavra}")
            self.lbl_status.setStyleSheet("color: #ff6b6b;")
        self._desabilitar_entrada()

    def _desabilitar_entrada(self):
        self.input_palpite.setEnabled(False)
        self.btn_enviar.setEnabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = JogoPalavrasUI(arquivo_palavras="lista.txt", max_tentativas=6)
    janela.show()
    sys.exit(app.exec())