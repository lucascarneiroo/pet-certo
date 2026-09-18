"""
Módulo reservado para o algoritmo de compatibilidade adotante/animal
(score ponderado e/ou Gale-Shapley — casamento estável), o componente
computacional avançado do projeto.

Ainda não implementado nesta sprint: o foco atual é banco conectado,
login, cadastro de usuários, controle de perfis e o CRUD principal
(animais). Quando implementado, este módulo será chamado a partir de
uma nova rota na API (ex: GET /api/animais/recomendados), sem precisar
alterar nada na camada de banco ou autenticação.
"""


def calcular_score_compatibilidade(adotante: dict, animal: dict) -> float:
    """Placeholder — será implementado na próxima sprint.

    Ideia: soma ponderada de critérios (porte, energia, crianças,
    outros pets, experiência do adotante, tipo de moradia), normalizada
    entre 0 e 1.
    """
    raise NotImplementedError("Algoritmo de compatibilidade será implementado na próxima sprint.")
