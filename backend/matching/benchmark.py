"""Mede o tempo das três implementações do cálculo de compatibilidade
(ingênua, vetorizada com NumPy, paralela com multiprocessing) em cenários
de tamanhos crescentes, e confirma que todas produzem o mesmo resultado
numérico (a paralela e a vetorizada usam a mesma fórmula; a ingênua é a
referência independente escrita com loops puros)."""
import random
import time

import numpy as np

from database.tags_padrao import CATEGORIAS_PADRAO, TAGS_BOOLEANAS
from matching.compatibilidade import (
    calcular_matriz_scores,
    calcular_matriz_scores_ingenua,
    calcular_matriz_scores_paralelo,
    gerar_pareamento_estavel,
    matriz_de_preferencias,
    matriz_dos_animais,
)

random.seed(42)


def _tags_aleatorias_de_animal():
    tags = []
    for categoria_tags in CATEGORIAS_PADRAO.values():
        tags.append(random.choice(categoria_tags))
    for tag in TAGS_BOOLEANAS:
        if random.random() < 0.5:
            tags.append(tag)
    return tags


def _historico_aleatorio_de_adotante(pool_de_tags_de_animais, tamanho_max=5):
    if random.random() < 0.15 or not pool_de_tags_de_animais:
        return []  # simula adotante novo, sem histórico (cold start)
    quantidade = random.randint(1, min(tamanho_max, len(pool_de_tags_de_animais)))
    return random.sample(pool_de_tags_de_animais, quantidade)


def _rodar_cenario(n_adotantes: int, n_animais: int) -> None:
    tags_dos_animais = [_tags_aleatorias_de_animal() for _ in range(n_animais)]
    historicos = [_historico_aleatorio_de_adotante(tags_dos_animais) for _ in range(n_adotantes)]

    A = matriz_dos_animais(tags_dos_animais)
    P = matriz_de_preferencias(historicos)

    inicio = time.perf_counter()
    scores_ingenua = calcular_matriz_scores_ingenua(P, A)
    tempo_ingenua = time.perf_counter() - inicio

    inicio = time.perf_counter()
    scores_vetorizada = calcular_matriz_scores(P, A)
    tempo_vetorizada = time.perf_counter() - inicio

    inicio = time.perf_counter()
    scores_paralela = calcular_matriz_scores_paralelo(P, A)
    tempo_paralela = time.perf_counter() - inicio

    diferenca_max = np.max(np.abs(scores_ingenua - scores_vetorizada))
    assert diferenca_max < 1e-9, f"Divergência entre ingênua e vetorizada: {diferenca_max}"
    diferenca_paralela = np.max(np.abs(scores_vetorizada - scores_paralela))
    assert diferenca_paralela < 1e-9, f"Divergência entre vetorizada e paralela: {diferenca_paralela}"

    pares = n_adotantes * n_animais
    print(f"=== {n_adotantes} adotantes x {n_animais} animais ({pares} pares) ===")
    print(
        f"Ingênua: {tempo_ingenua:.4f}s | "
        f"Vetorizada: {tempo_vetorizada:.4f}s ({tempo_ingenua / max(tempo_vetorizada, 1e-9):.1f}x) | "
        f"Paralela: {tempo_paralela:.4f}s ({tempo_ingenua / max(tempo_paralela, 1e-9):.1f}x)"
    )
    print(f"Maior diferença numérica entre versões: {diferenca_max:.2e} (esperado: praticamente zero)\n")


def rodar_benchmarks() -> None:
    print("Benchmark do algoritmo de compatibilidade (Pet Certo)\n")
    for n in (50, 200, 1000):
        _rodar_cenario(n, n)

    print("=== Demonstração de pareamento estável (Gale-Shapley) ===")
    tags_animais_demo = [_tags_aleatorias_de_animal() for _ in range(4)]
    historicos_demo = [_historico_aleatorio_de_adotante(tags_animais_demo) for _ in range(6)]
    A_demo = matriz_dos_animais(tags_animais_demo)
    P_demo = matriz_de_preferencias(historicos_demo)
    scores_demo = calcular_matriz_scores(P_demo, A_demo)
    ids_adotantes = list(range(1, 7))
    ids_animais = list(range(101, 105))
    pareamento = gerar_pareamento_estavel(ids_adotantes, ids_animais, scores_demo)
    for id_adotante, id_animal in pareamento.items():
        print(f"  Adotante {id_adotante} -> Animal {id_animal}")
    print(f"({len(pareamento)} de {len(ids_animais)} animais pareados)")


if __name__ == "__main__":
    rodar_benchmarks()
