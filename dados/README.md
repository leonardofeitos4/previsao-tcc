# 📦 Diretório de Dados

> **Organização dos dados do projeto seguindo boas práticas de Ciência de Dados reprodutível.**

Este diretório segue a separação fundamental entre dados **brutos** (imutáveis) e dados **processados** (regeneráveis):

```
dados/
├── brutos/          ← Dados originais, NUNCA modificados manualmente
│   └── .gitkeep
├── processados/     ← Dados gerados pelos scripts, regeneráveis
│   └── .gitkeep
└── README.md        ← Você está aqui
```

---

## 🔒 Regra de Ouro: Dados Brutos São Imutáveis

Os dados em `brutos/` representam a **fonte da verdade** do seu projeto. Eles:

- **Nunca** são editados manualmente após a coleta
- **Nunca** são sobrescritos por scripts de pré-processamento
- São a base para **toda** a pipeline ser reproduzível

Se você precisa limpar, transformar ou filtrar dados, faça isso nos scripts e salve o resultado em `processados/`.

---

## 📂 Subdiretórios

| Diretório | Conteúdo | Versionado no Git? | Gerado por |
|-----------|----------|:-------------------:|------------|
| `brutos/` | Dados originais (CSV, JSON, Parquet) | Depende do tamanho* | Script 01 ou coleta manual |
| `processados/` | Dados limpos, treino/teste | ❌ (regeneráveis) | Scripts 03+ |

\* Ver seção "Versionamento de Dados" no README principal.

---

## 🔄 Fluxo dos Dados

```
              Script 01                 Script 03
Fonte  ──────────────────►  brutos/  ──────────────────►  processados/
(API, CSV, web scraping)     │                              │
                             │                              ├── dataset_processado.csv
                             │                              ├── dataset_treino.csv
                             └── dataset_clientes.csv       └── dataset_teste.csv
```

---

## 📋 Para Seu Projeto

Ao adaptar este repositório para seu trabalho:

1. **Substitua** o dataset de demonstração em `brutos/` pelo seu dataset real
2. **Documente** a proveniência dos dados (ver template em `brutos/README.md`)
3. **Adapte** os scripts de pré-processamento para suas variáveis
4. **Mantenha** a separação brutos/processados — é a base da reprodutibilidade
