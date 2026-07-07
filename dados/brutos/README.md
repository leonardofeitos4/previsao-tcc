# 📥 Dados Brutos (Raw Data)

> **Este diretório contém os dados originais, exatamente como foram coletados. Eles NUNCA devem ser modificados manualmente.**

---

## 📋 Dataset de Demonstração

O dataset padrão deste repositório é gerado pelo script `01_coleta_dados.py` e simula dados de **churn de clientes de telecomunicações**.

### `dataset_clientes.csv`

| Campo | Tipo | Descrição | Valores / Faixa |
|-------|------|-----------|----------------|
| `id_cliente` | Inteiro | Identificador único | 1 a 1000 |
| `idade` | Inteiro | Idade do cliente em anos | 18 a 70 |
| `sexo` | Categórico | Sexo biológico | M, F |
| `renda_mensal` | Contínuo | Renda mensal em R$ | ~2.500 a ~15.000 (log-normal) |
| `tempo_conta_meses` | Inteiro | Tempo como cliente (meses) | 1 a 120 |
| `num_produtos` | Inteiro | Produtos contratados | 1 a 4 |
| `tem_credito` | Binário | Possui crédito especial | 0 (não), 1 (sim) |
| `saldo` | Contínuo | Saldo médio em conta (R$) | ~0 a ~250.000 (exponencial) |
| `ativo` | Binário | Cliente está ativo | 0 (inativo), 1 (ativo) |
| `canal_aquisicao` | Categórico | Canal de aquisição | Loja Física, Online, Telefone, Indicação |
| `num_reclamacoes` | Inteiro | Reclamações abertas (12 meses) | 0 a ~8 |
| `satisfacao` | Ordinal | Nível de satisfação | 1 (muito insatisfeito) a 5 (muito satisfeito) |
| `churn` | Binário | **Variável-alvo**: evadiu-se? | 0 (não), 1 (sim) |

### Características do dataset
- **Registros:** 1.000
- **Valores ausentes:** ~5% em `renda_mensal`, ~3% em `satisfacao` (intencionais, para demonstrar imputação)
- **Desbalanceamento:** ~80% não-churn, ~20% churn
- **Seed:** 42 (reprodutível)

---

## 📝 Como Documentar Seus Próprios Dados

Ao substituir o dataset de demonstração pelo seu, documente aqui:

### Template de Documentação de Dados

```markdown
### Nome do arquivo: `meu_dataset.csv`

**Fonte:** [De onde veio? API, pesquisa de campo, base pública...]
**Data de coleta:** [DD/MM/AAAA]
**Responsável pela coleta:** [Nome]
**Tamanho:** [X registros × Y colunas]
**Formato:** [CSV, JSON, Parquet...]
**Encoding:** [UTF-8, Latin-1...]
**Separador:** [vírgula, ponto-e-vírgula, tab...]

**Descrição das variáveis:**
| Campo | Tipo | Descrição | Valores |
|-------|------|-----------|---------|
| ... | ... | ... | ... |

**Observações:**
- [Valores ausentes conhecidos?]
- [Dados sensíveis? Anonimizados?]
- [Restrições de uso / licença?]
```

---

## ⚠️ Regras Importantes

1. **Nunca edite** arquivos neste diretório manualmente
2. **Nunca sobrescreva** com dados processados — use `dados/processados/` para isso
3. Este diretório está no `.gitignore` por padrão (dados podem ser grandes). Para dados pequenos (<50MB), remova a linha correspondente do `.gitignore`
4. Para datasets grandes, considere Git LFS ou hospedagem externa (ver README principal)
