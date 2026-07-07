# 🧪 Anotação de Experimento

> *Documente cada experimento que você realizar. Um bom registro experimental permite que você (ou outra pessoa) reproduza exatamente o que foi feito e entenda por que determinados resultados foram obtidos.*

---

## Metadados

| Campo | Valor |
|-------|-------|
| **ID do Experimento** | _EXP-001_ |
| **Data** | _AAAA-MM-DD_ |
| **Pesquisador(a)** | _Seu nome_ |
| **Branch do Git** | _ex: feature/smote-balancing_ |
| **Commit** | _ex: abc1234_ |
| **Script(s) executado(s)** | _ex: 03, 04, 05_ |
| **Tempo de execução** | _ex: ~15 minutos_ |

---

## 1. Hipótese

_O que você espera que aconteça e por quê?_

> *Exemplo: "Espero que a aplicação de SMOTE no conjunto de treino melhore o Recall da classe minoritária (churn=1) em pelo menos 10%, possivelmente às custas de uma pequena queda na Precisão, porque o dataset atual tem apenas ~20% de positivos."*

---

## 2. Configuração do Experimento

### Dados utilizados
- **Dataset:** _ex: dados/processados/dataset_treino.csv_
- **Tamanho:** _ex: 800 registros (treino), 200 registros (teste)_
- **Pré-processamento:** _ex: winsorização P1-P99, StandardScaler_

### Modelo(s)
- **Algoritmo:** _ex: LightGBM_
- **Hiperparâmetros:**
  ```
  n_estimators: 200
  max_depth: 6
  learning_rate: 0.05
  ```

### Variáveis de controle
- **Seed:** _42_
- **K-Folds:** _5_
- **Validação:** _Stratified K-Fold_

### O que mudou em relação ao experimento anterior?
- _Ex: "Adicionei SMOTE(k=5) no pipeline de treino (não no teste)"_

---

## 3. Resultados

### Métricas principais

| Métrica | Valor anterior | Valor atual | Δ |
|---------|---------------|-------------|---|
| AUC-ROC | _0.877_ | _0.891_ | _+0.014_ |
| F1-Score | _0.612_ | _0.658_ | _+0.046_ |
| Acurácia | _0.825_ | _0.810_ | _-0.015_ |
| Recall | _0.543_ | _0.672_ | _+0.129_ |

### Figuras geradas
- _ex: resultados/figuras/curva_roc_exp001.png_
- _ex: resultados/figuras/matriz_confusao_exp001.png_

### Observações
- _O que chamou atenção nos resultados?_
- _Algo inesperado?_

---

## 4. Análise e Conclusão

_A hipótese foi confirmada? O que os resultados significam?_

> *Exemplo: "A hipótese foi parcialmente confirmada. O Recall melhorou 12.9 pontos percentuais, acima do esperado. Porém, a Acurácia caiu 1.5 p.p., o que é aceitável no contexto de previsão de churn (falsos negativos são mais custosos que falsos positivos)."*

---

## 5. Próximos Passos

- [ ] _Ex: Testar com k=3 e k=7 no SMOTE para avaliar sensibilidade_
- [ ] _Ex: Registrar os resultados na seção de Resultados do main.tex_
- [ ] _Ex: Gerar tabela LaTeX atualizada com script 05_

---

> **💡 Dica:** Numere seus experimentos sequencialmente (EXP-001, EXP-002...) e salve cada anotação com o ID no nome do arquivo: `docs/exp_001_baseline.md`, `docs/exp_002_smote.md`, etc.
