# Roteiro de apresentação — Defesa do TCC

**Arquivo dos slides:** `apresentacao_tcc.pptx` (23 slides, editável no PowerPoint)

**Orçamento: 20 min** → **~14 min de slides + ~5 min de app + 1 min de folga**

Slides 1–22 são a apresentação. O **slide 23 é reserva**: não mostre, deixe para
responder pergunta com número na mão.

Se estiver atrasado, **corte os slides 12 e 18** (marcados 🔸). Sem eles a fala cai
para ~12:40.

---

## Cronometragem

| # | Slide | Tempo | Acum. |
|---|-------|-------|-------|
| 1 | Capa | 0:15 | 0:15 |
| 2 | Roteiro | 0:10 | 0:25 |
| 3 | O problema | 0:45 | 1:10 |
| 4 | A pergunta | 0:40 | 1:50 |
| 5 | Os dados | 0:45 | 2:35 |
| 6 | **Tratamento dos dados** | 1:00 | 3:35 |
| 7 | O método | 0:50 | 4:25 |
| 8 | Por que walk-forward | 0:45 | 5:10 |
| 9 | Estabilidade | 0:45 | 5:55 |
| 10 | Teste independente | 0:40 | 6:35 |
| 11 | **A armadilha da acurácia** | 1:00 | 7:35 |
| 12 | 🔸 O que pesa no risco | 0:40 | 8:15 |
| 13 | Qual modelo levar | 0:35 | 8:50 |
| 14 | A previsão para 2025 | 0:30 | 9:20 |
| 15 | **A prova real** | 0:55 | 10:15 |
| 16 | **Previsto × aconteceu** | 0:50 | 11:05 |
| 17 | Mirassol | 0:45 | 11:50 |
| 18 | 🔸 Dez anos de risco | 0:35 | 12:25 |
| 19 | Cons. finais: objetivos | 0:35 | 13:00 |
| 20 | Cons. finais: contribuições | 0:30 | 13:30 |
| 21 | Cons. finais: limites | 0:30 | 14:00 |
| 22 | Conclusão → app | 0:15 | **14:15** |

Checkpoints: **7:35** (fim do slide 11) e **11:05** (fim do 16). Se passar de 8:00
no 11, corte o 12. Se passar de 11:30 no 16, corte o 18.

---

## O que falar em cada slide

### 1. Capa — 0:15
Bom dia. Sou Leonardo Feitosa Barroso, de Ciência de Dados para Negócios, e vou
apresentar meu trabalho sobre previsão de rebaixamento no Brasileirão, orientado
pelo professor Hilton Ramalho.

### 2. Roteiro — 0:10
Problema e pergunta, dados e método, resultados, a validação com o resultado real
de 2025, considerações finais, e fecho com uma demonstração do aplicativo.

### 3. O problema — 0:45
- Quatro clubes caem por temporada — 20% da amostra. Guardem esse número.
- Cair derruba receita de TV, patrocínio e valor de elenco, e o efeito se arrasta.
- Se o clube souber antes, pode agir.

### 4. A pergunta — 0:40
- **Dá para estimar quem cai antes de a bola rolar?**
- A literatura é quase toda sobre resultado de partida, em liga europeia.
- Não achei trabalho de rebaixamento no Brasileirão com **só dado pré-temporada**.
- É o cenário que interessa a quem decide.

### 5. Os dados — 0:45
- Transfermarkt, raspagem automatizada; dados públicos, uso acadêmico.
- **220 observações** rotuladas: 11 temporadas × 20 clubes, 2014 a 2024.
- **2025 ficou fora do treino**, reservada para prever.
- 15 variáveis: 3 de elenco (**o que o clube tem**) e 12 de janela deslizante
  (**o que o clube fez**).

### 6. Tratamento dos dados — 1:00 ⭐ *slide novo, o professor vai gostar*
- O dado bruto **não vinha pronto**. A limpeza foi parte do método, não detalhe.
- **O problema dos nomes**: as duas páginas do Transfermarkt que eu usei — a de
  elencos e a de classificação — grafam o mesmo clube de formas diferentes.
  "Clube Atletico Paranaense" numa, "Athletico-PR" na outra. Se eu cruzasse
  direto, **o clube simplesmente não casava** e eu perdia a linha.
- Resolvi com um **dicionário de normalização de ~60 entradas** mais remoção de
  acentos, aplicado nos dois lados antes do cruzamento por clube + temporada.
- Além disso: limpeza dos valores monetários (o Transfermarkt escreve
  "€ 45,50 mi."), conferência da lista de rebaixados ano a ano, e uma
  **auditoria do cruzamento** — procurei registros com pontos ausentes justamente
  para detectar merge que tivesse falhado silenciosamente.
- E o tratamento dos faltantes: recém-promovido não tem histórico na Série A, então
  15,5% das janelas ficaram vazias e foram imputadas pela mediana **do treino**.
- Resultado: 220 observações limpas e auditadas, sem furo no cruzamento.

### 7. O método — 0:50
- Percorra as caixas: coleta → janelas → pré-processamento → validação → ajuste
  → teste.
- O que amarra tudo: **nada do futuro entra no modelo**. As médias de T usam só
  T−1 para trás; mediana e escala calculadas só no treino.

### 8. Por que walk-forward — 0:45
- Validação cruzada normal embaralha as temporadas: treina com 2023 para prever
  2018. Fica bonito e é irreal.
- No walk-forward eu sempre treino no passado e valido no ano seguinte, 5 vezes.

### 9. Estabilidade — 0:45
- **Logística é a mais estável** (±0,058); **LightGBM o mais volátil** (±0,151).
- O buraco de 2020 é a pandemia — calendário comprimido, sem torcida. Nenhuma
  variável pré-temporada antecipa choque assim.
- Guardem a volatilidade do LightGBM, ela reaparece no fim.

### 10. Teste independente — 0:40
- Teste em 2023–2024, 40 observações nunca vistas.
- LightGBM 0,877, Random Forest 0,844, Logística 0,828.
- E o XGBoost com 0,652 — **mas com a mesma acurácia do LightGBM, 82,5%**.

### 11. A armadilha da acurácia — 1:00 ⭐ *melhor momento, não corra*
- Mesma acurácia: 82,5%. E mais: **a matriz de confusão é idêntica** — os dois
  acertam 3 dos 8 rebaixados e erram os mesmos casos no limiar de 50%.
- Ainda assim um tem AUC 0,652 e o outro 0,877. Por quê?
- Porque **a diferença não está na decisão, está na ordenação**. Cada triângulo é
  um clube que caiu, na posição do ranking de risco.
  - **LightGBM** concentra os rebaixados nas posições 1, 3, 5, 6, 7, 9.
  - **XGBoost** espalha: 18, 21, 24, 26, 28 — clubes que caíram e ele pôs na
    metade segura.
- A acurácia só vê o corte. O AUC vê o ranking inteiro. E é o **ranking** que serve
  ao gestor.

### 12. 🔸 O que pesa no risco — 0:40
- Azul protege, laranja aumenta.
- **Valor de mercado do elenco domina** — maior coeficiente, negativo.
- Vitórias nas 3 temporadas anteriores também protegem.
- Plantel grande aparece aumentando o risco — ver a explicação no Q&A abaixo,
  é a pergunta mais provável deste slide.

### 13. Qual modelo levar — 0:35
- LightGBM ganha no teste, mas oscila e é caixa-preta.
- Logística é terceira, mas **mais estável, interpretável e calibrada**.
- Escolhi a Logística. O slide 15 mostra que a escolha se pagou.

### 14. A previsão para 2025 — 0:30
- Logística treinada em 2014–2024, aplicada aos 20 clubes de 2025.
- Quatro maiores riscos: **Juventude, Sport, Vitória e Mirassol**.

### 15. A prova real — 0:55 ⭐
- O campeonato acabou, então **dá para conferir**.
- **Acertei 2 dos 4** no corte: Juventude e Sport — o 1.º e o 2.º maiores riscos.
- Mais importante: **AUC realizado de 0,922**, o melhor de todos os períodos.
- **Os quatro rebaixados reais estavam entre os sete maiores riscos.**
- O LightGBM caiu para 0,711 — a instabilidade do walk-forward se confirmou.
- Comparei com heurística ingênua: menor valor de elenco dá 0,906. O modelo supera,
  mas por margem estreita — e eu registro isso com honestidade.

### 16. Previsto × aconteceu — 0:50
- À esquerda o que eu previ, à direita o que aconteceu. **Linha horizontal = acerto
  de ordenação.**
- As quatro linhas laranja saem do topo e chegam ao topo: os rebaixados reais
  estavam todos no alto do meu ranking.
- A linha verde tracejada que atravessa o gráfico é o Mirassol — próximo slide.

### 17. Mirassol — 0:45
- Meu maior erro: previ 43,6% e o clube terminou **em 4.º**, na Libertadores.
- Motivo técnico: estreante na Série A, **sem histórico** — as 12 janelas
  receberam a mediana.
- E o contexto: **trato como caso atípico**. Em 2026, com o campeonato em curso,
  o Mirassol aparece **na zona de rebaixamento**. A fragilidade que o modelo
  apontou não desapareceu, só demorou uma temporada. Sem a campanha excepcional
  de 2025, o clube teria caído.
- *Cuidado:* diga "campeonato em curso" e "indício". Se a banca contestar,
  concorde — 2026 não terminou, é evidência circunstancial que reforça, não fecha.

### 18. 🔸 Dez anos de risco — 0:35
- Retreinei o modelo dez vezes, cada temporada só com o passado dela.
- Em cima o **efeito elevador**: Avaí, Goiás, Atlético-GO, Juventude.
- Embaixo os grandes, risco baixo e estável a década toda.
- Os erros também aparecem: Internacional 2016 com 14%, Grêmio 2021 com 0,4% —
  colapsos dentro da temporada, que dado pré-temporada não captura.

### 19. Considerações finais: objetivos — 0:35
Passe pelos cinco com o dedo, sem ler tudo: base construída, features sem
vazamento, quatro algoritmos com validação temporal, comparação em teste
independente, e a previsão de 2025 — que ainda foi validada contra o oficial.
**O objetivo geral foi alcançado.**

### 20. Considerações finais: contribuições — 0:30
1. Pipeline reprodutível e sem vazamento, repositório público.
2. A demonstração empírica da armadilha da acurácia.
3. Histórico recente complementa o indicador financeiro.
4. E uma previsão **verificada contra a realidade**, não só prometida.

### 21. Considerações finais: limites — 0:30
- Só dado pré-temporada: não capta lesão, troca de técnico, calendário.
- 220 observações é pouco.
- Recém-promovido depende de imputação, como o Mirassol mostrou.
- Sensibilidade: média em vez de mediana não muda nada; janelas 2/4 equivalem.
- Futuro: retreino durante a temporada, dados de transferência, Série B.

### 22. Conclusão → app — 0:15
> "O modelo previu antes. O campeonato confirmou a ordenação.
> Agora eu gostaria de mostrar a ferramenta funcionando."

---

## Demonstração do app — ~5 min

Deixe **rodando antes** de começar. Navegador em tela cheia (F11).

1. **Ranking 2025** (~1:00) — é a previsão do TCC, viva. Juventude 79,4% no topo.
2. **Simulador** (~1:30) — monte um clube. Comece no default (plantel 56,
   VM 48 M€ → ~37%), depois baixe o valor de mercado para ~25 M€ e mostre o risco
   subir. **Leia o aviso do próximo bloco antes de usar esta tela.**
3. **Desempenho do modelo** (~1:30) — ver o guia abaixo.
4. **Análise descritiva** (~0:30) — troque a temporada, mostre que o dado é auditável.
5. Volte ao ranking: *"é essa a entrega prática do trabalho."*

### 🔌 Se a internet ou o app falhar

Não improvise nem tente consertar na frente da banca. Diga:

> "Os números da ferramenta são exatamente os que acabei de mostrar nos slides."

Volte aos **slides 11, 15 e 16** — eles têm o mesmo conteúdo (armadilha da acurácia,
a prova real e previsto × aconteceu). **O app é a entrega prática, não o resultado
do trabalho.** O resultado está no artigo e nos slides.

### 🗣️ Diga isto ANTES de abrir o simulador

> "É uma versão reduzida, para exploração: eu informo alguns indicadores e as
> janelas de 3 e 5 temporadas recebem o mesmo valor. O **ranking** é que usa o
> modelo completo, com as 15 variáveis e o histórico real de cada clube."

Falar isso antes evita a pergunta "por que os números são diferentes das telas?".

### ⚠️ Sobre o simulador — leia antes de demonstrar

Havia **dois bugs** que eu corrigi:

**1. Faixa do tamanho do elenco.** O slider ia de 15 a 50 (default 25), mas na base
o plantel vai de **41 a 80, média 56** — é o plantel registrado no Transfermarkt,
que conta todos os atletas inscritos. A faixa inteira estava *abaixo do mínimo
real*, jogando toda simulação ~3,8 desvios abaixo da média.

**2. Unidade do aproveitamento** — este era o principal. O app enviava o
aproveitamento como **decimal (0,175)**, mas a base de treino está em **percentual
(média 47,1 · desvio 7,9)**. Isso colocava a variável a **5,9 desvios abaixo da
média** e, como os dois coeficientes de aproveitamento são positivos, subtraía
~4,3 do log-odds. **Era por isso que, mesmo com tudo no pior valor, o risco saía
baixo.**

Efeito da correção:

| Cenário | Antes | Depois |
|---|---|---|
| Tudo no pior valor | 69,4% | **91,8%** |
| Clube mediano | 0,5% | **19,8%** |
| Clube forte | — | 0,1% |

O "clube mediano = 19,8%" é a melhor prova de que a correção está certa: bate com
a taxa real de rebaixamento da Série A, que é 20%.

Perfis de referência (só com dados de elenco, histórico na mediana da liga):

| Perfil | Plantel | Estr. | VM (M€) | Risco |
|---|---|---|---|---|
| Média da Série A | 55 | 5 | 39 | 41,9% |
| **Rebaixado típico** | 59 | 3 | 29 | **57,2%** |
| Top-4 típico | 51 | 6 | 69 | 18,7% |

⚠️ **Regenere o app antes da defesa** para as correções entrarem no HTML:
`python scripts/gerar_app_real.py`

---

## Desempenho do Modelo — como explicar cada peça

Você me disse que não sabia explicar esta tela. Vá nesta ordem:

**1. Os seis cartões de cima**
- **Acurácia (80%)** — "de cada 10 clubes, acertei 8". Comece por ela e logo diga:
  *"mas essa é a métrica que engana, e o trabalho mostra por quê."*
- **Precisão** — dos clubes que eu apontei como rebaixados, quantos caíram.
- **Recall (rebaixado)** — dos que caíram, quantos eu peguei. **É a que mais
  importa aqui**: errar um rebaixamento custa mais caro que dar um alarme falso.
- **F1** — média harmônica das duas, quando você quer um número só.
- **AUC-ROC (teste) 0,828** — a probabilidade de o modelo dar risco maior a um
  clube que caiu do que a um que ficou. 0,5 é moeda, 1,0 é perfeito.
- **AUC walk-forward 0,794 ± 0,058** — a mesma medida, mas média de 5 temporadas.
  O ± é o que mostra estabilidade.

**2. Matriz de confusão** — quatro caixas. Diagonal = acerto.
- Verdadeiro negativo: falei que ficava e ficou.
- Verdadeiro positivo: falei que caía e caiu.
- **Falso negativo**: caiu e eu não vi — o erro caro.
- Falso positivo: alarme falso.

**3. Curva ROC** — cada ponto é um limiar de decisão diferente. Quanto mais a curva
sobe pela esquerda, melhor. A diagonal é o palpite aleatório. A área embaixo é o AUC.

**4. Calibração** — "quando eu digo 70%, cai 70% mesmo?" Pontos na diagonal =
probabilidade honesta. Os meus ficam próximos, com leve excesso de confiança.

**5. Tabela de comparação** — por que Logística: melhor estabilidade no
walk-forward, mesmo não tendo o melhor AUC no teste. Aponte a linha do XGBoost:
acurácia alta com AUC baixo, que é o caso do slide 11.

**6. Odds ratios** — o coeficiente convertido em "quantas vezes a chance muda".
- **OR < 1 protege, OR > 1 agrava.**
- Valor de mercado tem o OR mais baixo → o fator protetor mais forte.
- Frase pronta: *"cada desvio-padrão a mais de valor de elenco multiplica a chance
  de cair por 0,39"* (e^−0,931 ≈ 0,39).

---

## Perguntas prováveis — respostas curtas

**"Por que quanto maior o elenco, maior o risco de cair?"** ← *a mais provável*
Cuidado com a palavra "maior". **Clube maior tem risco menor**: valor de mercado é
o coeficiente mais forte e é protetor. O que aumenta o risco é o **plantel
numeroso mantendo o mesmo valor** — ou seja, muitos atletas somando pouco valor,
o que indica qualidade média baixa por jogador e rotatividade/instabilidade de
planejamento. Flamengo tem plantel grande **e** valor altíssimo: o efeito protetor
domina com folga. Se insistirem, mostre no simulador: suba o valor de mercado e o
risco desaba.

**"Coloquei tudo no pior valor e o risco continuou baixo — o modelo está errado?"**
Era um bug do simulador, não do modelo: o aproveitamento estava sendo enviado em
escala decimal onde o treino usa percentual. Corrigido, o cenário de tudo no pior
valor dá 91,8% e o clube mediano dá 19,8% — que é exatamente a taxa base de
rebaixamento da Série A. O modelo do artigo nunca foi afetado: ele lê os valores
direto da base, na escala certa. O Ranking 2025 sempre reproduziu o artigo.

**"O clube médio dá ~42% de risco, mas só 20% caem. Está errado?"**
Não. Treinei com `class_weight='balanced'`, que reequilibra as classes para o
modelo não ignorar a minoria. Isso desloca a escala das probabilidades para cima.
O que importa é a **ordenação** — e no teste a calibração ficou razoável (quartil
de maior risco: 63,6% previsto contra 50% observado).

**"Por que não usou rede neural?"**
220 observações. Modelo com muitos parâmetros sobreajusta. Está na seção 3.5.

**"Por que a semente 42?"**
Convenção da área, valor arbitrário, só para reprodutibilidade.

**"O AUC de 0,922 em 2025 não é sorte, com 20 clubes?"**
Pode ter variância, e por isso reporto intervalo de confiança por bootstrap e
recomendo ler o ranking, não o valor pontual. O argumento forte não é o 0,922
isolado: é que os quatro rebaixados reais ficaram entre os sete maiores riscos, e
que isso é coerente com o walk-forward de cinco temporadas.

**"O modelo só descobriu que time pobre cai."**
Em parte sim, e eu digo isso no trabalho: a heurística de menor valor de elenco
sozinha dá 0,906. A contribuição é integrar elenco e desempenho recente num escore
único, calibrado, com incerteza quantificada.

**"Por que escolheu o modelo que não teve o melhor AUC?"**
Porque o melhor AUC no teste era o menos estável no walk-forward. Em 2025 a
Logística fez 0,922 e o LightGBM 0,711.

**"Por que a matriz de confusão é igual nos dois modelos?"**
Porque no limiar de 50% eles tomam as mesmas decisões. A diferença está na
ordenação — que é o ponto do slide da armadilha.

**"Como você garantiu que o cruzamento dos nomes não perdeu dados?"**
Dicionário de normalização nos dois lados + auditoria: procurei registros com
pontos ausentes no período 2014–2024, que é a assinatura de um merge que falhou.

**"Os dados do Transfermarkt são confiáveis?"**
São estimativas por julgamento coletivo, não valores de transação. Müller, Simons e
Weinmann (2017) mostram qualidade comparável a avaliação profissional. A limitação
está registrada na metodologia.

---

## Checklist antes de entrar

- [ ] `apresentacao_tcc.pptx` no pendrive **e** na nuvem (exporte um PDF de backup)
- [ ] Abrir no PowerPoint e conferir 1 vez — as fontes são Calibri, padrão
- [ ] App **já rodando**, navegador em F11
- [ ] Repositório do GitHub público
- [ ] Cronômetro visível para os checkpoints de 7:35 e 11:05
- [ ] Ensaiar 2× em voz alta cronometrando
