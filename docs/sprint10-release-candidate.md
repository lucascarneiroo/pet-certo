# Sprint 10 — Release Candidate

Repositório: https://github.com/lucascarneiroo/pet-certo

Objetivo: consolidar uma versão candidata à entrega final — sistema
estável, interface e banco de dados em suas versões finais, APIs
documentadas e README atualizado.

## 1. Sistema estável

Suite de testes automatizados (núcleo de compatibilidade + fluxo
completo de adoção) confirmando os fluxos principais funcionando de
forma consistente.

## 2. Interface final

Criada uma identidade visual própria: logo (marca de pata), paleta de
cores e tipografia, aplicadas em toda a navegação (Landing, Login,
Cadastro, painéis dos 3 perfis). Bug real corrigido no processo: a
sidebar renderizava quase sem cor por faltar o tom escuro do gradiente
CSS.

Commit: [`921ae96`](https://github.com/lucascarneiroo/pet-certo/commit/921ae96).

## 3. Banco de dados final

Estrutura do `schema.sql` revisada: 17 tabelas, chaves e
relacionamentos coerentes com o modelo de herança de usuário e com o
fluxo completo de adoção.

## 4. APIs documentadas

[`docs/api.md`](api.md) — referência completa de todas as rotas
(método, autenticação, parâmetros, respostas, erros), revisada contra
o código do servidor.

## 5. README atualizado

`README.md` da raiz reescrito do zero — a versão anterior ainda
descrevia SQLite e "frontend: tecnologia a definir", de quando o
projeto começou.

Commit: [`2916a01`](https://github.com/lucascarneiroo/pet-certo/commit/2916a01).
