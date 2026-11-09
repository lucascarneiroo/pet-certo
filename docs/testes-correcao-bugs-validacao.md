# Testes, correção de bugs, validação e navegação

Repositório: https://github.com/lucascarneiroo/pet-certo

Cobre as 5 entregas desta etapa: testes funcionais, correção de bugs,
testes de validação, testes de navegação e atualização da documentação.

---

## 1. Testes funcionais

Rodados os 3 scripts de teste automatizado do projeto, contra uma
instância isolada (banco descartável, sem afetar dados reais):

- `scripts/teste_compatibilidade.py` — núcleo de compatibilidade, 14 verificações.
- `scripts/teste_fluxo_adocao.py` — fluxo completo ponta a ponta (cadastro,
  login, animal, favoritar, manifestação, aprovação, visita, etapas,
  documentos, conclusão), 25 verificações.
- `scripts/teste_validacao.py` (novo) — dados inválidos e regras de
  negócio, 18 verificações.

**Total: 57 verificações, todas passando.**

## 2. Correção de bugs

### Bug crítico: loop infinito de requisições

`ong/Dashboard.jsx` e `adopter/AnimalDetail.jsx` tinham `useEffect` usando
o objeto `usuario` inteiro como dependência. `getUsuario()` faz
`JSON.parse(localStorage...)` a cada chamada — ou seja, gera um objeto
novo a cada renderização. Como o efeito disparava toda vez que esse
objeto "mudava" (mesmo sem mudança real) e o próprio efeito atualizava
o estado da tela, o ciclo se repetia indefinidamente: centenas de
requisições por segundo, sem parar.

Confirmado na prática: o Dashboard da instituição disparou mais de 700
requisições em poucos segundos antes da correção. Corrigido trocando a
dependência pelo campo `id` (`usuario?.id`), que só muda quando o
usuário realmente troca de sessão.

Commit: [`8a69345`](https://github.com/lucascarneiroo/pet-certo/commit/8a69345).

## 3. Testes de validação

Testada a API diretamente com dados inválidos, campos obrigatórios
ausentes, formatos incorretos e tentativas de violar regras de negócio.
3 problemas encontrados e corrigidos:

| Problema | Antes | Depois |
|---|---|---|
| Data de nascimento inválida no cadastro de animal | HTTP 500 (erro cru do banco) | HTTP 400 com mensagem clara |
| Listar etapas de processo inexistente | HTTP 200 com lista vazia (erro escondido) | HTTP 404 |
| Concluir/cancelar processo inexistente | HTTP 403 ("pertence a outra instituição", mensagem enganosa) | HTTP 404 ("não encontrado") |

As duas últimas tinham a mesma causa: a checagem de posse ("você é dono
deste processo?") rodava antes da checagem de existência. Corrigido
fazendo a existência ser checada primeiro, nas rotas de etapas, visitas,
documentos, histórico, concluir e cancelar processo.

Commit: [`8a69345`](https://github.com/lucascarneiroo/pet-certo/commit/8a69345).

## 4. Testes de navegação

Percorridas todas as telas dos 3 perfis (administrador, instituição,
adotante): menus, redirecionamentos e controle de acesso. Sem erros de
console em nenhuma tela.

- Acesso cruzado de perfil (ex.: admin tentando acessar área do
  adotante) é bloqueado e redireciona para a própria área.
- URL inexistente redireciona para a página inicial.
- "Sair do painel" encerra a sessão de verdade — tentar voltar a uma
  área logada depois de sair redireciona para o login.
- Nenhum link quebrado encontrado nos menus dos 3 perfis.

## 5. Atualização da documentação

- `backend/README.md`: adicionado o comando do novo script de testes de
  validação.
- `backend/scripts/teste_validacao.py`: novo script, commitado, com as
  18 verificações de validação — pode ser rodado novamente a qualquer
  momento por qualquer pessoa do grupo.
- `backend/scripts/teste_fluxo_adocao.py`: atualizado para refletir a
  regra de negócio reforçada na Sprint 08 (não é mais possível concluir
  um processo pulando etapas) — o teste antigo pulava etapas e passou a
  falhar; corrigido para avançar as 4 etapas antes de concluir.

Commit: [`c076ea0`](https://github.com/lucascarneiroo/pet-certo/commit/c076ea0).

---

## Resumo

| Item | Resultado |
|---|---|
| Testes funcionais | 57 verificações automatizadas, todas passando |
| Correção de bugs | 1 bug crítico (loop infinito) + 3 bugs de validação corrigidos |
| Testes de validação | Script novo commitado, 18 verificações |
| Testes de navegação | 3 perfis percorridos, sem erros de console nem links quebrados |
| Documentação | README e scripts de teste atualizados |
