# Relatório Completo do Projeto
## Previsão de Rebaixamento no Brasileirão Série A — TCC

**Aluno:** Leonardo Feitosa  
**Curso:** Ciência de Dados — UFPB  
**Ano:** 2025  

---

## 1. VISÃO GERAL DO PROJETO

O projeto tem como objetivo prever quais clubes têm maior risco de rebaixamento no **Brasileirão Série A 2025**, utilizando dados financeiros e de elenco coletados do site **Transfermarkt**.

Foram treinados e comparados **3 modelos de classificação binária**:
- Regressão Logística
- Random Forest
- Support Vector Machine (SVM)

A variável-alvo é binária: **0 = Rebaixado** | **1 = Permaneceu na Série A**

---

## 2. ESTRUTURA DE ARQUIVOS

```
Previsao-Tcc/
│
├── app.py                          ← Entrada principal do Streamlit
├── requirements.txt                ← Dependências do projeto
│
├── app/
│   ├── controllers/
│   │   ├── config.py               ← Configuração da página (CSS, título)
│   │   └── sidebar.py              ← Barra lateral de navegação
│   ├── paginas/
│   │   ├── previsao.py             ← Página: Simulador + Ranking 2025
│   │   ├── analise_descritiva.py   ← Página: Análise exploratória interativa
│   │   ├── analise_sensibilidade.py← Página: Impacto de cada variável
│   │   └── dados_historicos.py     ← Página: Base histórica filtrável
│   └── utils/
│       ├── processamento.py        ← Carregamento de dados e modelos
│       └── styles.py               ← CSS profissional da interface
│
├── dados/
│   └── BASE_FINAL.xlsx             ← Base de dados (fonte única de verdade)
│
├── modelos/
│   ├── logistica.pkl               ← Modelo Regressão Logística treinado
│   ├── scaler_logistica.pkl        ← Scaler da Logística
│   ├── random_forest.pkl           ← Modelo Random Forest treinado
│   ├── scaler_rf.pkl               ← Scaler do Random Forest
│   ├── svm.pkl                     ← Modelo SVM treinado
│   └── scaler_svm.pkl              ← Scaler do SVM
│
├── img/                            ← Gráficos gerados pelos notebooks
│   ├── cm_logistica.png            ← Matriz de confusão — Logística
│   ├── cm_random_forest.png        ← Matriz de confusão — Random Forest
│   ├── cm_svm.png                  ← Matriz de confusão — SVM
│   ├── roc_logistica.png           ← Curva ROC — Logística
│   ├── roc_random_forest.png       ← Curva ROC — Random Forest
│   ├── roc_svm.png                 ← Curva ROC — SVM
│   ├── roc_comparacao.png          ← Curvas ROC dos 3 modelos juntos
│   ├── comparacao_metricas.png     ← Barras comparativas de métricas
│   ├── matrizes_confusao.png       ← 3 matrizes lado a lado
│   ├── feat_importance_rf.png      ← Importância das features (RF)
│   ├── coef_logistica.png          ← Coeficientes da Logística
│   └── previsao_2025.png           ← Ranking de risco 2025
│
└── notebooks/
    ├── 00_coleta_dados.ipynb
    ├── 01_analise_exploratoria.ipynb
    ├── 02_preprocessamento.ipynb
    ├── 03_modelo_logistica.ipynb
    ├── 04_modelo_random_forest.ipynb
    ├── 05_modelo_svm.ipynb
    ├── 06_comparacao_modelos.ipynb
    └── 07_previsao_2025.ipynb
```

---

## 3. BASE DE DADOS — BASE_FINAL.xlsx

- **Fonte:** Transfermarkt (https://www.transfermarkt.com.br)
- **Coleta:** Python com `requests` + `BeautifulSoup` (sem Excel, sem PROCV)
- **Período:** 2014 a 2025 (12 temporadas)
- **Registros:** 240 (20 clubes × 12 temporadas)
- **Clubes únicos:** 35

| Coluna | Tipo | Descrição |
|---|---|---|
| `Clube` | string | Nome padronizado do clube |
| `Plantel` | int | Total de jogadores no elenco |
| `ø Idade` | float | Idade média do plantel |
| `Estrangeiros` | int | Número de jogadores estrangeiros |
| `ø Valor de Mercado` | float | Valor médio por jogador (M€) |
| `Valor de Mercado Total` | float | Valor total do plantel (M€) |
| `Temporada` | int | Ano da temporada |
| `Pontos` | int | Pontos finais (NaN para 2025) |
| `Situacao` | string | Resultado: Rebaixado, SerieA, Top4 |
| `Status_bin` | int | Variável-alvo: 0=Rebaixado, 1=Permaneceu |

### Features usadas no modelo
- `Plantel`
- `Estrangeiros`
- `Valor de Mercado Total`

---

## 4. ERROS IDENTIFICADOS E CORRIGIDOS

### 4.1 Substituição do PROCV no Excel por Python

**Problema:** Os pontos finais de cada temporada eram adicionados manualmente via PROCV no Excel, processo manual, sujeito a erros e não reprodutível.

**Solução:** Script Python com `requests` + `BeautifulSoup` que raspa a tabela de classificação final do Transfermarkt para cada temporada (2014–2024), com merge automático por `Clube + Temporada`.

**Onde está:** `notebooks/00_coleta_dados.ipynb` — células de URLs e verificação

**Convenção de URLs descoberta:**
- O Transfermarkt usa `saison_id = Temporada - 1`
- Exemplo: Temporada 2024 na BASE_FINAL → `saison_id=2023` na URL

---

### 4.2 Padronização de Nomes de Clubes

**Problema:** O mesmo clube aparecia com nomes diferentes ao longo das temporadas, quebrando o merge e causando duplicatas.

| Nome original | Nome padronizado | Motivo |
|---|---|---|
| `Atlético Paranaense` | `Athletico Paranaense` | Rebrand oficial do clube em 2018 |
| `Vasco da` | `Vasco da Gama` | Nome truncado pelo Transfermarkt |

**Onde está:** `notebooks/00_coleta_dados.ipynb` — célula "Limpeza 1"

**Código:**
```python
renomear = {
    'Atlético Paranaense': 'Athletico Paranaense',
    'Vasco da':            'Vasco da Gama',
}
for antigo, novo in renomear.items():
    df.loc[df['Clube'] == antigo, 'Clube'] = novo
```

---

### 4.3 Correção dos Rótulos de Rebaixamento

**Problema:** A coluna `Situacao` continha erros graves — 8 clubes marcados como `Rebaixado` que não foram rebaixados, e 8 clubes que foram rebaixados mas estavam como `SerieA`. Erro identificado comparando a base com as tabelas históricas oficiais do Brasileirão.

**Regra:** Cada temporada deve ter **exatamente 4 clubes rebaixados**.

**Clubes removidos do Rebaixado (estavam errados):**

| Clube | Temporada |
|---|---|
| Vitória | 2016 |
| Vitória | 2017 |
| Ceará | 2019 |
| Fortaleza | 2020 |
| Vasco da Gama | 2023 |
| Grêmio | 2024 |
| Juventude | 2024 |
| Vitória | 2024 |

**Clubes adicionados ao Rebaixado (estavam faltando):**

| Clube | Temporada |
|---|---|
| Avaí | 2015 |
| Avaí | 2017 |
| América Mineiro | 2018 |
| Sport Recife | 2018 |
| Vasco da Gama | 2020 |
| Bahia | 2021 |
| Goiás | 2023 |
| Cuiabá | 2024 |

**Onde está:** `notebooks/00_coleta_dados.ipynb` — célula "Limpeza 2"

---

### 4.4 Correção do Bug de Probabilidade Invertida no Streamlit

**Problema:** Todas as páginas do Streamlit usavam `prob[1]` (probabilidade de **permanência**) como probabilidade de rebaixamento — o ranking estava completamente invertido.

**Solução:** Substituído por `prob[0]` (probabilidade de **rebaixamento**) em todos os arquivos:
- `app/paginas/previsao.py`
- `app/paginas/analise_sensibilidade.py`
- `app/utils/processamento.py`

**Código correto:**
```python
prob_reb = probs[0][0]   # índice 0 → classe Rebaixado
```

---

### 4.5 Correção dos Caminhos dos Modelos

**Problema:** `notebooks/07_previsao_2025.ipynb` e `app/utils/processamento.py` carregavam arquivos inexistentes:
- `modelo_logit_status.pkl` → não existia
- `scaler_logit_status.pkl` → não existia

**Solução:** Corrigido para os arquivos corretos gerados pelo notebook 03:
- `modelos/logistica.pkl`
- `modelos/scaler_logistica.pkl`

---

### 4.6 Notebooks com Kernel Travando (matplotlib no Windows)

**Problema:** No Windows com VS Code Jupyter, o comando `plt.show()` causa crash do kernel sem possibilidade de interrupção.

**Solução aplicada nos notebooks 04, 05 e 06:**
- Removido `matplotlib` e `plt.show()` dos notebooks
- Gráficos gerados via terminal Python com `matplotlib.use('Agg')`
- Notebooks exibem as imagens salvas com `display(Image(filename=...))`

---

### 4.7 Erro de Sintaxe no Notebook 02

**Problema:** `print[df['col',...]]` — duplo erro: `print[]` e colchete em vez de parêntese.

**Solução:** Corrigido para `print(df[['col',...]])`.

---

### 4.8 Dados Históricos Lendo CSV Desatualizado

**Problema:** `app/paginas/dados_historicos.py` importava `carregar_dados()` que lia `dados/BASE_FINAL.csv` — arquivo desatualizado sem as correções de pontos.

**Solução:** Alterado para `carregar_dados_excel()` que lê `dados/BASE_FINAL.xlsx`.

---

## 5. NOTEBOOKS — O QUE CADA UM FAZ

### 00_coleta_dados.ipynb
Documenta todo o processo de coleta e limpeza:
1. **URLs de scraping** — elenco (saison_id = Temporada) e pontos (saison_id = Temporada - 1)
2. **Carregamento** da BASE_FINAL.xlsx
3. **Limpeza 1** — padronização de nomes de clubes
4. **Limpeza 2** — correção dos rótulos de rebaixamento + salva xlsx corrigido
5. **Criação do Status_bin** — variável binária 0/1
6. **Verificação dos pontos** — confirma zero zeros indevidos
7. **Histograma** — distribuição de pontos por situação final

### 01_analise_exploratoria.ipynb
- Distribuição das variáveis por temporada
- Correlações entre features
- Boxplots: rebaixados vs permaneceram
- Evolução do valor de mercado ao longo dos anos

### 02_preprocessamento.ipynb
- Separação temporal treino/teste (sem aleatoriedade):
  - **Treino:** 2014–2022 (180 registros)
  - **Teste:** 2023–2024 (40 registros)
  - **Previsão:** 2025 (20 registros)
- Aplicação do `StandardScaler` (ajuste apenas no treino)
- Verificação de valores nulos e distribuição das classes

### 03_modelo_logistica.ipynb
- Treinamento da Regressão Logística com `class_weight='balanced'`
- Avaliação: acurácia, relatório de classificação, matriz de confusão
- Curva ROC e AUC
- Coeficientes do modelo (interpretabilidade)
- Salva: `logistica.pkl` e `scaler_logistica.pkl`

### 04_modelo_random_forest.ipynb
- Carrega `random_forest.pkl` (treinado via terminal por instabilidade do kernel no Windows)
- Avalia métricas e exibe imagens salvas
- Importância das features (Gini)
- Salva: `random_forest.pkl` e `scaler_rf.pkl`

### 05_modelo_svm.ipynb
- Carrega `svm.pkl` (treinado via terminal pelo mesmo motivo)
- SVM com kernel RBF e `probability=True`
- Avalia métricas e exibe curva ROC
- Salva: `svm.pkl` e `scaler_svm.pkl`

### 06_comparacao_modelos.ipynb
- Carrega os 3 modelos e compara no **mesmo conjunto de teste**
- Tabela com Acurácia, MAE, RMSE e AUC
- Gráfico de barras comparativo
- Curvas ROC dos 3 modelos sobrepostas
- Matrizes de confusão lado a lado
- **Justificativa da escolha do modelo final:** Regressão Logística

### 07_previsao_2025.ipynb
- Carrega o modelo final (Regressão Logística)
- Aplica nos dados de 2025 (20 clubes)
- Gera probabilidades de rebaixamento para cada clube
- Tabela e gráfico de ranking de risco
- 4 clubes com maior probabilidade marcados como previsão de rebaixamento

---

## 6. SEPARAÇÃO TEMPORAL (SEM VAZAMENTO DE DADOS)

A separação foi feita **exclusivamente por período temporal**, nunca de forma aleatória. Isso é fundamental para dados de série temporal — usar split aleatório causaria **data leakage** (o modelo "veria o futuro" durante o treino).

| Conjunto | Período | Registros |
|---|---|---|
| Treino | 2014–2022 | 180 |
| Teste | 2023–2024 | 40 |
| Previsão | 2025 | 20 |

---

## 7. RESULTADOS DOS MODELOS

Métricas no conjunto de teste (2023–2024):

| Modelo | Acurácia | MAE | RMSE | AUC |
|---|---|---|---|---|
| **Regressão Logística** | **75,00%** | 0.2500 | 0.5000 | **0.8125** |
| Random Forest | 82,50% | 0.1750 | 0.4183 | 0.6309 |
| SVM | 77,50% | 0.2250 | 0.4743 | 0.6836 |

### Por que a Regressão Logística foi escolhida?

1. **Maior AUC (0.8125)** — melhor capacidade de distinguir rebaixados de não-rebaixados, que é o objetivo do modelo
2. **Interpretabilidade** — os coeficientes revelam diretamente o peso de cada variável
3. **Adequação ao problema** — variável binária, poucas features numéricas
4. **AUC é a métrica mais relevante** para problemas com classes desbalanceadas

### Coeficientes da Regressão Logística

| Feature | Coeficiente | Interpretação |
|---|---|---|
| `Valor de Mercado Total` | +1.151 | Maior valor → menor risco de rebaixamento |
| `Plantel` | -0.665 | Plantel maior → maior risco (correlacionado com clubes menores) |
| `Estrangeiros` | +0.079 | Pouco impacto isolado |

---

## 8. PREVISÃO 2025

Os 4 clubes com maior probabilidade de rebaixamento prevista para 2025:

| Posição | Clube | Prob. Rebaixamento |
|---|---|---|
| 1º | Juventude | 50,3% |
| 2º | Mirassol | 46,4% |
| 3º | Ceará | 36,5% |
| 4º | Vitória | 30,4% |

> **Limitações:** O modelo usa apenas dados de elenco e valor de mercado registrados no início da temporada. Não considera lesões, mudanças técnicas, calendário ou desempenho em campo.

---

## 9. APLICAÇÃO STREAMLIT

Para executar:
```bash
python -m streamlit run app.py
```

### Páginas disponíveis

| Página | Descrição |
|---|---|
| **Previsão de Rebaixamento** | Simulador individual + Ranking 2025 + Upload CSV em lote |
| **Análise Descritiva** | Exploração interativa da base histórica |
| **Análise de Sensibilidade** | Como cada variável impacta o risco (curvas + heatmap + 3D) |
| **Dados Históricos** | Tabela completa 2014–2025 com filtros |

---

## 10. DESBALANCEAMENTO DE CLASSES

O dataset tem desequilíbrio natural: apenas **~20% dos registros são rebaixamentos** (44 de 220).

**Solução adotada:** `class_weight='balanced'` em todos os modelos — pondera automaticamente as classes inversamente proporcional às frequências, forçando o modelo a aprender o padrão dos rebaixamentos.

---

## 11. TECNOLOGIAS UTILIZADAS

| Biblioteca | Versão | Uso |
|---|---|---|
| `pandas` | — | Manipulação de dados |
| `numpy` | — | Operações numéricas |
| `scikit-learn` | — | Modelos, métricas, pré-processamento |
| `matplotlib` / `seaborn` | — | Geração de gráficos |
| `joblib` | — | Persistência dos modelos |
| `requests` + `BeautifulSoup` | — | Scraping do Transfermarkt |
| `openpyxl` | — | Leitura/escrita de Excel |
| `streamlit` | — | Interface web interativa |
| `plotly` | — | Gráficos interativos no Streamlit |

---

*Relatório gerado automaticamente — TCC Leonardo Feitosa — UFPB 2025*
