# Sprint 12 — Finalização, correção de bugs e Code Freeze

Repositório: https://github.com/lucascarneiroo/pet-certo

## 1. Sistema completamente finalizado

Todas as funcionalidades previstas estão implementadas e funcionando
de ponta a ponta contra o banco real: autenticação e perfis, CRUD de
animais com foto, fluxo completo de adoção (manifestação → aprovação
→ 4 etapas → visitas → documentos → conclusão/cancelamento) com
histórico auditável, núcleo de compatibilidade, painéis de
administrador e instituição, exportação CSV, busca e filtros.

O componente computacional avançado (núcleo de compatibilidade) está
integrado de verdade, não é simulação: 3 implementações (ingênua,
vetorizada com NumPy, paralela com `multiprocessing`) com resultado
numérico equivalente (diferença ~1e-14, ruído de ponto flutuante) e
speedup de até 258x da vetorizada sobre a ingênua em escala (1000x1000
pares), confirmado via `python -m matching.benchmark`.

## 2. Correção de todos os bugs

Revisão final rodando de novo as 57 verificações automatizadas do
projeto (núcleo de compatibilidade, fluxo completo de adoção,
validação de dados) contra uma instância limpa do banco — todas
passando, nenhum bug novo encontrado.

**Limitação conhecida e registrada:** aprovação/rejeição de documento
enviado pelo adotante não existe, porque a tabela `Documento` do banco
não tem coluna de status — mudar isso exige alterar o schema (de
responsabilidade do colega de banco de dados do grupo). Não compromete
os fluxos essenciais do produto.

## 3. Code Freeze

Versão final identificada no GitHub pela tag anotada **`v1.0.0`**,
marcando o commit exato congelado para apresentação e entrega. A
partir daqui, só correções críticas indispensáveis — sem novas
funcionalidades.

Tag: https://github.com/lucascarneiroo/pet-certo/releases/tag/v1.0.0
