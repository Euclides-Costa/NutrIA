# main.py
import os
from dotenv import load_dotenv
from perfil_db import init_db, obter_perfil_usuario, criar_perfil
from extrator import extrair_informacoes_relato
from ferramentas import calcular_saldo_macros
from propositor import propor_refeicao

load_dotenv()

def onboarding_usuario():
    print("\n📝 --- Criando seu Perfil Nutricional ---")
    nome = input("Qual o seu nome? ")
    idade = int(input("Qual sua idade? "))
    peso = float(input("Qual o seu peso (kg)? ex: 70.5: "))
    altura = float(input("Qual a sua altura (cm)? ex: 173: "))
    objetivo = input("Objetivo (emagrecer, manter, ganhar): ").strip().lower()
    
    restricoes_input = input("Alguma restrição alimentar? (Separe por vírgula ou aperte Enter se nenhuma): ")
    restricoes = [r.strip() for r in restricoes_input.split(',')] if restricoes_input else []
    
    print("\n⚙️ Calculando suas metas basais e salvando no banco de dados...")
    user_id = criar_perfil(nome, idade, peso, altura, objetivo, restricoes)
    
    print(f"✅ Perfil criado com sucesso! (Seu ID de usuário é {user_id})\n")
    return user_id

def chat_nutria():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Erro: Chave GOOGLE_API_KEY não encontrada no .env")
        return

    # 1. Inicializa o Banco de Dados
    init_db()

    print("=====================================================")
    print("🤖 NutrIA - Seu Assistente de Nutrição Esportiva")
    print("=====================================================")
    
    # 2. Verifica se o Usuário 1 existe no banco. Se não, faz o onboarding.
    perfil = obter_perfil_usuario(1)
    if not perfil:
        onboarding_usuario()
        perfil = obter_perfil_usuario(1)
    else:
        print(f"✅ Perfil carregado: Bem-vindo(a) de volta, {perfil['nome']}!")
        print(f"Suas metas: {perfil['metas_diarias']}")

    print("\nDigite 'sair' para encerrar o programa.\n")

    while True:
        relato = input("Você: ")
        
        if relato.lower() in ['sair', 'exit', 'quit']:
            print(f"NutrIA: Bom treino, {perfil['nome']}! Até a próxima.")
            break
            
        if not relato.strip():
            continue

        print("\n[NutrIA está pensando...]")
        
        try:
            print(" ⚙️ Extraindo alimentos e intensidade do treino...")
            dados_extraidos = extrair_informacoes_relato(relato, api_key)
            
            print(" 🧮 Consultando base nutricional e calculando macros...")
            calculo = calcular_saldo_macros(perfil, dados_extraidos.alimentos, dados_extraidos.intensidade_treino)
            
            print(" 🍽️ Montando sugestão de refeição ajustada...\n")
            resposta_final = propor_refeicao(
                saldo_restante=calculo["saldo_restante"],
                refeicao=dados_extraidos.refeicao_desejada,
                restricoes=perfil["restricoes"],
                api_key=api_key
            )
            
            print("=====================================================")
            print("NutrIA:\n")
            print(resposta_final)
            print("=====================================================")
            print(f"(Debug) Saldo calculado pelo Python: {calculo['saldo_restante']}")

        except Exception as e:
            print(f"\n❌ Ocorreu um erro no processamento: {e}")

if __name__ == "__main__":
    chat_nutria()