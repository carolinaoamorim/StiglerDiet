import argparse
import re
import unicodedata
from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DIETS = ROOT_DIR / "data" / "diets.csv"
DEFAULT_TACO = ROOT_DIR / "data" / "alimentos.csv"
DEFAULT_OUTPUT = ROOT_DIR / "data" / "processed" / "nutrientes_dietas.csv"


NUTRIENT_COLUMNS = {
    "Umidade....": "umidade_g_100g",
    "Energia..kcal.": "energia_kcal_100g",
    "Energia..kJ.": "energia_kj_100g",
    "Proteína..g.": "proteina_g_100g",
    "Lipídeos..g.": "lipideos_g_100g",
    "Colesterol..mg.": "colesterol_mg_100g",
    "Carboidrato..g.": "carboidrato_g_100g",
    "Fibra.Alimentar..g.": "fibra_alimentar_g_100g",
    "Cinzas..g.": "cinzas_g_100g",
    "Cálcio..mg.": "calcio_mg_100g",
    "Magnésio..mg.": "magnesio_mg_100g",
    "Manganês..mg.": "manganes_mg_100g",
    "Fósforo..mg.": "fosforo_mg_100g",
    "Ferro..mg.": "ferro_mg_100g",
    "Sódio..mg.": "sodio_mg_100g",
    "Potássio..mg.": "potassio_mg_100g",
    "Cobre..mg.": "cobre_mg_100g",
    "Zinco..mg.": "zinco_mg_100g",
    "Retinol..mcg.": "retinol_mcg_100g",
    "RE..mcg.": "re_mcg_100g",
    "RAE..mcg.": "rae_mcg_100g",
    "Tiamina..mg.": "tiamina_mg_100g",
    "Riboflavina..mg.": "riboflavina_mg_100g",
    "Piridoxina..mg.": "piridoxina_mg_100g",
    "Niacina..mg.": "niacina_mg_100g",
    "Vitamina.C..mg.": "vitamina_c_mg_100g",
}


# Chaves = alimento normalizado do data/diets.csv.
# taco_id em branco significa que a TACO nao tem equivalente confiavel.
MANUAL_TACO_MAP = {
    "ovo": (488, "taco_aproximado", "Ovo inteiro cozido; revisar se a dieta usar ovo cru ou frito."),
    "queijo mucarela": (463, "taco_exato", ""),
    "queijo parmesao ralado": (464, "taco_aproximado", "A TACO tem parmesao, sem separar ralado."),
    "manteiga sem sal": (262, "taco_exato", ""),
    "creme de leite fresco": (447, "taco_aproximado", "A TACO tem creme de leite generico."),
    "azeite extra virgem": (260, "taco_exato", ""),
    "abacate": (163, "taco_exato", ""),
    "espinafre": (119, "taco_aproximado", "A TACO usa espinafre Nova Zelandia cru."),
    "brocolis": (101, "taco_aproximado", "Usando brocolis cru para manter base por 100g de alimento comprado."),
    "couve flor": (117, "taco_aproximado", "Usando couve-flor crua para manter base por 100g de alimento comprado."),
    "aspargos": ("", "sem_match_taco", "Nao encontrei aspargos na TACO."),
    "rucula": (152, "taco_exato", ""),
    "tomate cereja": (161, "taco_aproximado", "A TACO tem tomate salada, nao tomate-cereja."),
    "alho": (82, "taco_exato", ""),
    "limao": (220, "taco_aproximado", "Usando limao tahiti cru."),
    "salmao": (316, "taco_aproximado", "Usando salmao sem pele fresco cru."),
    "carne bovina ancho": (343, "taco_aproximado", "Ancho nao existe na TACO; usando contra-file com gordura cru."),
    "mix de castanhas": ("", "sem_match_taco", "Precisa definir a proporcao das castanhas do mix."),
    "castanha do para": (589, "taco_exato", "A TACO chama de castanha-do-Brasil."),
    "sementes de girassol": ("", "sem_match_taco", "A TACO tem oleo de girassol, mas nao semente."),
    "cafe em po": (511, "taco_exato", ""),
    "aveia em flocos": (7, "taco_exato", ""),
    "leite vegetal amendoas": ("", "rotulo_necessario", "Produto industrializado; usar rotulo ou outra base."),
    "banana": (182, "taco_aproximado", "Usando banana prata crua."),
    "pasta de amendoim": (557, "taco_aproximado", "A TACO nao tem pasta; usando amendoim grao cru como aproximacao."),
    "sementes de chia": ("", "sem_match_taco", "Nao encontrei chia na TACO."),
    "linhaca": (594, "taco_exato", ""),
    "arroz integral": (2, "taco_exato", "Usando arroz integral cru."),
    "feijao preto": (568, "taco_exato", "Usando feijao preto cru."),
    "grao de bico": (575, "taco_exato", "Usando grao-de-bico cru."),
    "quinoa": ("", "sem_match_taco", "Nao encontrei quinoa na TACO."),
    "tofu": (584, "taco_exato", "A TACO chama de soja, queijo (tofu)."),
    "shoyu": (518, "taco_exato", ""),
    "leite de coco": (523, "taco_exato", ""),
    "iogurte vegetal soja": ("", "rotulo_necessario", "Produto vegetal industrializado; usar rotulo ou outra base."),
    "granola sem mel": ("", "rotulo_necessario", "Granola varia por marca/receita; usar rotulo ou receita padrao."),
    "frutas vermelhas congeladas": ("", "sem_match_taco", "Nao ha mistura de frutas vermelhas congeladas na TACO."),
    "beterraba": (98, "taco_exato", "Usando beterraba crua."),
    "cenoura": (110, "taco_exato", "Usando cenoura crua."),
    "tomate": (157, "taco_exato", "Usando tomate com semente cru."),
    "pepino": (142, "taco_exato", ""),
    "gengibre": ("", "sem_match_taco", "Nao encontrei gengibre na TACO."),
    "hortela": ("", "sem_match_taco", "Nao encontrei hortela na TACO."),
    "gergelim": (593, "taco_exato", ""),
    "suplemento de vitamina b12": ("", "rotulo_necessario", "Suplemento nao deve vir da TACO; usar dosagem do produto."),
    "mcmuffin bacon ovo e queijo": ("", "rotulo_necessario", "Item de restaurante; usar tabela nutricional da marca."),
    "cafe expresso": (471, "taco_aproximado", "Usando cafe infusao 10%."),
    "big mac": ("", "rotulo_necessario", "Item de restaurante; usar tabela nutricional da marca."),
    "batata frita media": (93, "taco_aproximado", "A TACO tem batata inglesa frita, nao porcao media da marca."),
    "coca cola media": (480, "taco_aproximado", "Usando refrigerante tipo cola."),
    "mcflurry ovomaltine": ("", "rotulo_necessario", "Item de restaurante; usar tabela nutricional da marca."),
    "mcchicken": ("", "rotulo_necessario", "Item de restaurante; usar tabela nutricional da marca."),
    "batata frita pequena": (93, "taco_aproximado", "A TACO tem batata inglesa frita, nao porcao pequena da marca."),
    "pao frances": (53, "taco_exato", ""),
    "manteiga": (261, "taco_aproximado", "Sem detalhe no diet.csv; usando manteiga com sal."),
    "queijo minas": (461, "taco_aproximado", "Usando queijo minas frescal."),
    "presunto": (439, "taco_aproximado", "Usando presunto sem capa de gordura."),
    "leite integral": (458, "taco_exato", "Usando leite de vaca integral."),
    "mamao": (226, "taco_aproximado", "Usando mamao papaia cru."),
    "arroz": (4, "taco_aproximado", "Usando arroz tipo 1 cru."),
    "feijao": (562, "taco_aproximado", "Usando feijao carioca cru para feijao generico."),
    "carne bovina": (376, "taco_aproximado", "Usando patinho sem gordura cru para carne bovina generica."),
    "frango": (405, "taco_aproximado", "Usando frango inteiro sem pele cru."),
    "batata": (92, "taco_aproximado", "Usando batata inglesa crua."),
    "farofa pronta": (131, "taco_aproximado", "Usando mandioca, farofa temperada."),
    "alface": (78, "taco_aproximado", "Usando alface crespa crua."),
    "oleo de soja": (272, "taco_exato", ""),
    "cebola": (107, "taco_exato", ""),
    "bolacha cream cracker": (13, "taco_exato", "A TACO chama de biscoito salgado cream cracker."),
    "suco de laranja": (215, "taco_aproximado", "Usando suco de laranja pera."),
    "maca": (222, "taco_aproximado", "Usando maca Fuji com casca crua."),
    "macarrao": (40, "taco_aproximado", "Usando macarrao de trigo cru."),
    "molho de tomate": (159, "taco_exato", "Usando tomate, molho industrializado."),
}


def normalize_text(value):
    text = str(value).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def clean_numeric(value):
    number = pd.to_numeric(value, errors="coerce")

    if pd.isna(number):
        return pd.NA

    if abs(float(number)) < 1e-4:
        return 0

    return number


def build_nutrients_csv(diets_path, taco_path, output_path):
    diets = pd.read_csv(diets_path)
    taco = pd.read_csv(taco_path)

    diets["alimento_normalizado"] = diets["alimento"].map(normalize_text)

    taco_by_id = taco.set_index("Número do Alimento", drop=False)

    rows = []
    for index, diet_row in diets.reset_index(drop=True).iterrows():
        normalized = diet_row["alimento_normalizado"]
        alimento = diet_row["alimento"]
        taco_id, status, note = MANUAL_TACO_MAP.get(
            normalized,
            ("", "sem_match_taco", "Alimento novo no diets.csv; revisar de-para manualmente."),
        )

        row = {
            "id_item_dieta": index + 1,
            "dieta": diet_row["dieta"],
            "alimento": alimento,
            "preco_medio": diet_row["preco_medio"],
            "peso": diet_row["peso"],
            "alimento_normalizado": normalized,
            "taco_numero_alimento": taco_id,
            "taco_descricao": "",
            "taco_categoria": "",
            "fonte_nutricional": "TACO" if taco_id != "" else "",
            "status_match": status,
            "observacao": note,
        }

        for output_column in NUTRIENT_COLUMNS.values():
            row[output_column] = pd.NA

        if taco_id != "":
            if taco_id not in taco_by_id.index:
                raise ValueError(f"ID TACO {taco_id} nao existe para {alimento}.")

            taco_row = taco_by_id.loc[taco_id]
            row["taco_descricao"] = taco_row["Descrição dos alimentos"]
            row["taco_categoria"] = taco_row["Categoria do alimento"]

            for taco_column, output_column in NUTRIENT_COLUMNS.items():
                row[output_column] = clean_numeric(taco_row[taco_column])

        rows.append(row)

    output = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(output_path, index=False)
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Gera uma tabela nutricional para os alimentos de data/diets.csv."
    )
    parser.add_argument("--dietas", type=Path, default=DEFAULT_DIETS)
    parser.add_argument("--taco", type=Path, default=DEFAULT_TACO)
    parser.add_argument("--saida", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    output = build_nutrients_csv(args.dietas, args.taco, args.saida)
    matched = output["taco_numero_alimento"].notna() & (output["taco_numero_alimento"].astype(str) != "")

    print(f"Arquivo salvo em: {args.saida}")
    print(f"Linhas baseadas no diets.csv: {len(output)}")
    print(f"Alimentos unicos: {output['alimento_normalizado'].nunique()}")
    print(f"Com match TACO: {int(matched.sum())}")
    print(f"Sem match TACO/rotulo: {int((~matched).sum())}")


if __name__ == "__main__":
    main()
