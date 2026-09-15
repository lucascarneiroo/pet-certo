# Modelo Entidade-Relacionamento (MER) — PetCerto

> Renderiza automaticamente no GitHub (é um diagrama Mermaid dentro do Markdown).

```mermaid
erDiagram
    USUARIO {
        int id PK
        string nome
        string email UK
        string senha_hash
        string salt
        string perfil
        string data_cadastro
    }

    ANIMAL {
        int id PK
        string nome
        string especie
        string raca
        string porte
        float idade_anos
        string nivel_energia
        string temperamento
        boolean convive_criancas
        boolean convive_outros_pets
        string necessidades_especiais
        string espaco_recomendado
        string status
        string data_cadastro
        int cadastrado_por FK
    }

    USUARIO ||--o{ ANIMAL : "cadastra"
```

## Entidades

### Usuário
Representa qualquer pessoa com acesso ao sistema — administrador do abrigo,
voluntário ou adotante. O **perfil** é o que define o que cada um pode
fazer (ver `docs/arquitetura.md`).

### Animal
Entidade principal do sistema nesta fase do projeto. Guarda as
características usadas tanto para exibição quanto, futuramente, para o
algoritmo de compatibilidade (porte, energia, convivência com crianças e
outros pets, espaço recomendado).

## Relacionamento

Um **Usuário** pode cadastrar vários **Animais** (relação 1 : N), registrado
pelo campo `cadastrado_por` em `Animal`, que aponta para o `id` do usuário
responsável pelo cadastro. Um animal só pode ter sido cadastrado por um
usuário (ou nenhum, se `cadastrado_por` for nulo).

Relacionamentos futuros previstos (próximas sprints, quando o fluxo de
adoção for implementado): `Usuario` (adotante) ↔ `Animal`, via uma nova
entidade `Solicitacao_Adocao`, representando o processo de interesse →
avaliação → aprovação → adoção.
