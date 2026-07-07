# 🔄 Dados Processados

> **Este diretório contém dados gerados automaticamente pelos scripts. Todos os arquivos aqui são REGENERÁVEIS e estão no `.gitignore`.**

---

## 📋 Arquivos Gerados

Os seguintes arquivos são produzidos pelo script `03_preprocessamento.py`:

| Arquivo | Gerado por | Descrição |
|---------|-----------|-----------|
| `dataset_processado.csv` | Script 03 | Dataset completo após limpeza, encoding e feature engineering |
| `dataset_treino.csv` | Script 03 | Subconjunto de treino (80%) com features normalizadas |
| `dataset_teste.csv` | Script 03 | Subconjunto de teste (20%) com features normalizadas |

### Transformações aplicadas (Script 03)

1. **Imputação de valores ausentes:** mediana (renda_mensal), moda (satisfacao)
2. **Tratamento de outliers:** winsorização nos percentis P1 e P99
3. **Feature engineering:** renda_por_produto, reclamacao_por_tempo, faixa_etaria, cliente_premium
4. **Codificação:** One-Hot Encoding para variáveis categóricas (sexo, canal_aquisicao, faixa_etaria)
5. **Normalização:** StandardScaler nas variáveis numéricas contínuas
6. **Divisão:** Stratified train/test split (80%/20%, seed=42)

---

## ⚠️ Importante

- **Não edite** estes arquivos manualmente — eles são regenerados por `make pipeline`
- **Não versione** no Git — estão no `.gitignore` porque são regeneráveis
- Se precisar de dados limpos para análise ad-hoc, execute `uv run python scripts/03_preprocessamento.py`
