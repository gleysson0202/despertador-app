from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QComboBox, QMessageBox, QFileDialog, QLineEdit, QLabel
import os
import sys

# Lista de disciplinas com códigos
disciplinas = {
    "PSICOLOGIA E MEIO AMBIENTE PSI": 2249,

}

class GUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gerador de Notas")
        self.resize(800, 600)

        # Variável para controlar o estado (se o texto está exibido ou oculto)
        self.texto_exibido = False

        # Layout principal
        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()  # Usar QHBoxLayout para alinhar botões lado a lado
        content_layout = QVBoxLayout()

        # Barra de pesquisa
        self.label_pesquisa = QLabel("Pesquisar Aluno ou Matrícula:", self)
        self.search_bar = QLineEdit(self)
        self.btn_pesquisar = QPushButton("Pesquisar", self)

        # OptionMenu para escolher a disciplina (QComboBox em PyQt5)
        self.combo_disciplina = QComboBox(self)
        self.combo_disciplina.addItems(disciplinas.keys())

        # Botões
        self.btn_selecionar_planilha = QPushButton("Escolher Planilha Com As Notas Do MOODLE", self)
        self.btn_salvar_arquivos = QPushButton("Salvar Arquivos", self)
        self.btn_exibir_nome_matricula = QPushButton("Exibir Nome;Matrícula", self)  # Novo botão

        # Adicionando widgets ao layout dos botões
        button_layout.addWidget(self.label_pesquisa)
        button_layout.addWidget(self.search_bar)
        button_layout.addWidget(self.btn_pesquisar)
        button_layout.addWidget(self.combo_disciplina)
        button_layout.addWidget(self.btn_exibir_nome_matricula)  # Novo botão
        button_layout.addWidget(self.btn_selecionar_planilha)
        button_layout.addWidget(self.btn_salvar_arquivos)

        # Caixas de texto
        self.textbox_sql = QTextEdit(self)
        self.textbox_sql.setVisible(False)  # Ocultar inicialmente
        self.textbox_planilha2 = QTextEdit(self)

        # Adicionando widgets ao layout de conteúdo
        content_layout.addWidget(self.textbox_sql)
        content_layout.addWidget(self.textbox_planilha2)

        # Adicionando layouts ao layout principal
        main_layout.addLayout(button_layout)
        main_layout.addLayout(content_layout)

        # Configurando o container central
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Conectando botões aos métodos
        self.btn_selecionar_planilha.clicked.connect(self.selecionar_planilha_2)
        self.btn_salvar_arquivos.clicked.connect(self.salvar_arquivos)
        self.btn_exibir_nome_matricula.clicked.connect(self.alternar_nome_matricula)  # Conectando o novo botão
        self.btn_pesquisar.clicked.connect(self.pesquisar_aluno)  # Conectando o botão de pesquisa

        # Consulta SQL e geração do DataFrame com os dados dos alunos
        self.consultar_sql_e_gerar_dataframe()

    def consultar_sql_e_gerar_dataframe(self):
        host, user, password, database = '192.168.7.7', 'relatorio', 'Tekalpha#72!', 'seibd'
        sql = "SELECT DISTINCT name AS nome, matricula AS matrícula FROM public.mdl_enrol WHERE role = 'student'"
        engine = create_engine(f'postgresql://{user}:{password}@{host}/{database}')
        Session = sessionmaker(bind=engine)
        session = Session()
        result = session.execute(text(sql))
        dados = result.fetchall()
        session.close()
        self.df_alunos = pd.DataFrame(dados, columns=['Nome', 'Matrícula'])

    def alternar_nome_matricula(self):
        if self.texto_exibido:
            self.ocultar_nome_matricula()  # Oculta o texto se estiver visível
        else:
            self.exibir_nome_matricula()  # Exibe o texto se estiver oculto

        self.texto_exibido = not self.texto_exibido  # Alterna o estado

    def exibir_nome_matricula(self):
        # Exibe o conteúdo de "Nome;Matrícula" no textbox_sql
        self.textbox_sql.setVisible(True)  # Tornar visível ao exibir o texto
        self.textbox_sql.clear()  # Limpa o conteúdo atual da caixa de texto
        self.textbox_sql.setText("Nome;Matrícula\n")
        for index, row in self.df_alunos.iterrows():
            self.textbox_sql.append(f"{row['Nome']};{row['Matrícula']}")
        self.btn_exibir_nome_matricula.setText("Ocultar Nome;Matrícula")  # Atualiza o texto do botão

    def ocultar_nome_matricula(self):
        # Oculta a caixa de texto
        self.textbox_sql.setVisible(False)
        self.btn_exibir_nome_matricula.setText("Exibir Nome;Matrícula")  # Atualiza o texto do botão

    def selecionar_planilha_2(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecione a segunda planilha", "", "Arquivos XLSX (*.xlsx);;Arquivos CSV (*.csv)", options=options)
        if file_path:
            self.textbox_planilha2.append(f"Planilha 2 selecionada: {file_path}")
            try:
                self.gerar_arquivo_txt(file_path)
                self.textbox_planilha2.append(f"\nArquivo gerado com sucesso.\n")
                self.comparar_e_exibir_matriculas()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Ocorreu um erro: {str(e)}")

    def comparar_e_exibir_matriculas(self):
        for line in self.textbox_planilha2.toPlainText().splitlines():
            try:
                nome, avaliacao = line.split(";")
                nome_busca = nome.split()[0]
                sobrenome = nome.split()[-1]
                matricula = next((row.Matrícula for row in self.df_alunos.itertuples() if (row.Nome.startswith(nome_busca) or row.Nome == nome) and row.Nome.endswith(sobrenome)), "")
                print(f"{nome};{matricula};{avaliacao}\n")
            except ValueError:
                print("Erro ao processar a linha:", line)

    def gerar_arquivo_txt(self, planilha2):
        file_extension = os.path.splitext(planilha2)[1].lower()
        if file_extension == ".xlsx":
            df2 = pd.read_excel(planilha2)
        elif file_extension == ".csv":
            df2 = pd.read_csv(planilha2)
            if not any(df2.columns.str.lower() == 'média') and not any(df2.columns.str.contains('Avaliar/20,00', case=False)) and not any(df2.columns.str.contains('Avaliar/100,00', case=False)):
                df2 = pd.read_csv(planilha2, header=None, names=['Nome', 'Sobrenome', 'Matrícula', 'Média'])
        else:
            raise ValueError("Formato de arquivo não suportado. Por favor, selecione um arquivo XLSX ou CSV.")

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

        if "Média" in df2.columns:
            avaliacao_column = "Média"
        elif any(df2.columns.str.contains('Avaliar/20,00', case=False)):
            avaliacao_column = df2.columns[df2.columns.str.contains('Avaliar/20,00', case=False)].tolist()[0]
        elif any(df2.columns.str.contains('Avaliar/100,00', case=False)):
            avaliacao_column = df2.columns[df2.columns.str.contains('Avaliar/100,00', case=False)].tolist()[0]
        else:
            raise ValueError("Coluna de avaliação (Média/Avaliar/20,00/Avaliar/100,00) não encontrada na quarta posição da planilha.")

        self.merged_df = pd.merge(self.df_alunos, df2, left_on='Nome', right_on='Nome Completo', how='inner')
        disciplina_escolhida = self.combo_disciplina.currentText()
        codigo_escolhido = disciplinas.get(disciplina_escolhida, "Código Não Especificado")
        self.merged_df['Código'] = codigo_escolhido
        self.merged_df.rename(columns={avaliacao_column: 'Avaliação'}, inplace=True)
        self.merged_df = self.merged_df[['Matrícula', 'Código', 'Avaliação']]

        self.textbox_planilha2.append("\nResultados:\n")
        self.textbox_planilha2.append(self.merged_df.to_string(index=False) + "\n")

    def salvar_arquivos(self):
        disciplina_escolhida = self.combo_disciplina.currentText()
        txt_file_path = f"Nota_{disciplina_escolhida}.txt"

        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        folder_path = os.path.join(desktop_path, 'Notas PSI ODT')
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        txt_file_path = os.path.join(folder_path, txt_file_path)
        with open(txt_file_path, 'w') as f:
            f.write(" ; ;\n")
            for index, row in self.merged_df.iterrows():
                f.write(f"{row['Matrícula']};{row['Código']};{row['Avaliação']}\n")
        QMessageBox.information(self, "Salvo", "Arquivo TXT gerado com sucesso!")

    def pesquisar_aluno(self):
        termo_pesquisa = self.search_bar.text().strip().lower()
        if not termo_pesquisa:
            QMessageBox.warning(self, "Aviso", "Por favor, insira um termo de pesquisa.")
            return

        resultados = self.df_alunos[self.df_alunos.apply(lambda row: termo_pesquisa in row['Nome'].lower() or termo_pesquisa in str(row['Matrícula']), axis=1)]

        if resultados.empty:
            QMessageBox.information(self, "Nenhum resultado", "Nenhum aluno encontrado com esse termo.")
        else:
            self.textbox_sql.clear()
            self.textbox_sql.setText("Nome;Matrícula\n")
            for index, row in resultados.iterrows():
                self.textbox_sql.append(f"{row['Nome']};{row['Matrícula']}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = GUI()
    gui.show()
    sys.exit(app.exec_())