# Relatório Completo do Projeto
## Previsão de Rebaixamento no Brasileirão Série A — TCC

**Aluno:** Leonardo Feitosa Barroso  
**Curso:** Ciência de Dados — UFPB  
**Ano:** 2025  

---

## 1. VISÃO GERAL DO PROJETO

O projeto tem como objetivo prever quais clubes têm maior risco de rebaixamento no **Brasileirão Série A 2025**, utilizando dados financeiros e de elenco coletados do site **Transfermarkt**.

Foram treinados e comparados **3 modelos de classificação binária**:
- Regressão Logística
- Random Forest
- Support Vector Machine (SVM)

A variável-alvo é binária seguindo a convenção estatística padrão:  
**1 = Rebaixado** (evento de interesse) | **0 = Permaneceu na Série A** (referência)

---

## 2. ESTRUTURA DE ARQUIVOS

```
Previsao-Tcc/
│
├── app.py                          ← Entrada principal do Streamlit
├── requirements.txt                ← Dependências do projeto
├── runtime.txt                     ← Versão Python (3.11.9) para Streamlit Cloud
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
│   ├── distribuicao_status_bin.png ← Pizza: proporção Rebaixado/Permaneceu
│   ├── pontos_por_situacao.png     ← Histograma de pontos por situação
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
- **Coleta:** Python com `requests` + `BeautifulSoup`
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
| `Status_bin` | int | **1 = Rebaixado, 0 = Permaneceu** |

### Features usadas no modelo
- `Plantel`
- `Estrangeiros`
- `Valor de Mercado Total`

---

## 4. CORREÇÕES REALIZADAS

### 4.1 Encoding da variável-alvo (Status_bin)

**Problema:** O encoding original era `0 = Rebaixado, 1 = Permaneceu`, invertendo a convenção estatística padrão da Regressão Logística, onde `1` deve representar o evento de interesse.

**Solução:** Corrigido para `1 = Rebaixado, 0 = Permaneceu` em todos os notebooks (00 a 07) e no Streamlit.

---

### 4.2 Probabilidades invertidas no Streamlit

**Problema:** Com o encoding corrigido (`1 = Rebaixado`), o `predict_proba` do sklearn retorna:
- `probs[:, 0]` → probabilidade de **Permaneceu** (classe 0)
- `probs[:, 1]` → probabilidade de **Rebaixado** (classe 1)

O Streamlit estava usando `probs[:, 0]` como prob. de rebaixamento — completamente invertido.

**Solução:** Corrigido para `probs[:, 1]` em:
- `app/paginas/previsao.py`
- `app/paginas/analise_sensibilidade.py`
- `app/utils/processamento.py`

---

### 4.3 Métricas incorretas na sidebar e página de previsão

**Problema:** Acurácia exibida era 89% e AUC-ROC 0.94 — valores incorretos, hardcoded de versão anterior.

**Solução:** Corrigido para os valores reais calculados no teste 2023–2024:
- Acurácia: **77,5%**
- AUC-ROC: **0.82**

Arquivos: `app/controllers/sidebar.py` e `app/paginas/previsao.py`

---

### 4.4 Padronização de nomes de clubes via NOME_MAP

**Problema:** O Transfermarkt usa nomes diferentes para o mesmo clube nas páginas de elenco e classificação (ex: `"CR Flamengo"` vs `"Flamengo"`), quebrando o merge e gerando Pontos = NaN.

**Solução:** Dicionário `NOME_MAP` com 70+ entradas + função `normalizar_nome()` com remoção de acentos via `unicodedata`, aplicada em ambos os scrapers antes do merge.

---

### 4.5 Convenção de URLs do Transfermarkt

**Problema:** `saison_id = Temporada` retornava dados errados (ex: temporada 2024 retornava standings parciais de 2025).

**Solução:** `saison_id = Temporada - 1` aplicado em ambas as funções de scraping (`fn_elenco` e `fn_pontos`).

---

### 4.6 Rótulos de rebaixamento corrigidos via dicionário REBAIXADOS

**Problema:** A `Situacao` derivada automaticamente da posição na tabela tinha erros pontuais.

**Solução:** Dicionário `REBAIXADOS` hardcoded com os 4 rebaixados reais de cada temporada (2014–2024), sobrescrevendo o valor derivado do scraping.

```python
REBAIXADOS = {
    2014: ["Bahia", "Botafogo", "Criciuma", "Vitoria"],
    2015: ["Avai", "Goias", "Joinville", "Vasco da Gama"],
    # ... 2016 a 2024
    2024: ["Athletico Paranaense", "Atletico Goianiense", "Criciuma", "Cuiaba"],
}
```

---

### 4.7 Notebooks 04 e 05 — modelos inexistentes

**Problema:** Os notebooks 04 e 05 tentavam `joblib.load()` de arquivos `random_forest.pkl` e `svm.pkl` que haviam sido deletados.

**Solução:** Substituídas as células de carregamento por treinamento direto inline (igual ao notebook 03), com geração das imagens e salvamento dos `.pkl` ao final.

---

### 4.8 Requirements.txt para deploy no Streamlit Cloud

**Problema:** `selenium`, `webdriver-manager` e `beautifulsoup4` causavam falha no install do Cloud (sem Chrome disponível).

**Solução:** Removidos os pacotes de scraping do `requirements.txt` (usados apenas localmente nos notebooks) e relaxadas as versões fixas para intervalos compatíveis.

---

## 5. NOTEBOOKS — O QUE CADA UM FAZ

### 00_coleta_dados.ipynb
1. Exibe URLs de scraping (convenção `saison_id = Temporada - 1`)
2. Define `NOME_MAP` + `normalizar_nome()` para padronização de nomes
3. `coletar_elenco_temporada(ano)` — scrapa plantel de cada clube
4. `coletar_pontos_temporada(ano)` — scrapa pontos e deriva Situação pela posição
5. Merge por `[Clube, Temporada]`
6. Aplica dicionário `REBAIXADOS` para corrigir rótulos
7. Cria `Status_bin` (1=Rebaixado, 0=Permaneceu)
8. Verifica Pontos (zero NaN esperado em 2014–2024)
9. Gera gráficos: pizza de Status_bin + histograma de pontos por situação
10. Salva `BASE_FINAL.xlsx`

### 01_analise_exploratoria.ipynb
- Distribuição das variáveis por temporada
- Correlações entre features e Status_bin
- Boxplots: rebaixados vs permaneceram
- Histogramas de distribuição das features por situação final

### 02_preprocessamento.ipynb
- Separação temporal treino/teste (sem aleatoriedade):
  - **Treino:** 2014–2022 (180 registros, 36 rebaixados)
  - **Teste:** 2023–2024 (40 registros, 8 rebaixados)
  - **Previsão:** 2025 (20 registros, sem rótulo)
- Aplicação do `StandardScaler` (ajuste apenas no treino)
- Visualização da divisão temporal

### 03_modelo_logistica.ipynb
- Treinamento com `class_weight='balanced'`, `max_iter=1000`
- Matriz de confusão, relatório de classificação, curva ROC
- Coeficientes do modelo
- Salva: `modelos/logistica.pkl` e `modelos/scaler_logistica.pkl`

### 04_modelo_random_forest.ipynb
- Treina RF com 300 árvores, `class_weight='balanced'`
- Matriz de confusão, curva ROC, importância das features
- Salva: `modelos/random_forest.pkl` e `modelos/scaler_rf.pkl`

### 05_modelo_svm.ipynb
- Treina SVM com kernel RBF, `C=1.0`, `gamma='scale'`, `probability=True`
- Matriz de confusão, curva ROC, tabela de probabilidades
- Salva: `modelos/svm.pkl` e `modelos/scaler_svm.pkl`

### 06_comparacao_modelos.ipynb
- Carrega os 3 modelos e compara no mesmo conjunto de teste
- Gráfico de barras comparativo de métricas
- Curvas ROC sobrepostas
- Matrizes de confusão lado a lado
- Justificativa da escolha da Regressão Logística como modelo final

### 07_previsao_2025.ipynb
- Carrega modelo final (Regressão Logística)
- Aplica nos 20 clubes da temporada 2025
- Gera ranking de probabilidade de rebaixamento
- Salva `img/previsao_2025.png`

---

## 6. SEPARAÇÃO TEMPORAL (SEM DATA LEAKAGE)

| Conjunto | Período | Registros | Rebaixados |
|---|---|---|---|
| Treino | 2014–2022 | 180 | 36 |
| Teste | 2023–2024 | 40 | 8 |
| Previsão | 2025 | 20 | — |

---

## 7. RESULTADOS DOS MODELOS

Métricas no conjunto de teste (2023–2024):

| Modelo | Acurácia | MAE | RMSE | AUC-ROC |
|---|---|---|---|---|
| **Regressão Logística** | 77,5% | 0.2250 | 0.4743 | **0.82** |
| Random Forest | 77,5% | 0.2250 | 0.4743 | 0.70 |
| SVM | 77,5% | 0.2250 | 0.4743 | 0.68 |

### Por que a Regressão Logística foi escolhida?

1. **Maior AUC (0.82)** — melhor capacidade de distinguir rebaixados de não-rebaixados
2. **Interpretabilidade** — coeficientes revelam diretamente o peso de cada variável
3. **Adequação ao problema** — variável binária, poucas features numéricas
4. **AUC é a métrica mais relevante** para problemas com classes desbalanceadas

### Coeficientes da Regressão Logística (features padronizadas)

| Feature | Coeficiente | Interpretação |
|---|---|---|
| `Valor de Mercado Total` | −1.135 | Maior valor → **menor** risco de rebaixamento |
| `Plantel` | +0.549 | Plantel maior → ligeiramente maior risco (elencos inchados) |
| `Estrangeiros` | −0.067 | Pouco impacto isolado |

---

## 8. PREVISÃO 2025

Top 8 clubes por probabilidade de rebaixamento (Regressão Logística):

| Posição | Clube | Prob. Rebaixamento |
|---|---|---|
| 1º | Sport Recife | 65,4% |
| 2º | Vitória | 64,0% |
| 3º | Juventude | 54,9% |
| 4º | Mirassol | 49,0% |
| 5º | Ceará | 36,3% |
| 6º | Fluminense | 26,0% |
| 7º | Fortaleza | 24,6% |
| 8º | Bahia | 23,8% |

> **Nota:** Mirassol aparece em 4º por ser a primeira participação histórica na Série A, com elenco e valor de mercado abaixo da média da competição.

> **Limitações:** O modelo usa apenas dados de elenco e valor de mercado registrados no início da temporada. Não considera lesões, mudanças técnicas, calendário ou desempenho em campo.

---

## 9. APLICAÇÃO STREAMLIT

- **Deploy:** https://previsao-tcc-tfdykpjzhid7qj7cqquwbr.streamlit.app/
- **Repositório:** https://github.com/leonardofeitos4/previsao-tcc

Para executar localmente:
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

O dataset tem desequilíbrio natural: apenas **~20% dos registros são rebaixamentos** (44 de 220 casos rotulados).

**Solução adotada:** `class_weight='balanced'` em todos os modelos.

---

## 11. TECNOLOGIAS UTILIZADAS

| Biblioteca | Uso |
|---|---|
| `pandas` | Manipulação de dados |
| `numpy` | Operações numéricas |
| `scikit-learn` | Modelos, métricas, pré-processamento |
| `matplotlib` / `seaborn` | Geração de gráficos nos notebooks |
| `joblib` | Persistência dos modelos |
| `requests` + `BeautifulSoup` | Scraping do Transfermarkt |
| `openpyxl` | Leitura/escrita de Excel |
| `streamlit` | Interface web interativa |
| `plotly` | Gráficos interativos no Streamlit |

---

*TCC — Leonardo Feitosa Barroso — Ciência de Dados — UFPB — 2025*
