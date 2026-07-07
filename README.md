# ⚽ Previsão de Rebaixamento — Brasileirão Série A (TCC)

> **TCC — Ciência de Dados, UFPB/CCSA** · Leonardo Feitosa Barroso · Orientador: Prof. Hilton Martins

Este repositório contém o Trabalho de Conclusão de Curso sobre **previsão de rebaixamento no Campeonato Brasileiro Série A** com técnicas de *Machine Learning*, organizado segundo o padrão do repositório-modelo [lema-ufpb/modelo-academico](https://github.com/lema-ufpb/modelo-academico), com foco em **reprodutibilidade** e boas práticas.

🔗 **Aplicativo online (Streamlit):**
👉 [previsao-rebaixamentobrasileirao2025-seriea.streamlit.app](https://previsao-rebaixamentobrasileirao2025-seriea.streamlit.app/)

---

## 🧠 Sobre o Projeto

Quatro modelos de classificação binária — **Regressão Logística, Random Forest, XGBoost e LightGBM** — são comparados sobre **15 features** que combinam:

- **Dados de elenco** (Transfermarkt): plantel, estrangeiros, valor de mercado total
- **Janelas deslizantes**: médias de desempenho (pontos, saldo de gols, gols pró/contra, vitórias, aproveitamento) das últimas 3 e 5 temporadas, calculadas com `shift(1).rolling()` para evitar *data leakage*

**Metodologia:** validação *walk-forward* (5 folds temporais, 2014–2022) + otimização com `RandomizedSearchCV` + `TimeSeriesSplit`, avaliação final em conjunto de teste independente (2023–2024).

**Resultados no teste (2023–2024):**

| Rank | Modelo | AUC-ROC | Acurácia |
|---|---|---|---|
| 1º | **LightGBM** | **0.877** | 82,5% |
| 2º | Random Forest | 0.844 | 80,0% |
| 3º | Regressão Logística | 0.828 | 80,0% |
| 4º | XGBoost | 0.652 | 82,5% |

A **Regressão Logística** é o modelo final adotado para a previsão 2025, pela maior estabilidade temporal no walk-forward (0.794 ± 0.058) e pela interpretabilidade dos coeficientes.

---

## 📂 Estrutura do Repositório

```text
previsao-tcc/
├── README.md                       ← Você está aqui
│
├── dados/
│   ├── brutos/                     ← Dados originais coletados (imutáveis)
│   │   ├── dados_brutos_transfermarkt.xlsx
│   │   ├── tabela_classificacao_brasileirao.csv
│   │   └── tabela_desempenho_brasileirao.xlsx
│   └── processados/
│       └── BASE_FINAL.xlsx         ← Base final (fonte única de verdade)
│
├── notebooks/                      ← Pipeline de análise (00 a 07)
│   ├── 00_coleta_dados.ipynb       ← Web scraping do Transfermarkt
│   ├── 01_analise_exploratoria.ipynb
│   ├── 02_preprocessamento.ipynb   ← 15 features + janelas deslizantes
│   ├── 03_modelo_logistica.ipynb   ← Walk-forward + tuning
│   ├── 04_modelo_random_forest.ipynb
│   ├── 05_modelo_svm.ipynb
│   ├── 06_comparacao_modelos.ipynb ← 4 modelos: LR, RF, XGBoost, LightGBM
│   └── 07_previsao_2025.ipynb      ← Previsão final da temporada 2025
│
├── scripts/                        ← Scripts auxiliares
│   ├── gerar_figuras_artigo.py     ← Regenera as figuras do artigo a partir dos modelos salvos
│   ├── gerar_relatorio_v2.py
│   └── gerar_app_real.py
│
├── modelos/                        ← Modelos treinados (.pkl) + scaler + medianas
│
├── resultados/
│   ├── figuras/                    ← Gráficos gerados (ROC, matrizes, previsão 2025...)
│   └── relatorios/                 ← Relatórios técnicos (HTML/DOCX)
│
├── tex/
│   └── tcc_artigo/                 ← 📄 ARTIGO DO TCC (LaTeX, ABNT via abntex2)
│       ├── main.tex                ← Texto completo do artigo
│       ├── referencias.bib         ← Referências bibliográficas
│       ├── figuras/                ← Figuras do artigo
│       └── tabelas/                ← Tabelas em .tex incluídas no texto
│
├── docs/                           ← Templates de gestão da pesquisa (modelo LEMA-UFPB)
│   ├── guia_escrita_cientifica.md
│   ├── diario_pesquisa.md
│   ├── reuniao_orientacao.md
│   └── checklist_defesa.md ...
│
├── app.py                          ← Aplicativo Streamlit (entrada principal)
├── app/                            ← Código do aplicativo (páginas, utils, controllers)
├── requirements.txt                ← Dependências do app
└── runtime.txt                     ← Versão do Python (Streamlit Cloud)
```

---

## 📄 Compilar o Artigo (LaTeX)

O artigo está em `tex/tcc_artigo/main.tex`, no formato **TCC-artigo** com classe `abntex2` (normas ABNT). Para compilar:

```bash
cd tex/tcc_artigo
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Requisitos: distribuição LaTeX ([MiKTeX](https://miktex.org/download) no Windows) com os pacotes `abntex2` e `abntex2cite`. Alternativa sem instalação: [Overleaf](https://www.overleaf.com) (envie a pasta `tex/tcc_artigo/`) ou [Tectonic](https://tectonic-typesetting.github.io).

Para regenerar as figuras do artigo a partir dos modelos salvos:

```bash
python scripts/gerar_figuras_artigo.py
```

---

## 🖥️ Executar o Aplicativo Streamlit

1. *(Opcional)* Crie um ambiente virtual:
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # macOS/Linux
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute:
   ```bash
   streamlit run app.py
   ```

### Páginas do aplicativo

| Página | Descrição |
|---|---|
| **Previsão de Rebaixamento** | Simulador individual + Ranking 2025 + Upload CSV em lote |
| **Análise Descritiva** | Exploração interativa da base histórica |
| **Análise de Sensibilidade** | Impacto de cada variável no risco previsto |
| **Dados Históricos** | Tabela completa 2014–2025 com filtros |

---

## 🔁 Reprodutibilidade

- Semente aleatória fixa (`random_state=42`) em todos os experimentos
- Separação temporal estrita: treino 2014–2022 · teste 2023–2024 · previsão 2025
- Imputação (mediana) e `StandardScaler` ajustados **somente no treino** — sem *data leakage*
- Dados brutos imutáveis em `dados/brutos/`; pipeline completo nos notebooks 00→07
