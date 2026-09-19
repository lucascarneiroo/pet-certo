"""Algoritmo de compatibilidade adotante x animal.

Adaptação necessária ao schema do Henrique: a tabela Adotante não tem
colunas de preferência declarada (não existe "porte desejado", "aceita
crianças" etc. para o adotante — só cpf, endereço e scorePerfil). O que
existe é o próprio histórico de interesse do adotante: Favorito e
ManifestacaoInteresse. Por isso a preferência de cada adotante é aprendida
a partir dos animais que ele já favoritou ou pelos quais já manifestou
interesse (um recomendador baseado em conteúdo, comparando etiquetas),
com um valor neutro quando ele ainda não interagiu com nada (cold start).

Isso é calculado com três implementações equivalentes (usadas no benchmark):
ingênua (loops Python puros), vetorizada (NumPy) e paralela (multiprocessing),
igual ao que já era feito na versão anterior sobre SQLite — só a forma de
montar os vetores de entrada mudou.
"""
import multiprocessing
from typing import List, Optional

import numpy as np

from database.tags_padrao import CATEGORIAS_PADRAO, CATEGORIA_DA_TAG, TAGS_BOOLEANAS, TODAS_AS_TAGS

_INDICE_DA_TAG = {tag: i for i, tag in enumerate(TODAS_AS_TAGS)}
DIMENSAO = len(TODAS_AS_TAGS)

PESOS_CATEGORIA = {"especie": 0.10, "porte": 0.20, "energia": 0.20, "espaco": 0.15, "experiencia": 0.10}
PESOS_BOOLEANO = {
    "Convive com Crianças": 0.10,
    "Convive com Outros Pets": 0.10,
    "Necessidades Especiais": 0.05,
}

# vetor de pesos por tag (0 fora das categorias ordinais/booleanas relevantes)
_PESO_ORDINAL = np.zeros(DIMENSAO)
for tag, categoria in CATEGORIA_DA_TAG.items():
    _PESO_ORDINAL[_INDICE_DA_TAG[tag]] = PESOS_CATEGORIA[categoria]

_INDICES_BOOL = [_INDICE_DA_TAG[t] for t in TAGS_BOOLEANAS]
_PESO_BOOL = np.array([PESOS_BOOLEANO[t] for t in TAGS_BOOLEANAS])


def vetor_do_animal(tags_do_animal: List[str]) -> np.ndarray:
    v = np.zeros(DIMENSAO)
    for tag in tags_do_animal:
        if tag in _INDICE_DA_TAG:
            v[_INDICE_DA_TAG[tag]] = 1.0
    return v


def matriz_dos_animais(lista_de_tags: List[List[str]]) -> np.ndarray:
    return np.array([vetor_do_animal(tags) for tags in lista_de_tags]) if lista_de_tags else np.zeros((0, DIMENSAO))


def vetor_de_preferencia(historico_de_tags: List[List[str]]) -> np.ndarray:
    """Constrói o vetor de preferência de um adotante a partir das etiquetas
    dos animais que ele já favoritou/manifestou interesse. Sem histórico,
    retorna um valor neutro (uniforme nas categorias ordinais, 0.5 nas
    booleanas) para não penalizar nem favorecer ninguém no cold start."""
    p = np.zeros(DIMENSAO)

    if not historico_de_tags:
        for categoria, tags in CATEGORIAS_PADRAO.items():
            for tag in tags:
                p[_INDICE_DA_TAG[tag]] = 1.0 / len(tags)
        for tag in TAGS_BOOLEANAS:
            p[_INDICE_DA_TAG[tag]] = 0.5
        return p

    n = len(historico_de_tags)
    for categoria, tags in CATEGORIAS_PADRAO.items():
        contagem = {tag: 0 for tag in tags}
        algum_registro = 0
        for tags_animal in historico_de_tags:
            presentes = [t for t in tags_animal if t in contagem]
            if presentes:
                contagem[presentes[0]] += 1
                algum_registro += 1
        if algum_registro == 0:
            for tag in tags:
                p[_INDICE_DA_TAG[tag]] = 1.0 / len(tags)
        else:
            for tag in tags:
                p[_INDICE_DA_TAG[tag]] = contagem[tag] / algum_registro

    for tag in TAGS_BOOLEANAS:
        idx = _INDICE_DA_TAG[tag]
        presentes = sum(1 for tags_animal in historico_de_tags if tag in tags_animal)
        p[idx] = presentes / n

    return p


def matriz_de_preferencias(historicos: List[List[List[str]]]) -> np.ndarray:
    return np.array([vetor_de_preferencia(h) for h in historicos]) if historicos else np.zeros((0, DIMENSAO))


# ------------------------------------------------------------- Cálculo do score

def calcular_matriz_scores_ingenua(P: np.ndarray, A: np.ndarray) -> np.ndarray:
    """Versão de referência, sem vetorização: dois loops Python puros."""
    n, m = P.shape[0], A.shape[0]
    resultado = np.zeros((n, m))
    for i in range(n):
        for j in range(m):
            score = 0.0
            for idx in range(DIMENSAO):
                if _PESO_ORDINAL[idx] > 0:
                    score += _PESO_ORDINAL[idx] * P[i, idx] * A[j, idx]
            for k, idx in enumerate(_INDICES_BOOL):
                peso = _PESO_BOOL[k]
                score += peso * (P[i, idx] * A[j, idx] + (1 - P[i, idx]) * (1 - A[j, idx]))
            resultado[i, j] = score
    return np.clip(resultado * 100, 0, 100)


def calcular_matriz_scores(P: np.ndarray, A: np.ndarray) -> np.ndarray:
    """Versão vetorizada com NumPy (produtos de matrizes em vez de loops)."""
    if P.shape[0] == 0 or A.shape[0] == 0:
        return np.zeros((P.shape[0], A.shape[0]))

    P_ordinal = P * _PESO_ORDINAL  # pesos já embutidos por coluna
    termo_ordinal = P_ordinal @ A.T  # (n, m)

    P_bool = P[:, _INDICES_BOOL]
    A_bool = A[:, _INDICES_BOOL]
    const_i = ((1 - P_bool) * _PESO_BOOL).sum(axis=1)  # (n,)
    coef = P_bool * (2 * _PESO_BOOL) - _PESO_BOOL  # equivalente a peso*(2P-1), (n, n_bool)
    termo_booleano = const_i[:, None] + coef @ A_bool.T  # (n, m)

    return np.clip((termo_ordinal + termo_booleano) * 100, 0, 100)


def _bloco_paralelo(args):
    P, A_bloco = args
    return calcular_matriz_scores(P, A_bloco)


def calcular_matriz_scores_paralelo(P: np.ndarray, A: np.ndarray, n_processos: Optional[int] = None) -> np.ndarray:
    """Mesma conta, mas divide os animais em blocos e usa multiprocessing
    para calcular cada bloco em um processo separado."""
    if A.shape[0] == 0:
        return np.zeros((P.shape[0], 0))
    n_processos = n_processos or min(multiprocessing.cpu_count(), max(1, A.shape[0]))
    blocos = np.array_split(A, n_processos) if n_processos > 1 else [A]
    with multiprocessing.Pool(processes=len(blocos)) as pool:
        resultados = pool.map(_bloco_paralelo, [(P, bloco) for bloco in blocos])
    return np.hstack(resultados)


# ---------------------------------------------------------- Pareamento estável

def gerar_pareamento_estavel(ids_adotantes: List[int], ids_animais: List[int], matriz_scores: np.ndarray) -> dict:
    """Algoritmo de Gale-Shapley: adotantes propõem, do animal mais
    compatível para o menos compatível, até que ninguém mais tenha
    proposta pendente. Resultado é estável: não existe par (adotante,
    animal) fora do pareamento que prefira mutuamente trocar de par."""
    n, m = len(ids_adotantes), len(ids_animais)
    ordem_preferencia = np.argsort(-matriz_scores, axis=1)  # (n, m), do melhor pro pior animal
    proximo_a_propor = [0] * n
    livre = list(range(n))
    animal_atual_de = {}  # idx_animal -> idx_adotante

    while livre:
        i = livre.pop(0)
        if proximo_a_propor[i] >= m:
            continue
        j = ordem_preferencia[i, proximo_a_propor[i]]
        proximo_a_propor[i] += 1
        if j not in animal_atual_de:
            animal_atual_de[j] = i
        else:
            atual = animal_atual_de[j]
            if matriz_scores[i, j] > matriz_scores[atual, j]:
                animal_atual_de[j] = i
                livre.append(atual)
            else:
                livre.append(i)

    return {
        ids_adotantes[i]: ids_animais[j]
        for j, i in animal_atual_de.items()
    }
