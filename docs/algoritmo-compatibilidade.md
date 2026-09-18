# Algoritmo de Compatibilidade — Otimização e Paralelismo

Componente computacional avançado do projeto (integração com Tópicos
Avançados). Código em [`backend/matching/compatibilidade.py`](../backend/matching/compatibilidade.py),
benchmark em [`backend/matching/benchmark.py`](../backend/matching/benchmark.py).

## O problema

Dado um grupo de adotantes e um grupo de animais disponíveis, achar o
melhor jeito de casar cada adotante com um animal, considerando que:

- Um adotante bom pra um animal pode não ser bom pra outro
- Vários adotantes podem querer o mesmo animal
- Simplesmente ordenar por "nota" não garante um resultado justo pro
  conjunto todo — pode deixar pares melhores possíveis passarem batido

Isso é formalmente um problema de **otimização combinatória em grafo
bipartido** (o mesmo tipo de problema usado para casar médicos
residentes a hospitais, ou alunos a escolas). Resolvido em duas etapas.

## Etapa 1 — Score de compatibilidade

Cada par (adotante, animal) recebe uma nota de 0 a 1, somando critérios
com pesos diferentes:

| Critério | Peso | Como é calculado |
|---|---|---|
| Porte | 20% | Distância entre porte desejado e porte do animal (pequeno/médio/grande) |
| Nível de energia | 20% | Distância entre energia desejada e energia do animal |
| Convivência com crianças | 15% | Zera se o adotante tem crianças e o animal não convive bem com elas |
| Convivência com outros pets | 15% | Mesma lógica, para outros animais em casa |
| Espaço | 15% | Penaliza apartamento pequeno para animal que precisa de quintal |
| Experiência do adotante | 15% | Penaliza pouca experiência para animal com necessidades especiais |

## Etapa 2 — Pareamento estável (Gale-Shapley)

Com a matriz de scores pronta, o sistema não só ordena — ele roda o
**algoritmo de Gale-Shapley** ("casamento estável"), o mesmo usado em
sistemas reais de alocação (ex: residência médica nos EUA).

Como funciona, em termos simples: cada adotante "propõe" ao animal com
quem tem maior compatibilidade. Se dois adotantes propõem ao mesmo
animal, ele fica provisoriamente com o de maior score — o outro tenta
o próximo animal da lista dele. O processo se repete até todo mundo
ficar pareado (ou esgotar as opções). No final, matematicamente, **não
existe nenhuma dupla adotante-animal fora do pareamento que
prefeririam trocar** — essa é a definição de "estável", e é o que
diferencia isso de um simples "ordenar por nota".

## Otimização de desempenho

Calcular o score de cada par com um `for` aninhado em Python puro
(adotante × animal) fica lento rápido — para 1000 adotantes e 1000
animais, são 1 milhão de contas. Por isso o cálculo da matriz de
scores tem três versões no código, para comparação:

1. **Ingênua** — loop Python, só de referência
2. **Vetorizada (NumPy)** — em vez de calcular par a par, monta arrays
   com os atributos de todos os adotantes e todos os animais de uma
   vez, e deixa o NumPy calcular a matriz inteira com operações de
   array (broadcasting), usando rotinas otimizadas em C por baixo
3. **Paralela (multiprocessing)** — divide os animais em blocos e
   distribui entre processos, usando vários núcleos de CPU ao mesmo
   tempo

### Resultado real do benchmark (`python -m matching.benchmark`)

| Tamanho da base | Ingênua | Vetorizada (NumPy) | Paralela (multiprocessing) |
|---|---|---|---|
| 50 × 50 (2.500 pares) | 0,0015s | 0,0003s (**5,2x**) | 0,0200s (0,1x — mais lenta) |
| 200 × 200 (40.000 pares) | 0,0209s | 0,0014s (**14,5x**) | 0,0092s (2,3x) |
| 1.000 × 1.000 (1.000.000 pares) | 0,7325s | 0,0395s (**18,5x**) | 0,0833s (8,8x) |

### Conclusão honesta sobre paralelismo

A vetorização com NumPy venceu em todos os testes — inclusive a
versão com multiprocessing, que nas bases testadas nem sempre compensa:
criar e coordenar processos tem um custo fixo, e para bases desse
tamanho esse custo é maior que o tempo economizado. A versão paralela
só passa a valer a pena com volumes bem maiores (dezenas de milhares
de pares em diante, cenário de uma rede de abrigos, não uma ONG só).

Por isso, a versão que o sistema usa de fato é a **vetorizada**. A
versão paralela continua no código, documentada e testada, como
caminho de escalabilidade caso a base cresça — não foi descartada, só
não é a padrão hoje.

Sobre GPU (CUDA/OpenCL, tecnologias citadas na disciplina): não fazem
sentido no volume de dados de um abrigo real (o overhead de mover
dados pra GPU custa mais que a conta em si). Ficaria justificável só
numa escala de milhões de pares — por isso a decisão técnica foi
priorizar CPU (vetorização + paralelismo sob demanda) em vez de GPU.

## Como rodar

```bash
cd backend
python -m matching.benchmark
```

Mostra os tempos reais das três versões e um exemplo de pareamento
estável rodando com dados de teste.

## Ainda não integrado à API

Este módulo funciona de forma independente (recebe listas de
dicionários com os atributos de adotantes e animais). Para virar uma
rota tipo `GET /api/animais/recomendados`, falta:

1. Guardar as preferências do adotante no banco (hoje a tabela
   `usuarios` não tem campos como porte preferido, energia desejada
   etc. — precisa de uma tabela nova, `perfis_adotante`)
2. Uma rota na API que busque essas preferências, monte a matriz e
   devolva o pareamento ou o ranking de animais recomendados

Isso fica para a próxima etapa.
