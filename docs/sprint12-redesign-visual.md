# Sprint 12 — Redesign visual da interface

Repositório: https://github.com/lucascarneiroo/pet-certo

Pedido: deixar a interface parecida com o site de referência
[amigonaosecompra.com.br](https://www.amigonaosecompra.com.br/) — roxo
forte, tipografia grande e em negrito, cards de animal bem fotográficos.

## O que mudou

- **Paleta:** roxo de marca intensificado (`#6A4C8C` → `#6A2C91`), alinhado
  à intensidade do roxo do site de referência.
- **Landing:** título principal muito maior e mais pesado (`font-black`,
  até `text-6xl`), na cor da marca em vez de cinza-escuro; botões viraram
  pílulas (`rounded-full`).
- **Cards de animal** (`adopter/Animals.jsx`): redesenhados no padrão do
  grid do site de referência — foto grande no topo, nome em roxo negrito,
  instituição como "local" em cinza embaixo. Removida a lista duplicada
  "Todos os animais disponíveis", que mostrava os mesmos dados da busca em
  outro formato.

## Correção: fotos cortando demais

Depois do redesign, as fotos ficaram cortando demais a cabeça/corpo dos
animais — os cards usavam uma faixa baixa e larga (160–176px de altura
numa largura bem maior), que corta muito uma foto de retrato (a maioria
das fotos reais de cão/gato).

Corrigido trocando a faixa por uma proporção mais equilibrada (`aspect-[4/3]`)
e priorizando o topo da foto (`object-position: top`) em vez do centro, em
todas as telas com foto de animal do sistema (cards do adotante, detalhe
do animal, preview de cadastro, miniaturas em lista).

Commits: [`0f5f87f`](https://github.com/lucascarneiroo/pet-certo/commit/0f5f87f) (redesign), [`fd38484`](https://github.com/lucascarneiroo/pet-certo/commit/fd38484) (correção de enquadramento).
