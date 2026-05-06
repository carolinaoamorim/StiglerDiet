import pandas as pd
import numpy as np

df = pd.read_csv("data/processed/diets_nutrientes_calculados.csv")

nutrientes = [
    "energia_kcal_100g",
    "proteina_g_100g",
    "carboidrato_g_100g",
    "lipideos_g_100g",
]

N = df[nutrientes].fillna(0).to_numpy()

q = pd.to_numeric(df["fator_100g"], errors="coerce").fillna(0).to_numpy(dtype=float)

N_real = N * q[:, None] # para obter os nutrientes por item 

dummies = pd.get_dummies(df['dieta'])
D = dummies.to_numpy(dtype=float) # matriz indicadora D relacionando cada item à sua dieta.
dietas = dummies.columns.to_list() # guarda a ordem das colunas das dietad

M = D.T @ N_real # matriz dieta x nutrientes

c = df["preco_medio"].fillna(0).to_numpy(dtype=float) # vetor de custos c com preco_medio por item

custo_dieta = D.T @ c

recomendacoes_diarias = {
    "energia_kcal_100g": 1800,  # kcal por dia
    "proteina_g_100g": 50,  # g por dia
    "carboidrato_g_100g": 300,  # g por dia
    "lipideos_g_100g": 70,  # g por dia
}

b = pd.Series(recomendacoes_diarias)[nutrientes].to_numpy(dtype=float)

R = M / b # para medir o percentual de atendimento nutricional.

teto = np.minimum(R, 1.0)
score_nutricional =  teto.mean(axis=1) # score nutricional de cada dieta

score_por_real = score_nutricional / custo_dieta

ranking = pd.DataFrame({
    "dieta": dietas,
    "custo_total": custo_dieta,
    "energia_kcal": M[:, 0],
    "proteina_g": M[:, 1],
    "carboidrato_g": M[:, 2],
    "lipideos_g": M[:, 3],
    "score_nutricional": score_nutricional,
    "score_por_real": score_por_real,
})

ranking["ranking_nutricao"] = ranking["score_nutricional"].rank(
    ascending=False,
    method="min"
).astype(int)

ranking["ranking_menor_custo"] = ranking["custo_total"].rank(
    ascending=True,
    method="min"
).astype(int)

ranking["ranking_custo_beneficio"] = ranking["score_por_real"].rank(
    ascending=False,
    method="min"
).astype(int)

ranking = ranking.sort_values("ranking_custo_beneficio")

print(ranking)

ranking.to_csv("data/processed/ranking_dietas.csv", index=False)
