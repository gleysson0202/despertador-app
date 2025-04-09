from flask import Flask, request, render_template
from flask_cors import CORS
import random
import smtplib
import mysql.connector

app = Flask(__name__)
CORS(app)

# ⚙️ Configurações do banco
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "gr896902@"  # 🔐 Altere para sua senha real
MYSQL_DATABASE = "formulario_fasem"

def conectar_mysql():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )

# 🔧 Criação automática do banco e tabela
def inicializar_banco():
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE}")
        cursor.execute(f"USE {MYSQL_DATABASE}")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dados_formulario (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100),
                cpf VARCHAR(20),
                telefone VARCHAR(20),
                email VARCHAR(100),
                curso VARCHAR(100),
                pontuacao_enem FLOAT,
                desconto_percentual INT,
                codigo_desconto VARCHAR(50)
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Banco e tabela verificados/criados com sucesso.")
    except Exception as e:
        print("❌ Erro ao criar banco/tabela:", e)

# 🔢 Gera um código aleatório
def gerar_codigo():
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))

# 📊 Calcula o desconto com base na nota
def calcular_desconto(pontuacao):
    if pontuacao >= 900:
        return 100
    elif pontuacao >= 850:
        return 80
    elif pontuacao >= 800:
        return 60
    elif pontuacao >= 750:
        return 40
    elif pontuacao >= 700:
        return 20
    else:
        return 10

# 📧 (Opcional) Envia o email com o código de desconto
def enviar_email(destinatario, codigo):
    remetente = "SEU_EMAIL@gmail.com"
    senha = "SENHA_DE_APP"  # Use uma senha de app do Gmail

    mensagem = f"""Subject: Código de Desconto

Obrigado por se inscrever!
Seu código de desconto é: {codigo}
"""

    with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
        servidor.starttls()
        servidor.login(remetente, senha)
        servidor.sendmail(remetente, destinatario, mensagem)

# 🌐 Página principal e submissão do formulário
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        nome = request.form["nome"]
        cpf = request.form["cpf"]
        telefone = request.form["Telefone"]
        email = request.form["email"]
        pontuacao_enem = float(request.form["pontuacao_enem"])
        curso = request.form["curso"]

        desconto = calcular_desconto(pontuacao_enem)
        codigo = gerar_codigo()

        try:
            conn = conectar_mysql()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO dados_formulario 
                (nome, cpf, telefone, email, curso, pontuacao_enem, desconto_percentual, codigo_desconto)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (nome, cpf, telefone, email, curso, pontuacao_enem, desconto, codigo))
            conn.commit()
            cursor.close()
            conn.close()

            # Envia o email (se configurado corretamente)
            # enviar_email(email, codigo)

            return render_template(
                "sucesso.html",
                nome=nome,
                email=email,
                percentual_desconto=desconto,
                discount_code=codigo,
                descricao_bolsa=f"Você garantiu {desconto}% de desconto com sua nota do ENEM!",
                curso=curso
            )

        except Exception as e:
            return f"<h3 style='color:red;'>Erro ao salvar dados: {e}</h3>"

    return render_template("index.html")

if __name__ == "__main__":
    inicializar_banco()
    app.run(debug=True)