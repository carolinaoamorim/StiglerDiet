import pandas as pd

# Dados de exemplo
dados = [
    {"dieta": "alimentacao_normal_brasil", "alimento": "arroz", "preco_medio": 6.50, "peso": "1 kg"},
    {"dieta": "alimentacao_normal_brasil", "alimento": "feijao", "preco_medio": 9.80, "peso": "1 kg"},
    {"dieta": "alimentacao_normal_brasil", "alimento": "macarrao", "preco_medio": 4.50, "peso": "500 g"},
    {"dieta": "alimentacao_normal_brasil", "alimento": "pao frances", "preco_medio": 0.90, "peso": "50 g"},
    {"dieta": "alimentacao_normal_brasil", "alimento": "batata", "preco_medio": 5.20, "peso": "1 kg"},
    {"dieta": "alimentacao_normal_brasil", "alimento": "frango", "preco_medio": 16.90, "peso": "1 kg"},
    {"dieta": "alimentacao_normal_brasil", "alimento": "carne bovina", "preco_medio": 39.90, "peso": "1 kg"},
    {"dieta": "alimentacao_normal_brasil", "alimento": "ovo", "preco_medio": 0.85, "peso": "1 unidade"},
    {"dieta": "alimentacao_normal_brasil", "alimento": "peixe", "preco_medio": 28.00, "peso": "1 kg"},
    {"dieta": "alimentacao_normal_brasil", "alimento": "alface", "preco_medio": 3.50, "peso": "1 unidade"},
]

# Criar DataFrame
df = pd.DataFrame(dados)

# Exibir a tabela
print(df)

# Salvar em CSV
df.to_csv("tabela_dieta_alimentos.csv", index=False, encoding="utf-8-sig")