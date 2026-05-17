# Otimização de Dietas por Análise Matricial: Uma Abordagem de Álgebra Linear para Avaliação Nutricional

## I. Introdução

A escolha de uma dieta adequada é um problema multidimensional que balanceia requisitos nutricionais, custos econômicos e viabilidade prática. Este projeto modela o problema de avaliação de dietas como um sistema de álgebra linear, permitindo quantificar o atendimento nutricional e o custo-benefício de diferentes regimes alimentares. A abordagem segue princípios de otimização linear amplamente utilizados em pesquisa operacional [1].

## II. Modelagem Linear do Problema

Seja $N \in \mathbb{R}^{m \times n}$ a matriz de nutrientes, onde cada linha representa um alimento $i$ e cada coluna um nutriente $j$ (energia, proteína, carboidrato, lipídeos). O vetor $q \in \mathbb{R}^m$ contém os fatores de conversão (fator_100g) que normalizam as quantidades consumidas.

A matriz de nutrientes reais é calculada como:
$$N_{real} = N \cdot \text{diag}(q)$$

A matriz indicadora $D \in \{0,1\}^{m \times d}$ mapeia cada alimento para sua respectiva dieta (cetogênica, vegana, normal, fast food). A matriz de nutrientes por dieta é:
$$M = D^T \cdot N_{real}$$

O vetor de custos por dieta é $\text{custo} = D^T \cdot c$, onde $c \in \mathbb{R}^m$ contém o preço médio de cada alimento.

O atendimento nutricional é medido como:
$$R = \frac{M}{b}$$

onde $b \in \mathbb{R}^n$ contém as recomendações diárias. O score nutricional é a média do atendimento capeada em 100%:
$$s_{nut} = \frac{1}{n}\sum_{j} \min(R_{ij}, 1.0)$$

O score custo-benefício é:
$$s_{cb} = \frac{s_{nut}}{\text{custo}}$$

## III. Implementação e Resultados

Os dados foram processados de `diets_nutrientes_calculados.csv`. O algoritmo produziu rankings em três dimensões:

| Dieta | Custo (R$) | Score Nutricional | Score/Real | Ranking |
|-------|-----------|-------------------|-----------|---------|
| Controle | 287.95 | 0.917 | 0.003473 | **1º** |
| Vegana | 331.00 | 0.854 | 0.003021 | 2º |
| McDonald's | 121.80 | 0.202 | 0.002451 | 3º |
| Cetogênica | 414.75 | 0.323 | 0.002411 | 4º |

A dieta "controle" oferece o melhor equilíbrio entre qualidade nutricional (91.7% das recomendações) e custo-benefício. A vegana se aproxima, enquanto dietas restritivas (cetogênica) ou com baixa variedade (fast food) apresentam déficits significativos.

## IV. Comparação com Referência

Stigler (1945) resolveu o "Stigler Diet Problem" usando programação linear para minimizar custos mantendo requisitos nutricionais mínimos [2]. Nossa abordagem é dual: **não** minimizamos custos, mas comparamos soluções reais sob múltiplas métricas. Enquanto Stigler buscava a dieta ótima, nós avaliamos dietas reais, permitindo análise de trade-offs.

## V. Limitações e Implicações

**Limitações:** (1) Recomendações diárias são simplificadas e uniformes; (2) Assunção linear ignora sinergia nutricional e biodisponibilidade; (3) Dados agregados em 100g mascaram variação intra-grupo; (4) Modelo não considera palatabilidade, acessibilidade ou sustentabilidade.

**Implicações:** O ranking sugere que dietas balanceadas (controle/vegana) superam especializadas (cetogênica/fast food), contrário ao discurso comercial. Porém, a utilidade real depende do contexto do paciente (objetivos específicos invalidam recomendações genéricas).

## VI. Conclusão

A modelagem de dietas como problema de álgebra linear viabiliza análise objetiva e computável. O projeto demonstra que ferramentas matemáticas simples revelam padrões em dados complexos, fundamentais para decisões racionais em nutrição.

---

## Referências

[1] G. B. Dantzig, "Linear programming and extensions," *Princeton University Press*, 1963.

[2] G. J. Stigler, "The cost of subsistence," *Journal of Farm Economics*, vol. 27, no. 2, pp. 303–314, 1945.

---

**Estrutura de Arquivos do Projeto:**
- `src/analise_matricial_dietas.py` — Implementação principal com álgebra linear
- `data/processed/ranking_dietas.csv` — Resultados finais
- `data/processed/diets_nutrientes_calculados.csv` — Dados de entrada
