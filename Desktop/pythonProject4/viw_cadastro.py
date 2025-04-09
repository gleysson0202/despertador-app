import pyrebase
import pandas as pd
import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter import filedialog

# Configurações do Firebase
firebase_config = {
    "apiKey": "AIzaSyB7SjJp7LWNuaJj5bipguty70ndR_cv9-U",
    "authDomain": "bolsa-enem-ecc87.firebaseapp.com",
    "databaseURL": "https://bolsa-enem-ecc87-default-rtdb.firebaseio.com",
    "projectId": "bolsa-enem-ecc87",
    "storageBucket": "bolsa-enem-ecc87.appspot.com",
    "messagingSenderId": "1037060130895",
    "appId": "1:1037060130895:web:e5714ef7dd2f5d3a6b023a",
    "measurementId": "G-VH8H77BSZ1"

}

firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()


def download_cadastros_excel():
    # Obter todos os registros da coleção "dados_formulario"
    cadastros = db.child("dados_formulario").get().val()

    # Verificar se existem cadastros
    if cadastros:
        # Converter para DataFrame pandas
        data = []
        for key, info in cadastros.items():
            data.append(info)
        df = pd.DataFrame(data)

        # Salvar em um arquivo Excel
        filepath = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Planilha Excel", "*.xlsx")])
        if filepath:
            df.to_excel(filepath, index=False)
            messagebox.showinfo("Sucesso", "Cadastros salvos com sucesso em:\n" + filepath)
    else:
        messagebox.showwarning("Atenção", "Nenhum cadastro encontrado.")


def exibir_cadastros():
    # Limpar a caixa de texto
    txt_cadastros.delete("1.0", tk.END)

    # Obter todos os registros da coleção "dados_formulario"
    cadastros = db.child("dados_formulario").get().val()

    # Adicionar os cadastros à caixa de texto
    if cadastros:
        for key, data in cadastros.items():
            txt_cadastros.insert(tk.END, f"Nome: {data.get('nome')}\n")
            txt_cadastros.insert(tk.END, f"CPF: {data.get('cpf')}\n")
            txt_cadastros.insert(tk.END, f"Telefone: {data.get('Telefone')}\n")
            txt_cadastros.insert(tk.END, f"Email: {data.get('email')}\n")
            txt_cadastros.insert(tk.END, f"Curso: {data.get('curso')}\n")
            txt_cadastros.insert(tk.END, f"Pontuação ENEM: {data.get('pontuacao_enem')}\n")
            txt_cadastros.insert(tk.END, f"Desconto %: {data.get('desconto_percentual')}\n")  # Correção aqui
            txt_cadastros.insert(tk.END, f"Código de Desconto: {data.get('codigo_desconto')}\n\n")
    else:
        txt_cadastros.insert(tk.END, "Nenhum cadastro encontrado.")


# Criar a janela principal
root = tk.Tk()
root.title("Cadastro de Alunos")

# Criar a caixa de texto para exibir os cadastros
txt_cadastros = scrolledtext.ScrolledText(root, width=80, height=20, wrap=tk.WORD)
txt_cadastros.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

# Botão para exibir os cadastros
btn_exibir = tk.Button(root, text="Exibir Cadastros", command=exibir_cadastros)
btn_exibir.grid(row=1, column=0, padx=5, pady=5)

# Botão para baixar os cadastros em Excel
btn_excel = tk.Button(root, text="Baixar Cadastros em Excel", command=download_cadastros_excel)
btn_excel.grid(row=1, column=1, padx=5, pady=5)

root.mainloop()
