"""
Algoritmo de compatibilidade adotante-animal — componente computacional
avançado do projeto (integração com Tópicos Avançados).

Resolve dois problemas:

1. Calcular um SCORE DE COMPATIBILIDADE (0 a 1) entre cada par
   adotante-animal, considerando critérios reais de adoção responsável
   (porte, energia, convivência com crianças/outros pets, tipo de
   moradia, experiência do adotante).

2. A partir da matriz de scores, encontrar um PAREAMENTO ESTÁVEL entre
   todos os adotantes e animais disponíveis, usando o algoritmo de
   Gale-Shapley ("casamento estável"). Isso é um problema de
   otimização combinatória de verdade: o sistema não está só
   ordenando por nota, está resolvendo uma alocação em que ninguém
   ganharia trocando de par depois de pronto.

Sobre desempenho — três versões da mesma conta, para comparação:

- calcular_matriz_scores_ingenua(): loop Python puro, par a par.
  Existe só de referência para o benchmark.
- calcular_matriz_scores(): vetorizada com NumPy — monta arrays e
  deixa o NumPy calcular a matriz inteira de uma vez (broadcasting),
  usando rotinas em C por baixo. Ordens de magnitude mais rápida que
  o loop equivalente, mesmo em um único núcleo.
- calcular_matriz_scores_paralelo(): divide os animais em blocos e
  distribui entre processos (multiprocessing), usando vários núcleos
  de CPU de verdade. Compensa a partir de bases maiores — para poucos
  animais, o custo de criar processos é maior que o ganho.

Números reais dessa comparação: rode `python -m matching.benchmark`.
"""

from __future__ import annotations

import multiprocessing as mp
from typing import Optional

import numpy as np

PESOS = {
    "porte": 0.20,
    "energia": 0.20,
    "criancas": 0.15,
    "outros_pets": 0.15,
    "espaco": 0.15,
    "experiencia": 0.15,
}

_ORDEM_PORTE = {"pequeno": 0, "medio": 1, "grande": 2}
_ORDEM_ENERGIA = {"baixo": 0, "medio": 1, "alto": 2}


# ---------------------------------------------------------------------
# Versão vetorizada (NumPy) — a que o sistema usa de verdade
# ---------------------------------------------------------------------

def _campos_adotantes(adotantes: list[dict]) -> dict[str, np.ndarray]:
    n = len(adotantes)
    return {
        "porte": np.array([_ORDEM_PORTE.get(a.get("preferencia_porte", "medio"), 1) for a in adotantes]).reshape(n, 1),
        "energia": np.array([_ORDEM_ENERGIA.get(a.get("energia_desejada", "medio"), 1) for a in adotantes]).reshape(n, 1),
        "tem_criancas": np.array([bool(a.get("tem_criancas", False)) for a in adotantes]).reshape(n, 1),
        "tem_outros_pets": np.array([bool(a.get("tem_outros_pets", False)) for a in adotantes]).reshape(n, 1),
        "apartamento": np.array([a.get("tipo_moradia", "apartamento") == "apartamento" for a in adotantes]).reshape(n, 1),
        "experiencia_anos": np.array([float(a.get("experiencia_anos", 0)) for a in adotantes]).reshape(n, 1),
    }


def _campos_animais(animais: list[dict]) -> dict[str, np.ndarray]:
    m = len(animais)
    return {
        "porte": np.array([_ORDEM_PORTE.get(a.get("porte", "medio"), 1) for a in animais]).reshape(1, m),
        "energia": np.array([_ORDEM_ENERGIA.get(a.get("nivel_energia", "medio"), 1) for a in animais]).reshape(1, m),
        "convive_criancas": np.array([bool(a.get("convive_criancas", False)) for a in animais]).reshape(1, m),
        "convive_outros_pets": np.array([bool(a.get("convive_outros_pets", False)) for a in animais]).reshape(1, m),
        "precisa_quintal": np.array([a.get("espaco_recomendado") == "casa_com_quintal" for a in animais]).reshape(1, m),
        "necessita_experiencia": np.array([bool(a.get("necessidades_especiais")) for a in animais]).reshape(1, m),
    }


def calcular_matriz_scores(adotantes: list[dict], animais: list[dict]) -> np.ndarray:
    """Calcula a matriz inteira de scores (n_adotantes x n_animais) de
    uma vez, sem laço Python — cada célula é o score daquele adotante
    com aquele animal."""
    if not adotantes or not animais:
        return np.zeros((len(adotantes), len(animais)))

    ad = _campos_adotantes(adotantes)
    an = _campos_animais(animais)

    score_porte = 1 - np.abs(ad["porte"] - an["porte"]) / 2
    score_energia = 1 - np.abs(ad["energia"] - an["energia"]) / 2
    score_criancas = np.where(ad["tem_criancas"] & ~an["convive_criancas"], 0.0, 1.0)
    score_outros_pets = np.where(ad["tem_outros_pets"] & ~an["convive_outros_pets"], 0.0, 1.0)
    score_espaco = np.where(ad["apartamento"] & an["precisa_quintal"], 0.3, 1.0)
    score_experiencia = np.where(
        an["necessita_experiencia"] & (ad["experiencia_anos"] < 1), 0.4, 1.0
    )

    return (
        PESOS["porte"] * score_porte
        + PESOS["energia"] * score_energia
        + PESOS["criancas"] * score_criancas
        + PESOS["outros_pets"] * score_outros_pets
        + PESOS["espaco"] * score_espaco
        + PESOS["experiencia"] * score_experiencia
    )


# ---------------------------------------------------------------------
# Versão ingênua (Python puro) — só para benchmark comparativo
# ---------------------------------------------------------------------

def _score_par(adotante: dict, animal: dict) -> float:
    porte_ad = _ORDEM_PORTE.get(adotante.get("preferencia_porte", "medio"), 1)
    porte_an = _ORDEM_PORTE.get(animal.get("porte", "medio"), 1)
    score_porte = 1 - abs(porte_ad - porte_an) / 2

    energia_ad = _ORDEM_ENERGIA.get(adotante.get("energia_desejada", "medio"), 1)
    energia_an = _ORDEM_ENERGIA.get(animal.get("nivel_energia", "medio"), 1)
    score_energia = 1 - abs(energia_ad - energia_an) / 2

    score_criancas = 0.0 if (adotante.get("tem_criancas") and not animal.get("convive_criancas")) else 1.0
    score_outros_pets = 0.0 if (adotante.get("tem_outros_pets") and not animal.get("convive_outros_pets")) else 1.0
    score_espaco = 0.3 if (adotante.get("tipo_moradia") == "apartamento" and animal.get("espaco_recomendado") == "casa_com_quintal") else 1.0
    score_experiencia = 0.4 if (animal.get("necessidades_especiais") and adotante.get("experiencia_anos", 0) < 1) else 1.0

    return (
        PESOS["porte"] * score_porte
        + PESOS["energia"] * score_energia
        + PESOS["criancas"] * score_criancas
        + PESOS["outros_pets"] * score_outros_pets
        + PESOS["espaco"] * score_espaco
        + PESOS["experiencia"] * score_experiencia
    )


def calcular_matriz_scores_ingenua(adotantes: list[dict], animais: list[dict]) -> np.ndarray:
    """Mesma conta que calcular_matriz_scores(), mas com loop Python
    par a par — sem otimização nenhuma. Serve só de referência para o
    benchmark, não deve ser usada pelo sistema."""
    n, m = len(adotantes), len(animais)
    matriz = np.zeros((n, m))
    for i, ad in enumerate(adotantes):
        for j, an in enumerate(animais):
            matriz[i, j] = _score_par(ad, an)
    return matriz


# ---------------------------------------------------------------------
# Versão paralela (multiprocessing) — para bases maiores
# ---------------------------------------------------------------------

def _calcular_bloco(args):
    adotantes, bloco_animais = args
    return calcular_matriz_scores(adotantes, bloco_animais)


def calcular_matriz_scores_paralelo(
    adotantes: list[dict], animais: list[dict], n_processos: Optional[int] = None
) -> np.ndarray:
    """Divide os animais em blocos e distribui entre processos
    (multiprocessing), usando vários núcleos de CPU de verdade — não é
    só truque de sintaxe do NumPy, são processos do sistema operacional
    rodando ao mesmo tempo. Vale a pena a partir de bases grandes (ex:
    uma rede de abrigos, não só uma ONG); para poucos animais o custo
    de criar os processos é maior que o ganho."""
    if not adotantes or not animais:
        return np.zeros((len(adotantes), len(animais)))

    n_processos = min(n_processos or mp.cpu_count(), len(animais)) or 1
    blocos = [list(bloco) for bloco in np.array_split(animais, n_processos) if len(bloco) > 0]
    tarefas = [(adotantes, bloco) for bloco in blocos]

    with mp.Pool(processes=len(tarefas)) as pool:
        resultados = pool.map(_calcular_bloco, tarefas)

    return np.hstack(resultados)


# ---------------------------------------------------------------------
# Pareamento estável (Gale-Shapley) — a parte de otimização combinatória
# ---------------------------------------------------------------------

def gerar_pareamento_estavel(
    ids_adotantes: list, ids_animais: list, matriz_scores: np.ndarray
) -> dict:
    """
    Algoritmo de Gale-Shapley (casamento estável). Os adotantes
    'propõem' aos animais em ordem decrescente do próprio score; cada
    animal fica provisoriamente com quem tem o maior score entre os
    que já propuseram, e solta quem tiver score pior se alguém melhor
    aparecer depois. O resultado final é estável: não existe nenhuma
    dupla adotante-animal fora do pareamento que prefeririam trocar
    pra ficar junta.

    Retorna {id_adotante: id_animal}. Se houver mais adotantes que
    animais, quem sobrar simplesmente não aparece no resultado (fica
    na fila para quando outro animal ficar disponível).
    """
    n_adotantes = len(ids_adotantes)
    n_animais = len(ids_animais)
    if n_adotantes == 0 or n_animais == 0:
        return {}

    preferencias = [list(np.argsort(-matriz_scores[i])) for i in range(n_adotantes)]
    proximo = [0] * n_adotantes

    livres = list(range(n_adotantes))
    animal_atual: dict[int, int] = {}   # index do animal -> index do adotante pareado com ele
    par_do_adotante: dict[int, int] = {}

    while livres:
        i = livres.pop(0)
        if proximo[i] >= n_animais:
            continue  # já propôs pra todos os animais, fica sem par por ora

        j = preferencias[i][proximo[i]]
        proximo[i] += 1

        if j not in animal_atual:
            animal_atual[j] = i
            par_do_adotante[i] = j
        elif matriz_scores[i, j] > matriz_scores[animal_atual[j], j]:
            k = animal_atual[j]
            animal_atual[j] = i
            par_do_adotante[i] = j
            del par_do_adotante[k]
            livres.append(k)
        else:
            livres.append(i)

    return {ids_adotantes[i]: ids_animais[j] for i, j in par_do_adotante.items()}
