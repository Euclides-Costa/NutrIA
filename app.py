# app.py
import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Importa os módulos que você já criou
from perfil_db import init_db, obter_perfil_usuario, criar_perfil
from extrator import extrair_informacoes_relato
from ferramentas import calcular_saldo_macros
from propositor import propor_refeicao

load_dotenv()

app = Flask(__name__)
api_key = os.getenv("GOOGLE_API_KEY")

@app.route("/")
def index():
    init_db()
    perfil = obter_perfil_usuario(1)
    # Se o perfil 1 não existir, avisa o HTML para mostrar a tela de cadastro
    precisa_onboarding = True if not perfil else False
    return render_template("index.html", precisa_onboarding=precisa_onboarding, perfil=perfil)

@app.route("/api/onboarding", methods=["POST"])
def onboarding():
    dados = request.json
    restricoes = [r.strip() for r in dados.get("restricoes", "").split(",")] if dados.get("restricoes") else []
    
    criar_perfil(
        nome=dados["nome"],
        idade=int(dados["idade"]),
        peso=float(dados["peso"]),
        altura=float(dados["altura"]),
        objetivo=dados["objetivo"],
        restricoes=restricoes
    )
    return jsonify({"status": "sucesso"})

@app.route("/api/chat", methods=["POST"])
def chat():
    dados = request.json
    relato = dados.get("mensagem")
    perfil = obter_perfil_usuario(1)
    
    try:
        # Pipeline do Agente
        dados_extraidos = extrair_informacoes_relato(relato, api_key)
        calculo = calcular_saldo_macros(perfil, dados_extraidos.alimentos, dados_extraidos.intensidade_treino)
        resposta_final = propor_refeicao(
            saldo_restante=calculo["saldo_restante"],
            refeicao=dados_extraidos.refeicao_desejada,
            restricoes=perfil["restricoes"],
            api_key=api_key
        )
        
        # Converte quebras de linha do markdown para HTML
        resposta_html = resposta_final.replace('\n', '<br>')
        
        return jsonify({
            "resposta": resposta_html, 
            "saldo": calculo["saldo_restante"]
        })
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)