import sys
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QComboBox, QFileDialog, QMessageBox
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
import os

# Lista de disciplinas com códigos
disciplinas = {
    "A FORMAÇÃO DA INTELIGÊNCIA, DA VONTADE E DA MEMÓRIA": 1982,
    "A LITERATURA E A FORMAÇÃO DO IMAGINÁRIO": 1985,
    "ANTROPOLOGIA FILOSÓFICA": 1986,
    "AS ARTES LIBERAIS DO TRIVIUM E DO QUADRIVIUM": 1983,
    "EDUCAÇÃO CLÁSSICA E EDUCAÇÃO MODERNA": 1987,
    "FILOSOFIA ESPECULATIVA": 1980,
    "METODOLOGIA DA PESQUISA": 1988,
    "MORAL DAS VIRTUDES": 1981,
    "RATIO STUDIORUM": 1984,
    "SEMINÁRIO DE PESQUISA": 1989,
}

# Estilo CSS para a interface
STYLE_SHEET = """
    QMainWindow {
        background-color: #2E3440;
    }
    QLabel {
        color: #ECEFF4;
        font-size: 14px;
    }
    QComboBox {
        background-color: #4C566A;
        color: #ECEFF4;
        border: 1px solid #81A1C1;
        border-radius: 5px;
        padding: 5px;
    }
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 20px;
        border-left: 1px solid #81A1C1;
    }
    QPushButton {
        background-color: #88C0D0;
        color: #2E3440;
        border: none;
        border-radius: 5px;
        padding: 10px;
        font-size: 14px;
    }
    QPushButton:hover {
        background-color: #81A1C1;
    }
    QTextEdit {
        background-color: #4C566A;
        color: #ECEFF4;
        border: 1px solid #81A1C1;
        border-radius: 5px;
        padding: 10px;
        font-size: 14px;
    }
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerador de Notas")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet(STYLE_SHEET)  # Aplicar o estilo CSS

        # Layout principal
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # Título
        self.title_label = QLabel("Gerador de Notas - PSI ODT")
        self.title_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Seleção de disciplina
        self.disciplina_label = QLabel("Selecione a Disciplina:")
        self.disciplina_label.setFont(QFont("Arial", 12))
        self.layout.addWidget(self.disciplina_label)
        self.combo_disciplina = QComboBox()
        self.combo_disciplina.addItems(disciplinas.keys())
        self.combo_disciplina.setFont(QFont("Arial", 12))
        self.layout.addWidget(self.combo_disciplina)

        # Seleção de tipo de avaliação
        self.tipo_avaliacao_label = QLabel("Tipo de Avaliação:")
        self.tipo_avaliacao_label.setFont(QFont("Arial", 12))
        self.layout.addWidget(self.tipo_avaliacao_label)
        self.combo_tipo_avaliacao = QComboBox()
        self.combo_tipo_avaliacao.addItems(["AVP", "REC"])
        self.combo_tipo_avaliacao.setFont(QFont("Arial", 12))
        self.layout.addWidget(self.combo_tipo_avaliacao)

        # Botões
        self.button_layout = QHBoxLayout()
        self.btn_selecionar_planilha = QPushButton("Escolher Planilha Com As Notas Do MOODLE")
        self.btn_selecionar_planilha.setIcon(QIcon("folder.png"))  # Ícone para o botão
        self.btn_selecionar_planilha.clicked.connect(self.selecionar_planilha_2)
        self.button_layout.addWidget(self.btn_selecionar_planilha)

        self.btn_salvar_arquivos = QPushButton("Salvar Arquivos")
        self.btn_salvar_arquivos.setIcon(QIcon("save.png"))  # Ícone para o botão
        self.btn_salvar_arquivos.clicked.connect(self.salvar_arquivos)
        self.button_layout.addWidget(self.btn_salvar_arquivos)
        self.layout.addLayout(self.button_layout)

        # Caixas de texto
        self.text_layout = QHBoxLayout()
        self.textbox_avaliacao = QTextEdit()
        self.textbox_avaliacao.setPlaceholderText("Avaliação")
        self.text_layout.addWidget(self.textbox_avaliacao)

        self.textbox_1tb = QTextEdit()
        self.textbox_1tb.setPlaceholderText("1 TB")
        self.text_layout.addWidget(self.textbox_1tb)

        self.textbox_2tb = QTextEdit()
        self.textbox_2tb.setPlaceholderText("2 TB")
        self.text_layout.addWidget(self.textbox_2tb)

        self.textbox_vda = QTextEdit()
        self.textbox_vda.setPlaceholderText("VDA")
        self.text_layout.addWidget(self.textbox_vda)
        self.layout.addLayout(self.text_layout)

        # Consulta SQL e geração do DataFrame com os dados dos alunos
        self.consultar_sql_e_gerar_dataframe()

    def consultar_sql_e_gerar_dataframe(self):
        host, user, password, database = '192.168.7.7', 'relatorio', 'Tekalpha#72!', 'seibd'
        sql = "SELECT DISTINCT name AS nome, matricula AS matrícula FROM public.mdl_enrol WHERE role = 'student'"
        engine = create_engine(f'postgresql://{user}:{password}@{host}/{database}')
        Session = sessionmaker(bind=engine)  # Criando a fábrica de sessões
        session = Session()  # Criando uma sessão
        result = session.execute(text(sql))
        dados = result.fetchall()
        session.close()
        self.df_alunos = pd.DataFrame(dados, columns=['Nome', 'Matrícula'])

    def selecionar_planilha_2(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecione a segunda planilha", "", "Planilhas (*.xlsx *.csv)")
        if file_path:
            try:
                self.gerar_arquivo_txt(file_path)
                self.comparar_e_exibir_matriculas()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Ocorreu um erro: {str(e)}")

    def calcular_valores(self):
        # Limpar valores não numéricos (como vírgulas) e converter para float
        self.merged_df['Avaliação'] = self.merged_df['Avaliação'].replace(',', '.', regex=True).astype(float)

        # Definindo as condições para 1TB, 2TB e VDA
        conditions = [
            (self.merged_df['Avaliação'] == 100.0),
            (self.merged_df['Avaliação'] == 90.0),
            (self.merged_df['Avaliação'] == 80.0),
            (self.merged_df['Avaliação'] == 70.0),
            (self.merged_df['Avaliação'] == 60.0),
            (self.merged_df['Avaliação'] == 50.0),
            (self.merged_df['Avaliação'] == 40.0),
            (self.merged_df['Avaliação'] == 30.0),
            (self.merged_df['Avaliação'] == 20.0),
            (self.merged_df['Avaliação'] == 10.0),
            (self.merged_df['Avaliação'] == 0.0)
        ]

        values_1tb = [20, 20, 10, 10, 10, 10, 10, 10, 0, 0, 0]
        values_2tb = [20, 10, 10, 10, 10, 10, 10, 10, 10, 0, 0]
        values_vda = [60, 60, 60, 50, 40, 30, 20, 10, 10, 10, 0]

        self.merged_df['1 TB'] = np.select(conditions, values_1tb, default=0)
        self.merged_df['2 TB'] = np.select(conditions, values_2tb, default=0)
        self.merged_df['VDA'] = np.select(conditions, values_vda, default=0)

    def comparar_e_exibir_matriculas(self):
        # Limpar caixas de texto antes de exibir novos resultados
        self.textbox_avaliacao.clear()
        self.textbox_1tb.clear()
        self.textbox_2tb.clear()
        self.textbox_vda.clear()

        self.calcular_valores()

        # Adicionar o valor completo da coluna Avaliação
        for _, row in self.merged_df.iterrows():
            matricula = row['Matrícula']
            codigo = row['Código']
            avaliacao = row['Avaliação']

            # Inserir o valor completo da avaliação na nova caixa de texto
            self.textbox_avaliacao.append(f"{matricula};{codigo};{avaliacao}")

            # Inserir os resultados nas respectivas caixas de texto
            self.textbox_1tb.append(f"{matricula};{codigo};{row['1 TB']}")
            self.textbox_2tb.append(f"{matricula};{codigo};{row['2 TB']}")
            self.textbox_vda.append(f"{matricula};{codigo};{row['VDA']}")

    def gerar_arquivo_txt(self, planilha2):
        file_extension = os.path.splitext(planilha2)[1].lower()
        if file_extension == ".xlsx":
            df2 = pd.read_excel(planilha2)
        elif file_extension == ".csv":
            df2 = pd.read_csv(planilha2)
        else:
            raise ValueError("Formato de arquivo não suportado. Por favor, selecione um arquivo XLSX ou CSV.")

        # Ajuste para garantir que a coluna de avaliação seja renomeada corretamente
        avaliacao_column = "Avaliar/100,00"

        if "Nome" not in df2.columns:
            if "Aluno" in df2.columns:
                df2.rename(columns={"Aluno": "Nome"}, inplace=True)
            else:
                df2.rename(columns={df2.columns[0]: "Nome"}, inplace=True)

        if "Sobrenome" in df2.columns:
            df2["Nome Completo"] = df2["Nome"] + " " + df2["Sobrenome"]
            df2.drop(columns=["Nome", "Sobrenome"], inplace=True)
        else:
            if "Aluno" in df2.columns:
                df2.rename(columns={"Aluno": "Nome Completo"}, inplace=True)
            else:
                df2.rename(columns={df2.columns[0]: "Nome Completo"}, inplace=True)

        if avaliacao_column in df2.columns:
            df2.rename(columns={avaliacao_column: 'Avaliação'}, inplace=True)
        else:
            raise ValueError("Coluna de avaliação não encontrada na planilha.")

        self.merged_df = pd.merge(self.df_alunos, df2, left_on='Nome', right_on='Nome Completo', how='inner')
        disciplina_escolhida = self.combo_disciplina.currentText()
        codigo_escolhido = disciplinas.get(disciplina_escolhida, "Código Não Especificado")
        self.merged_df['Código'] = codigo_escolhido
        self.merged_df = self.merged_df[['Matrícula', 'Código', 'Avaliação']]

    def salvar_arquivos(self):
        disciplina_escolhida = self.combo_disciplina.currentText()
        tipo_avaliacao = self.combo_tipo_avaliacao.currentText()
        folder_path = os.path.join(os.path.expanduser('~/Desktop/Notas PSI ODT'), disciplina_escolhida)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        if tipo_avaliacao == "AVP":
            # Salvar as colunas 1 TB, 2 TB e VDA em arquivos separados
            self.salvar_Nota_txt(folder_path, '1 TB', '1 TB.txt')
            self.salvar_Nota_txt(folder_path, '2 TB', '2 TB.txt')
            self.salvar_Nota_txt(folder_path, 'VDA', 'VDA.txt')
        elif tipo_avaliacao == "REC":
            # Salvar apenas a coluna Avaliação com o nome REC.txt
            self.salvar_Nota_txt(folder_path, 'Avaliação', 'REC.txt')

        # Mostrar aviso de sucesso
        QMessageBox.information(self, "Sucesso", "Arquivos salvos com sucesso!")

    def salvar_Nota_txt(self, folder_path, nota_type, file_name):
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'w') as f:
            f.write(" ; ;\n")
            for _, row in self.merged_df.iterrows():
                f.write(f"{row['Matrícula']};{row['Código']};{row[nota_type]}\n")

# Executar a aplicação
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())