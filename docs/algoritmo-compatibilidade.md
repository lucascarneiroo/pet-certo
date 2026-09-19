# Algoritmo de compatibilidade e componente computacional avançado

## O problema

Dado um adotante e um animal disponível, calcular um score de 0 a 100 que
diga o quanto eles combinam, e conseguir fazer isso em escala (milhares de
adotantes x milhares de animais) sem que o tempo de cálculo exploda.

## Por que não é uma preferência declarada

O schema de banco (definido por Henrique) não tem uma tabela de
"preferências do adotante" — `Adotante` só guarda CPF, endereço e um score
de perfil. Em vez de forçar uma tabela nova fora do modelo combinado pelo
grupo, o algoritmo aprende a preferência do adotante a partir do próprio
comportamento dele: os animais que ele já favoritou ou pelos quais já
manifestou interesse. É, na prática, um recomendador baseado em conteúdo
(content-based filtering), e é exatamente para isso que as tabelas
`Favorito`, `ManifestacaoInteresse`, `Recomendacao` e `Compatibilidade` do
schema servem.

Cada animal tem um conjunto de etiquetas (características), tiradas de um
vocabulário fixo (`GET /api/tags`), agrupado em categorias:

- Espécie, Porte, Energia, Espaço recomendado, Experiência exigida
  (categorias de escolha única — o animal tem exatamente uma etiqueta de
  cada)
- Convive com Crianças, Convive com Outros Pets, Necessidades Especiais
  (marcações booleanas — a etiqueta existe ou não)

O "perfil de preferência" do adotante é montado assim: para cada categoria
de escolha única, calcula-se a fração dos animais curtidos que têm cada
etiqueta daquela categoria (uma distribuição de probabilidade). Para as
booleanas, calcula-se a fração dos animais curtidos que têm aquela
etiqueta. Um adotante sem histórico (cold start) recebe um perfil neutro
(uniforme nas categorias, 0,5 nas booleanas), para não ser penalizado nem
favorecido antes de interagir com o sistema.

## O cálculo do score

Cada categoria tem um peso (soma 1,0): Porte e Energia pesam mais (0,20
cada), Espaço e os dois booleanos principais (crianças, outros pets) 0,10
a 0,15, Espécie e Experiência 0,10, Necessidades Especiais 0,05.

```
score(adotante, animal) =
    Σ categorias de escolha única: peso_categoria * P[adotante, etiqueta_do_animal_na_categoria]
  + Σ etiquetas booleanas: peso_etiqueta * (P*presente + (1-P)*(1-presente))
```

Onde `P` é o valor do perfil de preferência do adotante para aquela
etiqueta. O resultado é multiplicado por 100 e limitado entre 0 e 100.

## Três implementações, para comparar desempenho (componente computacional avançado)

O mesmo cálculo foi escrito de três formas (`backend/matching/compatibilidade.py`):

1. **Ingênua**: dois laços `for` em Python puro, percorrendo cada par
   (adotante, animal) e cada etiqueta — implementação de referência,
   usada só para conferir que as outras duas dão o mesmo resultado.
2. **Vetorizada (NumPy)**: o mesmo cálculo expresso como produtos de
   matrizes (multiplicação matricial), sem laços explícitos em Python.
3. **Paralela (multiprocessing)**: divide os animais em blocos e calcula
   cada bloco em um processo separado, depois junta os resultados.

As três são comparadas em `backend/matching/benchmark.py`, com sementes
fixas (`random.seed(42)`) para reprodutibilidade, e o resultado numérico é
conferido entre elas (`assert diferenca_max < 1e-9`) — ou seja, o ganho de
desempenho não vem às custas de precisão.

### Resultado real medido (rodando `python3 matching/benchmark.py`)

```
=== 50 adotantes x 50 animais (2500 pares) ===
Ingênua: 0.0194s | Vetorizada: 0.0005s (36.4x) | Paralela: 0.0316s (0.6x)

=== 200 adotantes x 200 animais (40000 pares) ===
Ingênua: 0.2679s | Vetorizada: 0.0014s (187.9x) | Paralela: 0.0121s (22.2x)

=== 1000 adotantes x 1000 animais (1000000 pares) ===
Ingênua: 6.8702s | Vetorizada: 0.0591s (116.3x) | Paralela: 0.3174s (21.6x)
```

A vetorização com NumPy venceu em todos os cenários testados — inclusive a
versão paralela, porque o custo de criar processos e copiar dados entre
eles (overhead do `multiprocessing`) supera o ganho, principalmente em
cenários pequenos (a paralela chega a ser mais lenta que a ingênua com 50
adotantes). Isso é um resultado honesto e didaticamente relevante: nem
todo problema se beneficia de paralelismo, e a forma como os dados são
representados (vetores/matrizes numéricas) importa mais do que a
quantidade de processos usados.

## Pareamento estável (Gale-Shapley)

Além do score individual, `gerar_pareamento_estavel()` implementa o
algoritmo de Gale-Shapley para encontrar um pareamento estável entre um
conjunto de adotantes e um conjunto de animais disponíveis simultaneamente
(por exemplo, para sugerir uma "rodada de adoção" otimizada): cada
adotante propõe, em ordem de compatibilidade decrescente, até que ninguém
mais tenha proposta pendente. O resultado é estável — não existe um par
(adotante, animal) fora do pareamento final que prefira mutuamente trocar
de parceiro.
