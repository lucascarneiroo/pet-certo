"""Testes do núcleo de compatibilidade (matching/compatibilidade.py):
cálculo de pontuação com diferentes combinações de perfis de adotante e
características de animal, casos-limite (cold start, animal sem
características) e verificação de que o pareamento gerado pelo
Gale-Shapley é estável.

Não depende do servidor rodando (ao contrário de teste_fluxo_adocao.py) —
testa o módulo Python de compatibilidade diretamente, com valores
conhecidos, para cobrir o RNF25 (testes do mecanismo de compatibilidade
com diferentes combinações de perfis de adotante e características de
animal).
"""
import random

import numpy as np

from matching.compatibilidade import (
    calcular_matriz_scores,
    calcular_matriz_scores_ingenua,
    gerar_pareamento_estavel,
    vetor_de_preferencia,
    vetor_do_animal,
)


def esperar(condicao, mensagem):
    if not condicao:
        raise AssertionError(f"FALHOU: {mensagem}")
    print(f"OK: {mensagem}")


def score(historico_tags, tags_animal):
    P = vetor_de_preferencia(historico_tags).reshape(1, -1)
    A = vetor_do_animal(tags_animal).reshape(1, -1)
    return float(calcular_matriz_scores(P, A)[0, 0])


# ---------------------------------------------------------------------------
# 1) Perfis extremos: adotante totalmente compatível x totalmente incompatível
# ---------------------------------------------------------------------------

CACHORRO_PEQUENO_CALMO = [
    "Espécie: Cão", "Porte: Pequeno", "Energia: Baixa",
    "Espaço: Apartamento", "Experiência: Não Exige Experiência Prévia",
    "Convive com Crianças",
]
CACHORRO_GRANDE_AGITADO = [
    "Espécie: Cão", "Porte: Grande", "Energia: Alta",
    "Espaço: Casa com Quintal Grande", "Experiência: Exige Experiência Prévia",
]

# adotante cujo histórico (favoritos/manifestações) é só de animais pequenos e calmos
historico_apartamento = [CACHORRO_PEQUENO_CALMO, CACHORRO_PEQUENO_CALMO, CACHORRO_PEQUENO_CALMO]

score_compativel = score(historico_apartamento, CACHORRO_PEQUENO_CALMO)
score_incompativel = score(historico_apartamento, CACHORRO_GRANDE_AGITADO)

esperar(score_compativel > 90, f"perfil totalmente compatível gera score alto ({score_compativel:.1f})")
esperar(score_incompativel < 40, f"perfil totalmente incompatível gera score baixo ({score_incompativel:.1f})")
esperar(score_compativel > score_incompativel,
        "score do animal compatível é maior que o do incompatível, para o mesmo histórico de adotante")

# ---------------------------------------------------------------------------
# 2) Cold start: adotante sem histórico recebe um score neutro, nem o melhor nem o pior
# ---------------------------------------------------------------------------

score_frio = score([], CACHORRO_PEQUENO_CALMO)
esperar(score_incompativel < score_frio < score_compativel,
        f"adotante sem histórico (cold start) recebe score neutro ({score_frio:.1f}), "
        f"entre o pior ({score_incompativel:.1f}) e o melhor ({score_compativel:.1f}) caso")

# ---------------------------------------------------------------------------
# 3) Diferentes combinações: cada categoria que deixa de bater reduz o score,
#    isoladamente (mantendo as demais características iguais)
# ---------------------------------------------------------------------------

base_animal = [
    "Espécie: Gato", "Porte: Médio", "Energia: Média",
    "Espaço: Casa com Quintal Pequeno", "Experiência: Não Exige Experiência Prévia",
]
historico_base = [base_animal]

variacoes = [
    ("porte", "Porte: Médio", "Porte: Grande"),
    ("energia", "Energia: Média", "Energia: Alta"),
    ("espaço", "Espaço: Casa com Quintal Pequeno", "Espaço: Casa com Quintal Grande"),
    ("espécie", "Espécie: Gato", "Espécie: Cão"),
    ("experiência", "Experiência: Não Exige Experiência Prévia", "Experiência: Exige Experiência Prévia"),
]
score_base = score(historico_base, base_animal)
for nome_categoria, tag_igual, tag_diferente in variacoes:
    animal_variado = [t if t != tag_igual else tag_diferente for t in base_animal]
    score_variado = score(historico_base, animal_variado)
    esperar(score_base > score_variado,
            f"mudar só a categoria '{nome_categoria}' reduz o score ({score_base:.1f} -> {score_variado:.1f})")

# ---------------------------------------------------------------------------
# 4) Características booleanas: concordância entre adotante e animal pontua mais
# ---------------------------------------------------------------------------

animal_sem_criancas = list(base_animal)
animal_com_criancas = base_animal + ["Convive com Crianças"]
historico_com_criancas = [animal_com_criancas, animal_com_criancas]

score_concorda = score(historico_com_criancas, animal_com_criancas)
score_discorda = score(historico_com_criancas, animal_sem_criancas)
esperar(score_concorda > score_discorda,
        f"animal com a mesma característica booleana do histórico do adotante pontua mais "
        f"({score_concorda:.1f} > {score_discorda:.1f})")

# ---------------------------------------------------------------------------
# 5) Caso-limite: animal sem nenhuma característica cadastrada não quebra o cálculo
# ---------------------------------------------------------------------------

score_vazio = score(historico_base, [])
esperar(0 <= score_vazio <= 100, f"animal sem características cadastradas ainda gera um score válido ({score_vazio:.1f})")

# ---------------------------------------------------------------------------
# 6) Implementação vetorizada bate com a ingênua também neste conjunto de perfis
#    (o benchmark.py já compara as três em combinações aleatórias; aqui é um
#    conjunto fixo e determinístico, independente do benchmark)
# ---------------------------------------------------------------------------

P_multi = vetor_de_preferencia(historico_com_criancas).reshape(1, -1)
A_multi = np.array([
    vetor_do_animal(CACHORRO_PEQUENO_CALMO),
    vetor_do_animal(CACHORRO_GRANDE_AGITADO),
    vetor_do_animal(base_animal),
])
diferenca = float(np.abs(calcular_matriz_scores(P_multi, A_multi) - calcular_matriz_scores_ingenua(P_multi, A_multi)).max())
esperar(diferenca < 1e-9, f"implementação vetorizada bate com a ingênua neste conjunto (diferença {diferenca:.2e})")

# ---------------------------------------------------------------------------
# 7) Gale-Shapley: o pareamento gerado é estável (nenhum par fora dele prefere
#    mutuamente trocar em relação aos pares formados)
# ---------------------------------------------------------------------------


def pareamento_e_estavel(matriz, adotantes_ids, animais_ids, pareamento):
    idx_adotante = {a: i for i, a in enumerate(adotantes_ids)}
    idx_animal = {a: j for j, a in enumerate(animais_ids)}
    animal_do_adotante = dict(pareamento)
    adotante_do_animal = {an: a for a, an in pareamento.items()}
    for a in adotantes_ids:
        score_atual_a = (
            matriz[idx_adotante[a], idx_animal[animal_do_adotante[a]]] if a in animal_do_adotante else -1.0
        )
        for an in animais_ids:
            if animal_do_adotante.get(a) == an:
                continue
            score_alternativo = matriz[idx_adotante[a], idx_animal[an]]
            score_atual_an = (
                matriz[idx_adotante[adotante_do_animal[an]], idx_animal[an]] if an in adotante_do_animal else -1.0
            )
            if score_alternativo > score_atual_a and score_alternativo > score_atual_an:
                return False  # par (a, an) prefere mutuamente romper o pareamento
    return True


random.seed(7)
animais_ids = [101, 102, 103, 104]
adotantes_ids = [1, 2, 3, 4, 5]
tags_dos_animais = [CACHORRO_PEQUENO_CALMO, CACHORRO_GRANDE_AGITADO, base_animal, animal_com_criancas]
pool_historico = [CACHORRO_PEQUENO_CALMO, CACHORRO_GRANDE_AGITADO, base_animal]
historicos = [random.sample(pool_historico, k=random.randint(0, 2)) for _ in adotantes_ids]

A_pareamento = np.array([vetor_do_animal(t) for t in tags_dos_animais])
P_pareamento = np.array([vetor_de_preferencia(h) for h in historicos])
matriz_pareamento = calcular_matriz_scores(P_pareamento, A_pareamento)

pareamento = gerar_pareamento_estavel(adotantes_ids, animais_ids, matriz_pareamento)

esperar(len(pareamento) == min(len(adotantes_ids), len(animais_ids)),
        f"pareamento usa todos os animais disponíveis quando há mais adotantes que animais ({len(pareamento)} pares)")
esperar(pareamento_e_estavel(matriz_pareamento, adotantes_ids, animais_ids, pareamento),
        "pareamento gerado pelo Gale-Shapley é estável (sem par que prefira mutuamente trocar)")

print("\nTodos os testes do núcleo de compatibilidade passaram.")
