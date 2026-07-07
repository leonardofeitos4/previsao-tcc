# 📂 Documentação de Apoio à Pesquisa

> **Templates prontos para organizar seu trabalho acadêmico do início ao fim.**

Este diretório contém modelos em Markdown que você pode copiar e preencher ao longo do seu projeto de pesquisa. Eles complementam os templates LaTeX em `tex/` e os scripts em `scripts/`, cobrindo o **lado organizacional** do trabalho acadêmico: anotações, planejamento, fichamentos e preparação para defesa.

---

## 📋 Templates Disponíveis

| Template | Arquivo | Quando usar |
|----------|---------|-------------|
| 📓 Diário de Pesquisa | [`diario_pesquisa.md`](diario_pesquisa.md) | Registros diários de decisões, leituras e impasses |
| 🧪 Anotação de Experimento | [`anotacao_experimento.md`](anotacao_experimento.md) | Documentar cada experimento com hipótese, configuração e resultado |
| 💡 Brainstorm | [`brainstorm.md`](brainstorm.md) | Sessões de geração de ideias e priorização |
| 📅 Planejamento Semanal | [`planejamento_sprint.md`](planejamento_sprint.md) | Organizar tarefas da semana com metas e retrospectiva |
| 📖 Fichamento | [`fichamento.md`](fichamento.md) | Resumir e analisar artigos e livros lidos |
| 🤝 Reunião de Orientação | [`reuniao_orientacao.md`](reuniao_orientacao.md) | Registrar pauta, decisões e tarefas combinadas |
| ✅ Checklist de Defesa | [`checklist_defesa.md`](checklist_defesa.md) | Verificação final antes da entrega ou defesa |
| ✍️ Guia de Escrita Científica | [`guia_escrita_cientifica.md`](guia_escrita_cientifica.md) | Mini-manual de escrita acadêmica com dicas práticas |
| 📚 Glossário de Termos | [`glossario_termos.md`](glossario_termos.md) | Definições dos termos técnicos usados no repositório |

---

## 🚀 Como Usar

1. **Copie** o template para um novo arquivo com a data ou nome descritivo:
   ```bash
   cp docs/fichamento.md docs/fichamento_hastie2009.md
   cp docs/anotacao_experimento.md docs/exp_001_baseline.md
   ```

2. **Preencha** as seções, removendo as instruções em itálico.

3. **Versione** com Git para manter o histórico das suas anotações:
   ```bash
   git add docs/
   git commit -m "docs: adiciona fichamento de Hastie (2009)"
   ```

> **💡 Dica:** Use uma pasta `docs/fichamentos/`, `docs/experimentos/` etc. se preferir organizar por tipo. A estrutura é livre!
