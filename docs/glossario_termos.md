# 📚 Glossário de Termos Técnicos

> *Definições dos termos técnicos utilizados neste repositório, especialmente voltado para estudantes que estão tendo o primeiro contato com Ciência de Dados e LaTeX.*

---

## Ciência de Dados e Machine Learning

### Acurácia (Accuracy)
Proporção de predições corretas sobre o total de predições. Cuidado: pode ser enganosa em datasets desbalanceados. Se 95% dos clientes não cancelam, um modelo que sempre prediz "não cancela" terá 95% de acurácia sem aprender nada útil.

### AUC-ROC (Area Under the ROC Curve)
Área sob a curva ROC. Mede a capacidade do modelo de distinguir entre as classes. Varia de 0 a 1, onde 0.5 equivale a um classificador aleatório e 1.0 a um classificador perfeito. Preferível à acurácia em datasets desbalanceados.

### Boosting
Técnica de *ensemble* que treina modelos fracos sequencialmente, onde cada modelo tenta corrigir os erros do anterior. LightGBM e XGBoost são implementações populares.

### Churn
Taxa de evasão ou cancelamento de clientes. Métrica fundamental em negócios baseados em assinatura (telecomunicações, SaaS, streaming). É a variável-alvo do problema de demonstração deste repositório.

### Classificação Binária
Problema de aprendizado supervisionado onde a variável-alvo tem exatamente duas classes possíveis (ex: churn = 0 ou 1, spam ou não-spam, fraude ou legítimo).

### Cross-Validation (Validação Cruzada)
Técnica para estimar o desempenho de um modelo dividindo os dados em K partes (*folds*). O modelo é treinado K vezes, cada vez usando K-1 partes para treino e 1 parte para teste. Reduz o risco de overfitting na avaliação.

### Dataset
Conjunto de dados organizado, geralmente em formato tabular (linhas = observações, colunas = variáveis). Pode ser armazenado em CSV, Parquet, JSON ou em bancos de dados.

### EDA (Exploratory Data Analysis)
Análise Exploratória de Dados. Etapa inicial onde se investiga o dataset por meio de estatísticas descritivas e visualizações para entender padrões, distribuições, correlações e anomalias antes de aplicar modelos.

### Ensemble
Estratégia que combina múltiplos modelos para obter predições melhores que qualquer modelo individual. Random Forest (bagging) e LightGBM (boosting) são exemplos.

### Feature (Variável Preditora)
Variável usada como entrada do modelo para fazer predições. Também chamada de atributo, preditor ou variável independente. No exemplo deste repositório: idade, renda, tempo de conta, etc.

### Feature Engineering (Engenharia de Features)
Processo de criar novas variáveis a partir das existentes para melhorar a capacidade preditiva dos modelos. Exemplo: criar "renda por produto" dividindo renda pelo número de produtos contratados.

### F1-Score
Média harmônica entre Precisão e Recall. Útil quando há desbalanceamento entre as classes e quando tanto falsos positivos quanto falsos negativos são custosos.

### Hiperparâmetros
Configurações do modelo definidas **antes** do treinamento (não aprendidas dos dados). Exemplos: número de árvores no Random Forest, taxa de aprendizado no LightGBM, C na Regressão Logística.

### Imputação
Técnica para preencher valores ausentes (missing values) nos dados. Estratégias comuns: usar a média, mediana (para dados assimétricos) ou moda (para dados categóricos).

### K-Fold (Stratified)
Variação de validação cruzada que garante que cada *fold* mantenha a mesma proporção de classes que o dataset completo. Essencial em problemas com classes desbalanceadas.

### LightGBM
Implementação eficiente de Gradient Boosting pela Microsoft. Usa amostragem baseada em gradiente (GOSS) e agrupamento de features (EFB) para ser mais rápido que implementações tradicionais sem perder acurácia.

### Matriz de Confusão
Tabela que resume o desempenho de um classificador mostrando: Verdadeiros Positivos (TP), Verdadeiros Negativos (TN), Falsos Positivos (FP) e Falsos Negativos (FN).

### Normalização / Padronização
Transformação que coloca as variáveis numa escala comparável. StandardScaler subtrai a média e divide pelo desvio padrão, resultando em variáveis com média 0 e desvio 1. Importante para modelos sensíveis à escala (ex: Regressão Logística).

### One-Hot Encoding
Técnica para converter variáveis categóricas (ex: "Loja Física", "Online") em variáveis binárias (0/1). Cada categoria vira uma nova coluna.

### Overfitting (Sobreajuste)
Quando o modelo memoriza os dados de treino mas não generaliza para dados novos. Sinal: desempenho excelente no treino mas ruim no teste.

### Pipeline
Sequência ordenada de etapas de processamento de dados e modelagem. Neste repositório, a pipeline vai do script 01 (coleta) ao 06 (exportação de figuras).

### Random Forest
Algoritmo de *ensemble* que constrói múltiplas árvores de decisão com amostras *bootstrap* dos dados e seleção aleatória de features em cada nó.

### Recall (Revocação / Sensibilidade)
Proporção de positivos reais que foram corretamente identificados. Em churn: de todos os clientes que realmente cancelaram, quantos o modelo conseguiu prever?

### Reprodutibilidade
Capacidade de outro pesquisador obter exatamente os mesmos resultados usando o mesmo código, dados e configurações. Garantida neste repositório pela seed fixa, scripts versionados e pipeline automatizada.

### Seed (Semente Aleatória)
Número que inicializa o gerador de números pseudo-aleatórios, garantindo que os resultados sejam reproduzíveis. Neste repositório, usamos `SEED = 42` em todos os scripts.

### SMOTE (Synthetic Minority Over-sampling Technique)
Técnica para gerar exemplos sintéticos da classe minoritária, ajudando a balancear o dataset para treino.

### Winsorização
Técnica de tratamento de outliers que substitui valores extremos pelos percentis definidos (ex: P1 e P99). Diferente de remoção: preserva o tamanho do dataset.

---

## LaTeX e Documentação

### ABNT (Associação Brasileira de Normas Técnicas)
Órgão que define as normas de formatação para trabalhos acadêmicos no Brasil. O pacote `abntex2` implementa essas normas no LaTeX.

### abnTeX2
Classe LaTeX que implementa automaticamente as normas ABNT para trabalhos acadêmicos brasileiros. Suporta artigos (`article`), monografias, dissertações e teses.

### BibTeX
Formato para gerenciar referências bibliográficas em LaTeX. As referências são definidas em um arquivo `.bib` e citadas no texto com `\cite{}` ou `\citeonline{}`.

### EPS (Encapsulated PostScript)
Formato de imagem vetorial de alta qualidade, ideal para figuras em documentos LaTeX. Diferente de PNG/JPG (raster), imagens EPS podem ser ampliadas infinitamente sem perda de qualidade.

### latexmk
Ferramenta que automatiza a compilação de documentos LaTeX, executando quantas passadas de `pdflatex` e `bibtex` forem necessárias para resolver todas as referências cruzadas.

---

## Ferramentas e Infraestrutura

### Git
Sistema de controle de versão distribuído. Permite rastrear todas as mudanças no código ao longo do tempo, colaborar com outros pesquisadores e reverter erros.

### .gitignore
Arquivo que informa ao Git quais arquivos ou diretórios devem ser **ignorados** (não versionados). Neste repositório, exclui artefatos regeneráveis como PDFs, modelos treinados e dados processados.

### Makefile
Arquivo que define atalhos para comandos frequentes (ex: `make pipeline`, `make latex`). Automatiza tarefas repetitivas e documenta o fluxo de trabalho do projeto.

### uv
Gerenciador de pacotes Python extremamente rápido (alternativa ao pip). Usado neste repositório para instalar dependências e executar scripts.

### pyproject.toml
Arquivo de configuração do projeto Python que define metadados, dependências e configurações de ferramentas (ruff, pytest). Substitui o antigo `setup.py`.

### Jupyter Notebook
Ambiente interativo que combina código, visualizações e texto em um único documento. Os notebooks deste repositório são versões exploratórias dos scripts.

---

> **💡 Dica:** Se encontrar um termo que não está neste glossário, adicione-o! Este é um documento vivo que cresce com o seu aprendizado.
