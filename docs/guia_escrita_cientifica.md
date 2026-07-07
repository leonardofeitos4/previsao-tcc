# ✍️ Guia de Escrita Científica

> *Mini-manual prático para estudantes que precisam escrever textos acadêmicos com clareza, precisão e rigor. Não é um tratado de metodologia — é um companheiro de escrita.*

---

## Sumário

1. [Princípios Gerais](#1-princípios-gerais)
2. [Escrevendo Cada Seção](#2-escrevendo-cada-seção)
3. [Linguagem Acadêmica](#3-linguagem-acadêmica)
4. [Verbos e Tempos Verbais](#4-verbos-e-tempos-verbais)
5. [Conectivos e Transições](#5-conectivos-e-transições)
6. [Citações no Padrão ABNT](#6-citações-no-padrão-abnt)
7. [Erros Comuns e Como Evitá-los](#7-erros-comuns-e-como-evitá-los)
8. [Dicas Finais de Revisão](#8-dicas-finais-de-revisão)

---

## 1. Princípios Gerais

### A regra de ouro: Clareza acima de tudo

Um texto científico não precisa ser complicado para ser profundo. Na verdade, quanto mais claro, melhor. Se o leitor precisa reler uma frase três vezes, o problema é do texto, não do leitor.

**Antes (ruim):**
> "A utilização de metodologias computacionais baseadas em algoritmos de aprendizado de máquina supervisionado para a realização de tarefas de classificação binária tem sido amplamente empregada na literatura recente."

**Depois (bom):**
> "Algoritmos de aprendizado supervisionado são amplamente utilizados para classificação binária."

### Três pilares do texto científico

| Pilar | Significado | Exemplo |
|-------|-------------|---------|
| **Objetividade** | Fatos, não opiniões | ❌ "O LightGBM é incrível" → ✅ "O LightGBM obteve AUC de 0,91" |
| **Impessoalidade** | Sem primeira pessoa | ❌ "Eu treinei o modelo" → ✅ "O modelo foi treinado" |
| **Precisão** | Dados concretos, não vagos | ❌ "A acurácia foi boa" → ✅ "A acurácia foi de 82,5%" |

### Estrutura de um parágrafo científico

Um bom parágrafo segue a estrutura **TED**:
1. **T**ópico: Primeira frase apresenta a ideia central do parágrafo.
2. **E**vidência: Frases seguintes desenvolvem com dados, citações ou argumentos.
3. **D**esfecho: Última frase conclui ou faz a transição para o próximo parágrafo.

> ⚠️ **Regra prática:** Cada parágrafo deve ter no mínimo 3 frases. Se tem 1-2 frases, provavelmente precisa ser expandido ou mesclado com outro.

---

## 2. Escrevendo Cada Seção

### 2.1 Resumo / Abstract

O resumo é o cartão de visitas do seu trabalho. Muitos leitores (e avaliadores!) decidem se vão ler o trabalho inteiro com base apenas no resumo.

**Estrutura recomendada (IMRAD):**

| Elemento | O que escrever | Extensão |
|----------|---------------|----------|
| **Contexto** | Qual é o problema? | 1-2 frases |
| **Objetivo** | O que o trabalho faz? | 1 frase |
| **Método** | Como foi feito? | 1-2 frases |
| **Resultados** | O que foi encontrado? | 1-2 frases (com números!) |
| **Conclusão** | O que significa? | 1 frase |

**Tamanho recomendado:** 150-250 palavras (TCC/artigo) · 250-500 palavras (dissertação/tese).

**Dica fundamental:** Escreva o resumo **por último**, quando todo o trabalho estiver pronto.

### 2.2 Introdução

A introdução funciona como um **funil**: começa largo (contexto geral) e vai estreitando até o problema específico.

**Perguntas que a Introdução deve responder:**
1. **Qual é o tema?** — Contextualize em 1-2 parágrafos.
2. **Por que é importante?** — Justifique com dados ou referências.
3. **O que ainda não sabemos?** — Identifique a lacuna (gap) na literatura.
4. **O que este trabalho faz?** — Apresente o objetivo geral.
5. **Quais são os objetivos específicos?** — Liste de forma mensurável.
6. **Como o texto está organizado?** — Descreva a estrutura dos capítulos/seções.

**Erro fatal:** Começar a Introdução com a definição do termo central. ❌ "Machine Learning é uma subárea da IA que..." — Isso é fundamentação teórica, não introdução. Na introdução, **contextualize o problema**.

**Tamanho recomendado:** 2-3 páginas (TCC/artigo) · 4-6 páginas (dissertação) · 6-10 páginas (tese).

### 2.3 Fundamentação Teórica / Revisão de Literatura

Esta seção demonstra que você domina o assunto. Mas atenção: **dominar não é listar**.

**O que NÃO fazer (colagem de citações):**
> "Segundo Silva (2020), X é Y. De acordo com Santos (2021), X também é Y. Para Oliveira (2022), X é Y." ← Isso é um catálogo, não uma fundamentação.

**O que FAZER (síntese crítica):**
> "A definição de X evoluiu ao longo da última década. Enquanto Silva (2020) enfatiza o aspecto A, Santos (2021) amplia a perspectiva ao incluir B. Oliveira (2022), por sua vez, propõe uma integração de ambos, argumentando que C." ← Aqui você compara, conecta e avalia criticamente.

**Como organizar:**
- Por **eixos temáticos** (não por autor): agrupe conceitos relacionados.
- Do **geral para o específico**: defina conceitos amplos antes dos detalhados.
- Inclua uma subseção de **trabalhos correlatos**: o que já foi feito de similar? Quais resultados obtiveram? Como seu trabalho se diferencia?

**Tabela comparativa de trabalhos correlatos (excelente recurso!):**

| Autor | Ano | Método | Dados | AUC-ROC | Diferencial |
|-------|-----|--------|-------|---------|-------------|
| Silva | 2020 | RF | Real (5k) | 0,85 | Sem balanceamento |
| Santos | 2021 | LGBM | Real (50k) | 0,91 | Com SMOTE |
| **Este trabalho** | **2024** | **3 modelos** | **Fictício (1k)** | **0,877** | **Pipeline reprodutível** |

### 2.4 Metodologia

A metodologia é o seu **protocolo de laboratório**. Qualquer pesquisador deve conseguir reproduzir seu trabalho lendo apenas esta seção.

**Checklist de informações obrigatórias:**

- [ ] **Dados:** Fonte, volume, período de coleta, formato, dicionário de variáveis.
- [ ] **Pré-processamento:** Tratamento de missing values (qual estratégia e por quê), outliers, codificação, normalização.
- [ ] **Divisão treino/teste:** Proporção e método (holdout, K-fold, stratified).
- [ ] **Algoritmos:** Quais, com quais hiperparâmetros, e por que esses foram escolhidos.
- [ ] **Métricas:** Quais métricas de avaliação e por que são adequadas para o problema.
- [ ] **Reprodutibilidade:** Seed, versões de software, link do repositório.

**Dica:** Use verbos no **pretérito perfeito** ("foram treinados", "utilizou-se") se os experimentos já foram realizados, ou **futuro do presente** ("serão treinados") se é um projeto de pesquisa.

### 2.5 Resultados e Discussão

Esta é a seção mais importante do seu trabalho. Aqui você mostra o que descobriu e **interpreta** os achados.

**Padrão OII para cada resultado:**
1. **O**bservação: O que os dados mostram? (fato)
2. **I**nterpretação: O que isso significa? (análise)
3. **I**mplicação: Como isso se relaciona com a literatura? (conexão)

**Exemplo:**
> **Observação:** "O modelo LightGBM obteve AUC-ROC de 0,877, superando a Regressão Logística (0,823) e o Random Forest (0,856)."
>
> **Interpretação:** "O desempenho superior do LightGBM pode ser atribuído à sua capacidade de capturar interações não-lineares entre as variáveis, especialmente entre satisfação e número de reclamações."
>
> **Implicação:** "Este resultado corrobora os achados de Fernandes (2023), que obteve AUC de 0,89 com dados reais de telecomunicações."

**Erros comuns:**
- ❌ Apenas descrever tabelas sem interpretar: "A Tabela 3 mostra os resultados."
- ❌ Não comparar com a literatura: seus números existem num vácuo.
- ❌ Ignorar resultados negativos: se algo não funcionou, explique por quê.

### 2.6 Conclusão / Considerações Finais

A conclusão **não** é um resumo do trabalho. É uma avaliação de fechamento.

**Estrutura recomendada:**
1. **Retomada dos objetivos:** Cada objetivo específico foi alcançado? (1-2 parágrafos)
2. **Principais contribuições:** O que o trabalho acrescenta ao campo? (1 parágrafo)
3. **Limitações:** O que não foi possível fazer e por quê? (1 parágrafo)
4. **Trabalhos futuros:** Sugestões concretas para pesquisas subsequentes. (1 parágrafo)

**Regras de ouro:**
- ✅ Retome os objetivos e avalie honestamente.
- ✅ Reconheça limitações — isso demonstra maturidade.
- ❌ Não introduza referências novas.
- ❌ Não apresente dados novos.
- ❌ Não use "Em suma" ou "Portanto" para iniciar — comece com conteúdo substantivo.

---

## 3. Linguagem Acadêmica

### Palavras e expressões a EVITAR

| ❌ Evite | ✅ Use em vez disso | Por quê |
|----------|-------------------|---------|
| "Muito", "bastante" | Quantifique: "82,5%", "3 vezes maior" | Vagos e subjetivos |
| "Eu acho que" | "Os resultados sugerem que" | Impessoal |
| "A gente" | "Os pesquisadores" / voz passiva | Coloquial |
| "Etc." | Liste todos ou use "entre outros" | Impreciso |
| "Através de" (no sentido de "por meio de") | "Por meio de" | "Através" = físico |
| "Onde" (no sentido de "em que") | "Em que", "no qual" | "Onde" = lugar físico |
| "Nível" (no sentido de "âmbito") | "No âmbito de", "na esfera de" | Galicismo |
| "O mesmo" (como pronome) | Repetir o substantivo ou usar pronome | Arcaico/jurídico |
| "Em nível de" | "Em termos de", "quanto a" | Impreciso |
| "Fazer com que" | Verbo direto: "provocar", "causar" | Prolixo |

### Palavras e expressões RECOMENDADAS

| Função | Expressões |
|--------|-----------|
| **Indicar causa** | "Em razão de", "devido a", "em virtude de" |
| **Indicar consequência** | "Por conseguinte", "em decorrência", "como resultado" |
| **Indicar contraste** | "Todavia", "no entanto", "em contrapartida", "por outro lado" |
| **Indicar adição** | "Ademais", "além disso", "complementarmente" |
| **Indicar conclusão** | "Portanto", "desse modo", "diante do exposto" |
| **Introduzir evidência** | "Conforme", "segundo", "de acordo com" |
| **Expressar cautela** | "Sugere-se que", "os dados indicam", "aparentemente" |

---

## 4. Verbos e Tempos Verbais

### Quais tempos usar em cada seção?

| Seção | Tempo verbal | Exemplo |
|-------|-------------|---------|
| **Resumo** | Pretérito perfeito | "Este trabalho investigou..." |
| **Introdução** | Presente do indicativo | "A retenção de clientes é..." |
| **Fundamentação** | Presente do indicativo | "A Regressão Logística modela..." |
| **Metodologia** | Pretérito perfeito | "Foram treinados três modelos..." |
| **Resultados** | Presente do indicativo | "A Tabela 3 apresenta..." |
| **Discussão** | Presente do indicativo | "Os resultados corroboram..." |
| **Conclusão** | Pretérito perfeito + Presente | "O objetivo foi alcançado. O modelo demonstra..." |
| **Projeto de pesquisa** | Futuro | "Serão treinados...", "Será utilizado..." |

### Verbos úteis para resultados

| Quando o resultado... | Use |
|----------------------|-----|
| Confirma a literatura | "corrobora", "confirma", "está alinhado com", "é consistente com" |
| Contradiz a literatura | "contradiz", "diverge de", "contrasta com" |
| É novo | "revela", "evidencia", "demonstra" |
| É parcial | "sugere", "indica", "aponta para" |

### Verbos úteis para citações

| Verbo | Uso | Exemplo |
|-------|-----|---------|
| **Argumentar** | O autor defende uma posição | "Silva (2020) argumenta que..." |
| **Demonstrar** | O autor prova algo com dados | "Santos (2021) demonstra que..." |
| **Propor** | O autor sugere algo novo | "Oliveira (2022) propõe um framework..." |
| **Destacar** | O autor enfatiza | "Hastie (2009) destaca a importância de..." |
| **Investigar** | O autor estuda algo | "Fernandes (2023) investiga o impacto de..." |
| **Relatar** | O autor descreve resultados | "Lima (2024) relata que..." |
| **Criticar** | O autor avalia negativamente | "Peçanha (2024) critica a falta de..." |
| **Concordar** | Alinhamento com outro autor | "Em concordância com Breiman (2001), ..." |

---

## 5. Conectivos e Transições

Conectivos são a "cola" entre frases e parágrafos. Sem eles, o texto fica fragmentado.

### Conectivos por função

#### Para adicionar ideias
- Além disso, ...
- Complementarmente, ...
- Adicionalmente, ...
- Não apenas ..., mas também ...
- Somado a isso, ...

#### Para contrastar
- Entretanto, ...
- No entanto, ...
- Por outro lado, ...
- Em contrapartida, ...
- Apesar de ..., ...
- Diferentemente do que propõe [Autor], ...

#### Para exemplificar
- Por exemplo, ...
- A título de ilustração, ...
- Como demonstrado na Tabela X, ...
- Conforme evidenciado pela Figura Y, ...

#### Para indicar causa/consequência
- Em virtude de ..., ...
- Como consequência, ...
- Dado que ..., ...
- Isso resulta em ...
- Por essa razão, ...

#### Para concluir/sintetizar
- Em síntese, ...
- Diante do exposto, ...
- À luz dos resultados, ...
- Pode-se concluir que ...
- Os achados permitem afirmar que ...

#### Para indicar sequência temporal/lógica
- Primeiramente, ... Em seguida, ... Por fim, ...
- Antes de ..., é necessário ...
- Após a etapa de ..., procedeu-se a ...
- Na sequência, ...

---

## 6. Citações no Padrão ABNT

### Tipos de citação

#### Citação indireta (paráfrase)
Você reformula a ideia do autor com suas próprias palavras.

```latex
% Autor como complemento (final da frase):
Modelos de ensemble superam classificadores individuais \cite{hastie2009}.

% Autor como sujeito da frase:
Conforme \citeonline{hastie2009}, modelos de ensemble superam classificadores individuais.
```

#### Citação direta curta (até 3 linhas)
No corpo do texto, entre aspas, com indicação de página.

```latex
Segundo \citeonline{hastie2009}, ``a escolha do modelo deve considerar 
o trade-off entre viés e variância'' \cite[p.~37]{hastie2009}.
```

#### Citação direta longa (mais de 3 linhas)
Recuada 4cm, fonte menor, sem aspas, com indicação de página.

```latex
\begin{citacao}
A reprodutibilidade é um pilar fundamental da ciência moderna. 
Um resultado que não pode ser verificado independentemente 
não pode ser considerado conhecimento científico estabelecido 
\cite[p.~15]{lima2024}.
\end{citacao}
```

### Regra de ouro das citações

- Use `\citeonline{chave}` quando o autor é **sujeito** da frase: "**Hastie (2009)** afirma que..."
- Use `\cite{chave}` quando a citação é **complemento**: "...conforme proposto na literatura **(HASTIE, 2009)**."
- **Nunca** inicie um parágrafo com citação direta.
- **Prefira** citações indiretas (90%) a diretas (10%).

---

## 7. Erros Comuns e Como Evitá-los

### Erro 1: Parágrafos de uma frase
❌ "A Tabela 3 apresenta os resultados."
✅ "A Tabela 3 apresenta os resultados de desempenho dos três modelos no conjunto de teste. Observa-se que o LightGBM obteve o maior AUC-ROC (0,877), seguido pelo Random Forest (0,856). Esse padrão é consistente com a literatura, onde métodos de boosting tendem a superar bagging em dados tabulares."

### Erro 2: Gerundismo
❌ "O modelo está sendo treinado utilizando dados que estão sendo processados."
✅ "O modelo é treinado com dados previamente processados."

### Erro 3: Subjetividade disfarçada
❌ "Os resultados foram excelentes."
✅ "Os resultados superaram o baseline em 12 pontos percentuais de AUC-ROC."

### Erro 4: Redundância
❌ "A metodologia metodológica utilizada na pesquisa..."
✅ "A metodologia empregada..."

### Erro 5: Frases quilométricas
Se uma frase tem mais de **3 linhas**, quebre em duas. O leitor agradece.

### Erro 6: Iniciar frase com numeral
❌ "42 foi a seed utilizada."
✅ "A seed utilizada foi 42." ou "Quarenta e dois foi o valor da seed."

### Erro 7: Siglas não definidas
❌ "O AUC-ROC do LGBM foi 0,877 usando CV."
✅ "A Área sob a Curva ROC (AUC-ROC) do LightGBM (LGBM) foi de 0,877, obtida via Validação Cruzada (CV)."

Regra: defina a sigla na **primeira** ocorrência. Nas demais, use apenas a sigla.

### Erro 8: Confundir "a" e "há"
- **Há** = tempo passado: "Há dez anos, o LightGBM não existia."
- **A** = tempo futuro ou distância: "A conferência será daqui a dois meses."

### Erro 9: "Aonde" vs "Onde"
- **Onde** = lugar em que (estático): "O diretório onde os dados são armazenados."
- **Aonde** = lugar a que (movimento): "Aonde o pipeline leva os dados processados."
- Em textos acadêmicos, prefira **"em que"** ou **"no qual"**.

---

## 8. Dicas Finais de Revisão

### Técnica dos três passes

1. **Passe 1 — Estrutura:** Leia só os títulos de seções e primeiras frases de cada parágrafo. O texto faz sentido nessa leitura "rápida"? A lógica flui?

2. **Passe 2 — Conteúdo:** Leia completo. Cada afirmação é sustentada por dados ou referências? Há contradições entre seções?

3. **Passe 3 — Linguagem:** Leia em voz alta. Frases estranhas são imediatamente perceptíveis quando vocalizadas.

### Checklist de revisão rápida

- [ ] Cada parágrafo tem pelo menos 3 frases?
- [ ] Cada seção começa com uma frase que apresenta o tema?
- [ ] Todas as figuras e tabelas são referenciadas no texto?
- [ ] Todas as siglas estão definidas na primeira ocorrência?
- [ ] Os tempos verbais estão consistentes dentro de cada seção?
- [ ] Há conectivos ligando parágrafos e seções?
- [ ] O resumo pode ser entendido sem ler o restante do texto?

### O teste do "E daí?"

Após cada parágrafo, pergunte: "E daí? Por que isso importa?" Se você não consegue responder, o parágrafo provavelmente precisa de uma frase de conexão ou interpretação.

---

## Referências Recomendadas sobre Escrita Científica

- **ECO, U.** *Como se faz uma tese*. 26. ed. São Paulo: Perspectiva, 2016. — Clássico atemporal.
- **WAZLAWICK, R. S.** *Metodologia de Pesquisa para Ciência da Computação*. 3. ed. Rio de Janeiro: Elsevier, 2024. — Excelente para a área de Computação/Dados.
- **MORESI, E. A. D.** *Metodologia da Pesquisa*. Brasília: UCB, 2023. — Referência didática.

---

> **💡 Dica final:** A escrita é uma habilidade que melhora com prática. Não espere escrever o texto perfeito na primeira tentativa. Escreva uma versão ruim, depois melhore. Depois melhore de novo. As melhores teses do mundo tiveram rascunhos terríveis.
