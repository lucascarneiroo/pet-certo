"""
Compara o tempo de execução das três abordagens do cálculo da matriz
de compatibilidade: ingênua (loop Python puro), vetorizada (NumPy) e
paralela (multiprocessing).

Serve como prova concreta de otimização para a apresentação/vídeo —
não é só "IA magicamente mais rápida", são números reais.

Como usar:
    cd backend
    python -m matching.benchmark
"""

import random
import time

from matching.compatibilidade import (
    calcular_matriz_scores,
    calcular_matriz_scores_ingenua,
    calcular_matriz_scores_paralelo,
    gerar_pareamento_estavel,
)


def _gerar_adotante():
    return {
        "preferencia_porte": random.choice(["pequeno", "medio", "grande"]),
        "energia_desejada": random.choice(["baixo", "medio", "alto"]),
        "tem_criancas": random.random() < 0.4,
        "tem_outros_pets": random.random() < 0.3,
        "tipo_moradia": random.choice(["apartamento", "casa_com_quintal"]),
        "experiencia_anos": random.randint(0, 15),
    }


def _gerar_animal():
    return {
        "porte": random.choice(["pequeno", "medio", "grande"]),
        "nivel_energia": random.choice(["baixo", "medio", "alto"]),
        "convive_criancas": random.random() < 0.7,
        "convive_outros_pets": random.random() < 0.7,
        "espaco_recomendado": random.choice(["apartamento", "casa_com_quintal", "indiferente"]),
        "necessidades_especiais": random.random() < 0.2,
    }


def _medir(func, *args):
    inicio = time.perf_counter()
    resultado = func(*args)
    duracao = time.perf_counter() - inicio
    return resultado, duracao


def main():
    random.seed(42)  # resultados reproduzíveis

    for n in (50, 200, 1000):
        adotantes = [_gerar_adotante() for _ in range(n)]
        animais = [_gerar_animal() for _ in range(n)]

        print(f"\n=== {n} adotantes x {n} animais ({n*n} pares calculados) ===")

        matriz_ingenua, t_ingenua = _medir(calcular_matriz_scores_ingenua, adotantes, animais)
        print(f"Ingênua (loop Python puro):  {t_ingenua:.4f}s")

        matriz_vetorizada, t_vetorizada = _medir(calcular_matriz_scores, adotantes, animais)
        ganho_v = t_ingenua / t_vetorizada if t_vetorizada > 0 else float("inf")
        print(f"Vetorizada (NumPy):          {t_vetorizada:.4f}s   ({ganho_v:.1f}x mais rápido)")

        # confere que as duas versões dão o mesmo resultado (correção, não só velocidade)
        diferenca_max = abs(matriz_ingenua - matriz_vetorizada).max()
        assert diferenca_max < 1e-9, "as versões deram resultados diferentes!"

        matriz_paralela, t_paralela = _medir(calcular_matriz_scores_paralelo, adotantes, animais)
        ganho_p = t_ingenua / t_paralela if t_paralela > 0 else float("inf")
        print(f"Paralela (multiprocessing):  {t_paralela:.4f}s   ({ganho_p:.1f}x mais rápido)")

    print("\n=== Exemplo de pareamento estável (Gale-Shapley), com 6 adotantes e 4 animais ===")
    adotantes_exemplo = [_gerar_adotante() for _ in range(6)]
    animais_exemplo = [_gerar_animal() for _ in range(4)]
    ids_adotantes = [f"adotante_{i}" for i in range(6)]
    ids_animais = [f"animal_{j}" for j in range(4)]

    matriz = calcular_matriz_scores(adotantes_exemplo, animais_exemplo)
    pareamento = gerar_pareamento_estavel(ids_adotantes, ids_animais, matriz)
    for adotante_id, animal_id in pareamento.items():
        i = ids_adotantes.index(adotante_id)
        j = ids_animais.index(animal_id)
        print(f"{adotante_id} <-> {animal_id}  (score {matriz[i, j]:.2f})")
    sem_par = set(ids_adotantes) - set(pareamento.keys())
    if sem_par:
        print(f"Sem par nesta rodada: {sorted(sem_par)} (mais adotantes que animais disponíveis)")


if __name__ == "__main__":
    main()
