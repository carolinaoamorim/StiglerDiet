import numpy as np
import pandas as pd


# Helpers internos

def _replace_small(df: pd.DataFrame, threshold: float = 1e-4) -> pd.DataFrame:
    """Valores como 1e-05 no CSV representam traços nutricionais (~0). Substitui por 0."""
    return df.apply(lambda col: col.map(
        lambda x: 0.0 if isinstance(x, float) and abs(x) < threshold else x
    ) if col.dtype == float else col)


# 1. alimentos.csv

def load_alimentos(path: str = "data/alimentos.csv"):
    """
    Carrega alimentos.csv e retorna:
        matrix  : np.ndarray shape (n_alimentos, n_nutrientes)  — valores numéricos
        foods   : lista de descrições dos alimentos (n_alimentos,)
        nutrients: lista de nomes dos nutrientes     (n_nutrientes,)

    Colunas de texto (Número, Categoria, Descrição) são separadas.
    NA → 0.0  |  traços (1e-05) → 0.0
    """
    df = pd.read_csv(path)

    meta_cols = ["Número do Alimento", "Categoria do alimento", "Descrição dos alimentos"]
    foods      = df["Descrição dos alimentos"].tolist()
    nutrient_cols = [c for c in df.columns if c not in meta_cols]

    num_df = df[nutrient_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    num_df = _replace_small(num_df)

    matrix    = num_df.to_numpy(dtype=float)
    nutrients = nutrient_cols

    return matrix, foods, nutrients


# 2. acidos_graxos.csv

def load_acidos_graxos(path: str = "data/acidos-graxos.csv"):
    """
    Carrega acidos-graxos.csv e retorna:
        matrix  : np.ndarray shape (n_alimentos, n_acidos)
        foods   : lista de descrições dos alimentos
        acids   : lista de nomes dos ácidos graxos

    NA → 0.0  |  traços (1e-05) → 0.0
    """
    df = pd.read_csv(path)

    meta_cols  = ["Número do Alimento", "Categoria do alimento", "Descrição dos alimentos"]
    foods      = df["Descrição dos alimentos"].tolist()
    acid_cols  = [c for c in df.columns if c not in meta_cols]

    num_df = df[acid_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    num_df = _replace_small(num_df)

    matrix = num_df.to_numpy(dtype=float)
    acids  = acid_cols

    return matrix, foods, acids


# 3. aminoacidos.csv

def load_aminoacidos(path: str = "data/aminoacidos.csv"):
    """
    Carrega aminoacidos.csv e retorna:
        matrix  : np.ndarray shape (n_alimentos, n_aminoacidos)
        foods   : lista de descrições dos alimentos
        aminos  : lista de nomes dos aminoácidos

    Atenção: os índices de alimento NÃO são contíguos neste arquivo
    (ex: 56, 80, 83, 123...). O índice original é preservado em `ids`.

    ids     : lista de inteiros com os números originais dos alimentos
    NA → 0.0 | vírgula decimal (ex: "0,12") → float
    """
    df = pd.read_csv(path)

    meta_cols  = ["Número do Alimento", "Descrição dos alimentos"]
    ids        = df["Número do Alimento"].tolist()
    foods      = df["Descrição dos alimentos"].tolist()
    amino_cols = [c for c in df.columns if c not in meta_cols]

    def parse_br_float(val):
        """Converte '0,12' → 0.12 além do float normal."""
        if isinstance(val, str):
            val = val.replace(",", ".")
        try:
            return float(val)
        except (ValueError, TypeError):
            return 0.0

    num_df = df[amino_cols].map(parse_br_float)
    num_df = _replace_small(num_df)

    matrix = num_df.to_numpy(dtype=float)
    aminos = amino_cols

    return matrix, foods, aminos, ids


# 4. preco_alimento.csv

def load_precos(path: str = "data/preco_alimento.csv"):
    """
    Carrega preco_alimento.csv e retorna:
        matrix  : np.ndarray shape (n_series, n_meses)  — preços numéricos
        labels  : lista de strings 'PRODUTO | UF'        (n_series,)
        months  : lista de strings com os meses          (n_meses,)

    O CSV tem células mescladas implícitas (produto e UF vazios nas linhas
    seguintes). Esta função preenche os valores faltantes para frente (ffill)
    antes de montar a matriz.

    Vírgula decimal (ex: "1,35") → float  |  células vazias → NaN → 0.0
    """
    df = pd.read_csv(path, dtype=str)

    # As duas primeiras colunas são produto e UF (com merge implícito)
    produto_col = df.columns[0]   # "Produto/Unidade"
    nivel_col   = df.columns[1]   # "Nível de Comercialização"
    uf_col      = df.columns[2]   # "U.F."
    month_cols  = list(df.columns[3:])

    # Preenche produto e UF para frente (desfaz o merge implícito)
    df[produto_col] = df[produto_col].replace("", np.nan).ffill()
    df[uf_col]      = df[uf_col].replace("", np.nan).ffill()

    # Rótulo legível por linha
    labels = (df[produto_col].fillna("") + " | " + df[uf_col].fillna("")).tolist()

    def parse_br_float(val):
        if pd.isna(val) or str(val).strip() == "":
            return 0.0
        val = str(val).replace(".", "").replace(",", ".")   # "1.820,00" → "1820.00"
        try:
            return float(val)
        except ValueError:
            return 0.0

    num_df = df[month_cols].map(parse_br_float)
    matrix = num_df.to_numpy(dtype=float)
    months = month_cols

    return matrix, labels, months


# Teste rápido

if __name__ == "__main__":
    print("=== alimentos ===")
    M, foods, nutrients = load_alimentos()
    print(f"  shape: {M.shape}")
    print(f"  nutrientes: {nutrients[:5]} ...")
    print(f"  alimento[0]: {foods[0]}")
    print(f"  linha[0]: {M[0, :5]}\n")

    print("=== acidos graxos ===")
    M, foods, acids = load_acidos_graxos()
    print(f"  shape: {M.shape}")
    print(f"  ácidos: {acids[:5]} ...\n")

    print("=== aminoacidos ===")
    M, foods, aminos, ids = load_aminoacidos()
    print(f"  shape: {M.shape}")
    print(f"  ids dos alimentos: {ids[:5]} ...")
    print(f"  aminoácidos: {aminos[:5]} ...\n")

    print("=== precos ===")
    M, labels, months = load_precos()
    print(f"  shape: {M.shape}")
    print(f"  meses: {months[:4]} ...")
    print(f"  label[0]: {labels[0]}")
    print(f"  preços linha[0]: {M[0, :4]}")