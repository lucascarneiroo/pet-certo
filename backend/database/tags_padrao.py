"""
Conjunto padrão de etiquetas (tags) usadas para descrever características de animais.

O schema do Henrique modela características como uma tabela livre
(CaracteristicaAnimal + AnimalCaracteristica), o que permite qualquer texto.
Para o algoritmo de compatibilidade continuar funcionando de forma objetiva
(comparando porte, energia, espaço etc.), fixamos aqui um vocabulário
padronizado: todo animal cadastrado recebe suas etiquetas a partir destas
listas, uma por categoria. Isso mantém a flexibilidade do modelo do banco
(são só linhas em uma tabela) e a previsibilidade que o algoritmo precisa.

Cada tag pertence a exatamente uma categoria. O algoritmo de compatibilidade
usa CATEGORIA_DA_TAG para descobrir, a partir das tags de um animal, qual é
o seu porte, nível de energia etc.
"""

# categoria -> lista de tags válidas (ordem importa: usada para pontuação por distância)
CATEGORIAS_PADRAO = {
    "especie": ["Espécie: Cão", "Espécie: Gato", "Espécie: Outro"],
    "porte": ["Porte: Pequeno", "Porte: Médio", "Porte: Grande"],
    "energia": ["Energia: Baixa", "Energia: Média", "Energia: Alta"],
    "espaco": ["Espaço: Apartamento", "Espaço: Casa com Quintal Pequeno", "Espaço: Casa com Quintal Grande"],
    "experiencia": ["Experiência: Não Exige Experiência Prévia", "Experiência: Exige Experiência Prévia"],
}

# categorias "booleanas" (a tag existe ou não existe nas características do animal)
TAGS_BOOLEANAS = [
    "Convive com Crianças",
    "Convive com Outros Pets",
    "Necessidades Especiais",
]

# todas as tags válidas, achatadas — usadas para popular CaracteristicaAnimal no seed inicial
TODAS_AS_TAGS = [tag for tags in CATEGORIAS_PADRAO.values() for tag in tags] + TAGS_BOOLEANAS

# mapa reverso: tag -> categoria (só para as categorias de escolha única)
CATEGORIA_DA_TAG = {
    tag: categoria
    for categoria, tags in CATEGORIAS_PADRAO.items()
    for tag in tags
}
