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

import pandas as pd

# Dados de exemplo - dieta com muito fast food
dados = [
    {"dieta": "fastfood_alto_consumo", "alimento": "hamburguer", "preco_medio": 18.00, "peso": "200 g"},
    {"dieta": "fastfood_alto_consumo", "alimento": "batata frita", "preco_medio": 12.00, "peso": "150 g"},
    {"dieta": "fastfood_alto_consumo", "alimento": "refrigerante", "preco_medio": 8.00, "peso": "350 ml"},
    {"dieta": "fastfood_alto_consumo", "alimento": "pizza", "preco_medio": 45.00, "peso": "8 fatias"},
    {"dieta": "fastfood_alto_consumo", "alimento": "hot dog", "preco_medio": 10.00, "peso": "180 g"},
    {"dieta": "fastfood_alto_consumo", "alimento": "frango frito", "preco_medio": 22.00, "peso": "300 g"},
    {"dieta": "fastfood_alto_consumo", "alimento": "milkshake", "preco_medio": 15.00, "peso": "400 ml"},
    {"dieta": "fastfood_alto_consumo", "alimento": "sorvete", "preco_medio": 12.00, "peso": "200 g"},
    {"dieta": "fastfood_alto_consumo", "alimento": "salgadinho", "preco_medio": 7.00, "peso": "100 g"},
    {"dieta": "fastfood_alto_consumo", "alimento": "chocolate", "preco_medio": 6.50, "peso": "90 g"},
]

# Criar DataFrame
df = pd.DataFrame(dados)

# Exibir a tabela
print(df)

# Salvar em CSV
df.to_csv("tabela_dieta_fastfood.csv", index=False, encoding="utf-8-sig")