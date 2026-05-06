import argparse
from pathlib import Path

import numpy as np
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_RESUMO = ROOT_DIR / "data" / "processed" / "resumo_nutricional_dietas.csv"
DEFAULT_SAIDA_COMPARACAO = ROOT_DIR / "data" / "processed" / "comparacao_requisitos.csv"
DEFAULT_SAIDA_RANKING = ROOT_DIR / "data" / "processed" / "ranking_dietas.csv"


REQUISITOS_MINIMOS = {
    "energia_kcal_total": 2000,
    "proteina_g_total": 50,
    "carboidrato_g_total": 130,
    "lipideos_g_total": 70,
    "fibra_alimentar_g_total": 25,
    "calcio_mg_total": 1000,
    "ferro_mg_total": 14,
}

LIMITES_MAXIMOS = {
    "sodio_mg_total": 2000,
}


def gerar_ranking(resumo_path, saida_comparacao_path, saida_ranking_path):
    resumo = pd.read_csv(resumo_path)

    comparacao = resumo[
        [
            "dieta",
            "custo_total",
            "quantidade_itens",
            "itens_com_nutrientes",
            "itens_sem_nutrientes",
            *REQUISITOS_MINIMOS.keys(),
            *LIMITES_MAXIMOS.keys(),
        ]
    ].copy()

    adequacao_cols = []
    for coluna, recomendado in REQUISITOS_MINIMOS.items():
        nome_razao = coluna.replace("_total", "_razao")
        nome_adequacao = coluna.replace("_total", "_adequacao")

        comparacao[nome_razao] = comparacao[coluna] / recomendado
        comparacao[nome_adequacao] = comparacao[nome_razao].clip(upper=1)
        adequacao_cols.append(nome_adequacao)

    limite_cols = []
    for coluna, limite in LIMITES_MAXIMOS.items():
        nome_razao = coluna.replace("_total", "_razao_limite")
        nome_score = coluna.replace("_total", "_score")

        comparacao[nome_razao] = comparacao[coluna] / limite
        comparacao[nome_score] = np.where(
            comparacao[coluna] <= limite,
            1,
            limite / comparacao[coluna],
        )
        limite_cols.append(nome_score)

    comparacao["score_adequacao"] = comparacao[adequacao_cols].mean(axis=1)
    comparacao["score_limites"] = comparacao[limite_cols].mean(axis=1)
    comparacao["cobertura_dados"] = (
        comparacao["itens_com_nutrientes"] / comparacao["quantidade_itens"]
    )
    comparacao["score_nutricional"] = (
        comparacao["score_adequacao"]
        * comparacao["score_limites"]
        * comparacao["cobertura_dados"]
    )
    comparacao["score_por_real"] = comparacao["score_nutricional"] / comparacao["custo_total"]
    comparacao["score_por_100_reais"] = comparacao["score_por_real"] * 100

    ranking = comparacao[
        [
            "dieta",
            "custo_total",
            "score_nutricional",
            "score_por_real",
            "score_por_100_reais",
            "score_adequacao",
            "score_limites",
            "cobertura_dados",
            "itens_sem_nutrientes",
        ]
    ].copy()

    ranking["ranking_nutricao"] = ranking["score_nutricional"].rank(
        ascending=False,
        method="min",
    ).astype(int)
    ranking["ranking_menor_custo"] = ranking["custo_total"].rank(
        ascending=True,
        method="min",
    ).astype(int)
    ranking["ranking_custo_beneficio"] = ranking["score_por_real"].rank(
        ascending=False,
        method="min",
    ).astype(int)

    ranking = ranking.sort_values(
        ["ranking_custo_beneficio", "ranking_nutricao", "ranking_menor_custo"]
    ).reset_index(drop=True)

    saida_comparacao_path.parent.mkdir(parents=True, exist_ok=True)
    saida_ranking_path.parent.mkdir(parents=True, exist_ok=True)
    comparacao.to_csv(saida_comparacao_path, index=False)
    ranking.to_csv(saida_ranking_path, index=False)

    return comparacao, ranking


def main():
    parser = argparse.ArgumentParser(
        description="Gera ranking das dietas por nutricao, custo e custo-beneficio."
    )
    parser.add_argument("--resumo", type=Path, default=DEFAULT_RESUMO)
    parser.add_argument("--saida-comparacao", type=Path, default=DEFAULT_SAIDA_COMPARACAO)
    parser.add_argument("--saida-ranking", type=Path, default=DEFAULT_SAIDA_RANKING)
    args = parser.parse_args()

    _, ranking = gerar_ranking(
        resumo_path=args.resumo,
        saida_comparacao_path=args.saida_comparacao,
        saida_ranking_path=args.saida_ranking,
    )

    print(f"Comparacao salva em: {args.saida_comparacao}")
    print(f"Ranking salvo em: {args.saida_ranking}")
    print(
        ranking[
            [
                "dieta",
                "custo_total",
                "score_nutricional",
                "score_por_100_reais",
                "ranking_nutricao",
                "ranking_menor_custo",
                "ranking_custo_beneficio",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
