import argparse
import re
import unicodedata
from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DIETS = ROOT_DIR / "data" / "diets.csv"
DEFAULT_ESTIMATES = ROOT_DIR / "data" / "processed" / "pesos_estimados.csv"
DEFAULT_OUTPUT = ROOT_DIR / "data" / "processed" / "diets_quantidades.csv"


def normalizar_texto(valor):
    texto = str(valor).strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^a-z0-9]+", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def numero_brasileiro(valor):
    return float(str(valor).replace(",", "."))


def converter_peso_direto(alimento_normalizado, peso_normalizado):
    match = re.fullmatch(r"(\d+(?:[,.]\d+)?)\s*(g|kg|ml|l)", peso_normalizado)

    if not match:
        return pd.NA, pd.NA, pd.NA

    quantidade = numero_brasileiro(match.group(1))
    unidade = match.group(2)

    if unidade == "g":
        return quantidade, "direto_g", "Peso informado diretamente em gramas."

    if unidade == "kg":
        return quantidade * 1000, "direto_kg", "Peso convertido de kg para gramas."

    if unidade in {"ml", "l"}:
        volume_ml = quantidade if unidade == "ml" else quantidade * 1000
        densidade = 0.92 if alimento_normalizado in {"azeite extra virgem", "oleo de soja"} else 1.0
        quantidade_g = volume_ml * densidade
        observacao = "Volume convertido usando densidade 1 ml = 1 g."

        if densidade != 1.0:
            observacao = "Volume de oleo/azeite convertido usando densidade aproximada 0.92 g/ml."

        return quantidade_g, f"volume_{unidade}_estimado", observacao

    return pd.NA, pd.NA, pd.NA


def padronizar_quantidades(diets_path, estimates_path, output_path):
    diets = pd.read_csv(diets_path)
    estimates = pd.read_csv(estimates_path)

    diets["alimento_normalizado"] = diets["alimento"].map(normalizar_texto)
    diets["peso_normalizado"] = diets["peso"].map(normalizar_texto)

    estimates = estimates.copy()
    estimates["alimento_normalizado"] = estimates["alimento_normalizado"].map(normalizar_texto)
    estimates["peso_normalizado"] = estimates["peso_normalizado"].map(normalizar_texto)

    rows = []
    for _, row in diets.iterrows():
        quantidade_g, tipo, observacao = converter_peso_direto(
            row["alimento_normalizado"],
            row["peso_normalizado"],
        )

        if pd.isna(tipo):
            filtro = (
                (estimates["alimento_normalizado"] == row["alimento_normalizado"])
                & (estimates["peso_normalizado"] == row["peso_normalizado"])
            )

            if filtro.any():
                estimate = estimates.loc[filtro].iloc[0]
                quantidade_g = pd.to_numeric(estimate["quantidade_g"], errors="coerce")
                tipo = estimate["tipo_conversao"]
                observacao = estimate["observacao"]
            else:
                tipo = "sem_regra"
                observacao = "Criar regra em data/processed/pesos_estimados.csv."

        output_row = row.drop(labels=["peso_normalizado"]).to_dict()
        output_row["quantidade_g"] = quantidade_g
        output_row["fator_100g"] = quantidade_g / 100 if pd.notna(quantidade_g) else pd.NA
        output_row["tipo_conversao_quantidade"] = tipo
        output_row["observacao_quantidade"] = observacao
        rows.append(output_row)

    output = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(output_path, index=False)
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Padroniza a coluna peso do data/diets.csv para quantidade em gramas."
    )
    parser.add_argument("--dietas", type=Path, default=DEFAULT_DIETS)
    parser.add_argument("--estimativas", type=Path, default=DEFAULT_ESTIMATES)
    parser.add_argument("--saida", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    output = padronizar_quantidades(args.dietas, args.estimativas, args.saida)
    sem_regra = output[output["tipo_conversao_quantidade"] == "sem_regra"]
    sem_gramas = output["quantidade_g"].isna().sum()

    print(f"Arquivo salvo em: {args.saida}")
    print(f"Linhas processadas: {len(output)}")
    print(f"Linhas sem quantidade em gramas: {sem_gramas}")

    if not sem_regra.empty:
        print("Linhas sem regra:")
        print(sem_regra[["dieta", "alimento", "peso"]].to_string(index=False))


if __name__ == "__main__":
    main()
