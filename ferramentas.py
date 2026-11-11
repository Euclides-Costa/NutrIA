# ferramentas.py

def consultar_tabela_nutricional(nome_alimento: str, quantidade_g: float) -> dict:
    # Simula uma consulta a um banco de dados ou API externa (ex: TACO/IBGE)
    # Valores baseados em porções de 100g
    tabela = {
        "carne moída": {"kcal": 250.0, "prot": 26.0, "carb": 0.0, "gord": 15.0},
        "suco de laranja": {"kcal": 45.0, "prot": 0.7, "carb": 10.0, "gord": 0.2},
    }

    # Busca simples (poderia ser aprimorada no futuro)
    alimento_encontrado = None
    for chave in tabela:
        if chave in nome_alimento.lower():
            alimento_encontrado = tabela[chave]
            break

    if not alimento_encontrado:
        return {"kcal": 0, "prot": 0, "carb": 0, "gord": 0}

    # Se a quantidade não foi extraída (veio 0), assumimos uma porção padrão de 200g/ml
    qtd = quantidade_g if quantidade_g > 0 else 200.0
    fator = qtd / 100.0
    
    return {
        "kcal": alimento_encontrado["kcal"] * fator,
        "prot": alimento_encontrado["prot"] * fator,
        "carb": alimento_encontrado["carb"] * fator,
        "gord": alimento_encontrado["gord"] * fator
    }

def calcular_saldo_macros(perfil: dict, alimentos_extraidos: list, intensidade_treino: str) -> dict:
    metas = perfil["metas_diarias"].copy()
    historico = perfil["historico_consumido_hoje"]
    
    # 1. Recalcula a meta baseada na demanda do treino relatado
    intensidade = intensidade_treino.lower()
    if "pesado" in intensidade:
        metas["calorias"] += 300
        metas["carboidratos_g"] += 50
        metas["proteinas_g"] += 10
    elif "moderado" in intensidade:
        metas["calorias"] += 150
        metas["carboidratos_g"] += 25
        
    # 2. Subtrai o que já foi consumido hoje (antes do desvio)
    saldo = {
        "calorias": metas["calorias"] - historico["calorias"],
        "proteinas_g": metas["proteinas_g"] - historico["proteinas_g"],
        "carboidratos_g": metas["carboidratos_g"] - historico["carboidratos_g"],
        "gorduras_g": metas["gorduras_g"] - historico["gorduras_g"],
    }
    
    # 3. Consulta a base e subtrai os alimentos consumidos no desvio (ex: almoço)
    for alim in alimentos_extraidos:
        info = consultar_tabela_nutricional(alim.nome, alim.quantidade_gramas)
        saldo["calorias"] -= info["kcal"]
        saldo["proteinas_g"] -= info["prot"]
        saldo["carboidratos_g"] -= info["carb"]
        saldo["gorduras_g"] -= info["gord"]
        
    return {
        "saldo_restante": saldo,
        "metas_recalculadas": metas
    }