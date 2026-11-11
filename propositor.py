# propositor.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

def propor_refeicao(saldo_restante: dict, refeicao: str, restricoes: list, api_key: str) -> str:
    # Usamos uma temperatura levemente maior (ex: 0.4) para permitir criatividade nas receitas, 
    # mas mantendo o foco matemático.
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=0.4, google_api_key=api_key)
    
    prompt = PromptTemplate(
        template="""Você é o NutrIA, um nutricionista esportivo de IA.
        O usuário precisa de uma sugestão para o(a) {refeicao}.
        
        SALDO RESTATE PARA HOJE (você deve zerar esses valores com a sua sugestão):
        - Calorias: {calorias:.1f} kcal
        - Proteínas: {proteinas:.1f} g
        - Carboidratos: {carboidratos:.1f} g
        - Gorduras: {gorduras:.1f} g
        
        Restrições alimentares do usuário: {restricoes}
        
        SUA TAREFA:
        1. Sugira uma refeição realista (ou opções de pratos) que atinja esses macros.
        2. Especifique as quantidades em gramas.
        3. Não sugira nada que viole as restrições.
        4. Seja encorajador e direto.
        """,
        input_variables=["refeicao", "calorias", "proteinas", "carboidratos", "gorduras", "restricoes"]
    )
    
    chain = prompt | llm
    
    # Prepara as variáveis. Se os macros ficaram negativos, ajusta para 0 para não confundir o LLM.
    resultado = chain.invoke({
        "refeicao": refeicao,
        "calorias": max(saldo_restante["calorias"], 0),
        "proteinas": max(saldo_restante["proteinas_g"], 0),
        "carboidratos": max(saldo_restante["carboidratos_g"], 0),
        "gorduras": max(saldo_restante["gorduras_g"], 0),
        "restricoes": ", ".join(restricoes) if restricoes else "Nenhuma"
    })
    
    return resultado.content