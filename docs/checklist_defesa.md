# ✅ Checklist de Preparação para Defesa / Entrega

> *Use este checklist nas semanas finais do seu projeto para garantir que nada foi esquecido. Marque cada item conforme for verificando. Um trabalho bem revisado transmite profissionalismo e competência.*

---

**Tipo de documento:** ☐ TCC Artigo · ☐ TCC Monografia · ☐ Dissertação · ☐ Tese · ☐ Outro: ___  
**Data da entrega/defesa:** _DD/MM/AAAA_  
**Data desta revisão:** _DD/MM/AAAA_

---

## 📄 Formatação e Normas ABNT

### Estrutura do Documento
- [ ] Capa com instituição, título, autor e data corretos
- [ ] Resumo em português com palavras-chave (150-500 palavras para TCC/dissertação)
- [ ] Abstract em inglês com keywords
- [ ] Sumário gerado automaticamente e atualizado
- [ ] Lista de figuras atualizada
- [ ] Lista de tabelas atualizada
- [ ] Numeração de páginas correta (pretextual em romanos, textual em arábicos)

### Formatação de Texto
- [ ] Fonte tamanho 12 (corpo) e 10 (citações longas, notas de rodapé)
- [ ] Margens: superior 3cm, esquerda 3cm, inferior 2cm, direita 2cm
- [ ] Espaçamento entrelinhas 1,5 (corpo) e simples (citações longas)
- [ ] Parágrafos com recuo de primeira linha
- [ ] Títulos de seções/capítulos em negrito e numerados

### Referências e Citações
- [ ] Todas as citações no texto possuem entrada correspondente nas Referências
- [ ] Todas as entradas das Referências são citadas no texto
- [ ] Formato de citação consistente (ABNT alfanumérico)
- [ ] Citações diretas com mais de 3 linhas estão recuadas (4cm)
- [ ] Citações diretas incluem número de página
- [ ] `\citeonline{}` usado quando o autor é sujeito da frase
- [ ] `\cite{}` usado para citações indiretas ao final do período
- [ ] Arquivo `referencias.bib` sem entradas duplicadas

### Figuras e Tabelas
- [ ] Toda figura/tabela é referenciada no texto **antes** de aparecer
- [ ] Figuras em formato vetorial (.eps) para qualidade tipográfica
- [ ] Legendas informativas (não apenas "Gráfico 1")
- [ ] Fonte indicada abaixo de cada figura/tabela
- [ ] Tabelas usam `\toprule`, `\midrule`, `\bottomrule` (sem linhas verticais)
- [ ] Numeração sequencial correta

---

## 📊 Conteúdo Científico

### Introdução
- [ ] Contextualização do tema
- [ ] Problema de pesquisa claramente formulado
- [ ] Justificativa (relevância)
- [ ] Objetivo geral
- [ ] Objetivos específicos (mensuráveis)
- [ ] Estrutura do trabalho descrita

### Fundamentação Teórica
- [ ] Referências atualizadas (últimos 5 anos quando possível)
- [ ] Conceitos-chave definidos
- [ ] Estado da arte apresentado
- [ ] Trabalhos correlatos discutidos (não apenas listados)
- [ ] Síntese crítica (não apenas "colagem" de citações)

### Metodologia
- [ ] Tipo de pesquisa classificado
- [ ] Fonte e volume dos dados descritos
- [ ] Pré-processamento detalhado (reprodutível)
- [ ] Algoritmos com hiperparâmetros informados
- [ ] Estratégia de validação descrita (K-Fold, holdout, etc.)
- [ ] Métricas de avaliação justificadas
- [ ] Seed aleatória informada

### Resultados e Discussão
- [ ] Cada tabela/figura é interpretada no texto
- [ ] Resultados conectados com a literatura (fundamentação)
- [ ] Padrões inesperados discutidos
- [ ] Limitações dos resultados reconhecidas

### Conclusão
- [ ] Objetivos retomados e avaliados
- [ ] Contribuições sintetizadas
- [ ] Limitações do estudo listadas
- [ ] Trabalhos futuros concretos propostos
- [ ] Não introduz argumentos novos

---

## 💻 Reprodutibilidade (Pipeline)

- [ ] `make pipeline` executa sem erros do início ao fim
- [ ] `make latex DOC=<tipo>` compila o PDF sem erros
- [ ] Seed fixa em todos os scripts (`SEED = 42`)
- [ ] Dados brutos estão disponíveis (no repositório ou com link de download)
- [ ] `pyproject.toml` / `requirements.txt` atualizado com todas as dependências
- [ ] `.gitignore` exclui artefatos regeneráveis
- [ ] Repositório Git limpo (sem arquivos temporários)
- [ ] README.md atualizado com instruções de execução

---

## ✍️ Revisão Textual

- [ ] Revisão ortográfica completa (usar corretor automático + leitura manual)
- [ ] Concordância verbal e nominal verificada
- [ ] Eliminação de gerundismo ("está sendo utilizado" → "utiliza-se")
- [ ] Eliminação de repetições excessivas
- [ ] Parágrafos com pelo menos 3 frases
- [ ] Coerência entre seções (sem contradições)
- [ ] Termos técnicos em itálico na primeira ocorrência (ex: *churn*, *Machine Learning*)
- [ ] Siglas definidas na primeira aparição (ex: Inteligência Artificial (IA))
- [ ] Texto impessoal e objetivo (sem "eu acho", "nós pensamos")

---

## 🎤 Preparação para Defesa (se aplicável)

- [ ] Slides preparados (15-20 para TCC, 25-35 para dissertação)
- [ ] Slides cobrem: motivação, objetivo, metodologia, resultados, conclusão
- [ ] Ensaio da apresentação feito (cronometrar: 15-20min TCC, 30-45min dissertação)
- [ ] Perguntas frequentes da banca preparadas e praticadas
- [ ] Versão impressa do trabalho disponível (se exigido)
- [ ] Equipamento de apresentação testado (projetor, notebook, adaptadores)

---

## 📬 Entrega

- [ ] PDF final revisado uma última vez
- [ ] PDF enviado ao orientador para aprovação final
- [ ] PDF enviado à coordenação/secretaria no prazo
- [ ] Repositório Git com tag de versão final (`git tag v1.0-entrega`)
- [ ] Backup do repositório feito (nuvem ou HD externo)

---

> **💡 Dica final:** Peça para alguém que **não** é da sua área ler o Resumo e a Introdução. Se essa pessoa entender o propósito do trabalho, você acertou na clareza.
