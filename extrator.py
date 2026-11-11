# extrator.py
from pydantic import BaseModel, Field
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

class AlimentoConsumido(BaseModel):
    nome: str = Field(description="Nome do alimento consumido")
    quantidade_gramas: float = Field(description="Quantidade estimada em gramas. Se não especificado, assuma 0.")

class ContextoRelato(BaseModel):
    alimentos: List[AlimentoConsumido] = Field(description="Lista de alimentos consumidos fora do plano")
    intensidade_treino: str = Field(description="Intensidade do treino relatado (ex: leve, moderado, pesado)")
    refeicao_desejada: str = Field(description="Qual refeição o usuário quer que seja ajustada (ex: jantar)")

def extrair_informacoes_relato(relato_usuario: str, api_key: str) -> ContextoRelato:
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=0, google_api_key=api_key)
    
    # 1. Cria o parser baseado na sua estrutura Pydantic
    parser = PydanticOutputParser(pydantic_object=ContextoRelato)
    
    # 2. Injeta as instruções de formatação diretamente no prompt
    prompt = PromptTemplate(
        template="""Você é um assistente especialista em nutrição esportiva.
        Analise o relato do usuário e extraia os alimentos consumidos, a intensidade do treino e a refeição que precisa ser planejada.
        
        {format_instructions}
        
        Relato: {relato}
        """,
        input_variables=["relato"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    
    # 3. Conecta o prompt, o LLM e o Parser num pipeline simples
    chain = prompt | llm | parser
    
    resultado = chain.invoke({"relato": relato_usuario})
    return resultado