import pandas as pd

df = pd.read_csv("data/processed/diets_nutrientes_calculados.csv")

nutrientes = [
    "energia_kcal_100g",
    "proteina_g_100g",
    "carboidrato_g_100g",
    "lipideos_g_100g",
]

N = df[nutrientes].fillna(0).to_numpy()

print(N)