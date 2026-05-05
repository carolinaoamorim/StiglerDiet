import argparse
from pathlib import Path

import numpy as np
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_QUANTIDADES = ROOT_DIR / "data" / "processed" / "diets_quantidades.csv"
DEFAULT_NUTRIENTES = ROOT_DIR / "data" / "processed" / "nutrientes_dietas.csv"
DEFAULT_SAIDA_ITENS = ROOT_DIR / "data" / "processed" / "diets_nutrientes_calculados.csv"
DEFAULT_SAIDA_RESUMO = ROOT_DIR / "data" / "processed" / "resumo_nutricional_dietas.csv"


def garantir_id_item_dieta(df):
    df = df.copy()

    if "id_item_dieta" not in df.columns:
        df.insert(0, "id_item_dieta", range(1, len(df) + 1))

    return df


def colunas_nutrientes_100g(df):
    return [col for col in df.columns if col.endswith("_100g")]


def nome_total(coluna_100g):
    return coluna_100g.replace("_100g", "_total")


def calcular_nutrientes(quantidades_path, nutrientes_path, saida_itens_path, saida_resumo_path):
    quantidades = garantir_id_item_dieta(pd.read_csv(quantidades_path))
    nutrientes = garantir_id_item_dieta(pd.read_csv(nutrientes_path))

    nutrientes_cols = colunas_nutrientes_100g(nutrientes)

    if not nutrientes_cols:
        raise ValueError("Nao encontrei colunas nutricionais terminadas em _100g.")

    colunas_nutrientes = [
        "id_item_dieta",
        "taco_numero_alimento",
        "taco_descricao",
        "taco_categoria",
        "fonte_nutricional",
        "status_match",
        "observacao",
        *nutrientes_cols,
    ]

    dados = quantidades.merge(
        nutrientes[colunas_nutrientes],
        on="id_item_dieta",
        how="left",
        validate="one_to_one",
    )

    fator_100g = pd.to_numeric(dados["fator_100g"], errors="coerce").fillna(0).to_numpy()
    matriz_nutrientes = (
        dados[nutrientes_cols]
        .apply(pd.to_numeric, errors="coerce")
        .fillna(0)
        .to_numpy(dtype=float)
    )

    # Algebra Linear: cada linha nutricional por 100g e multiplicada pela quantidade em unidades de 100g.
    matriz_nutrientes_reais = matriz_nutrientes * fator_100g[:, None]

    total_cols = [nome_total(col) for col in nutrientes_cols]
    nutrientes_reais = pd.DataFrame(matriz_nutrientes_reais, columns=total_cols)
    dados_calculados = pd.concat([dados, nutrientes_reais], axis=1)

    dietas = list(dict.fromkeys(dados_calculados["dieta"]))
    matriz_dieta = (
        pd.get_dummies(dados_calculados["dieta"])
        .reindex(columns=dietas, fill_value=0)
        .to_numpy(dtype=float)
    )

    # Algebra Linear: D.T @ N_real soma os vetores nutricionais dos itens de cada dieta.
    matriz_resumo = matriz_dieta.T @ matriz_nutrientes_reais

    preco = pd.to_numeric(dados_calculados["preco_medio"], errors="coerce").fillna(0).to_numpy()
    quantidade_g = pd.to_numeric(dados_calculados["quantidade_g"], errors="coerce").fillna(0).to_numpy()
    tem_nutriente = dados_calculados["taco_numero_alimento"].notna().to_numpy(dtype=float)
    sem_quantidade = dados_calculados["quantidade_g"].isna().to_numpy(dtype=float)

    resumo = pd.DataFrame(matriz_resumo, columns=total_cols)
    resumo.insert(0, "dieta", dietas)
    resumo.insert(1, "custo_total", matriz_dieta.T @ preco)
    resumo.insert(2, "quantidade_itens", (matriz_dieta.T @ np.ones(len(dados_calculados))).astype(int))
    resumo.insert(3, "quantidade_total_g", matriz_dieta.T @ quantidade_g)
    resumo.insert(4, "itens_com_nutrientes", (matriz_dieta.T @ tem_nutriente).astype(int))
    resumo.insert(5, "itens_sem_nutrientes", (matriz_dieta.T @ (1 - tem_nutriente)).astype(int))
    resumo.insert(6, "itens_sem_quantidade_g", (matriz_dieta.T @ sem_quantidade).astype(int))

    saida_itens_path.parent.mkdir(parents=True, exist_ok=True)
    saida_resumo_path.parent.mkdir(parents=True, exist_ok=True)
    dados_calculados.to_csv(saida_itens_path, index=False)
    resumo.to_csv(saida_resumo_path, index=False)

    return dados_calculados, resumo


def main():
    parser = argparse.ArgumentParser(
        description="Calcula nutrientes reais por item e resumo nutricional por dieta."
    )
    parser.add_argument("--quantidades", type=Path, default=DEFAULT_QUANTIDADES)
    parser.add_argument("--nutrientes", type=Path, default=DEFAULT_NUTRIENTES)
    parser.add_argument("--saida-itens", type=Path, default=DEFAULT_SAIDA_ITENS)
    parser.add_argument("--saida-resumo", type=Path, default=DEFAULT_SAIDA_RESUMO)
    args = parser.parse_args()

    dados_calculados, resumo = calcular_nutrientes(
        quantidades_path=args.quantidades,
        nutrientes_path=args.nutrientes,
        saida_itens_path=args.saida_itens,
        saida_resumo_path=args.saida_resumo,
    )

    print(f"Arquivo por item salvo em: {args.saida_itens}")
    print(f"Resumo por dieta salvo em: {args.saida_resumo}")
    print(f"Linhas por item: {len(dados_calculados)}")
    print(f"Dietas resumidas: {len(resumo)}")
    print(
        resumo[
            [
                "dieta",
                "custo_total",
                "quantidade_itens",
                "itens_sem_nutrientes",
                "energia_kcal_total",
                "proteina_g_total",
                "carboidrato_g_total",
                "lipideos_g_total",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
