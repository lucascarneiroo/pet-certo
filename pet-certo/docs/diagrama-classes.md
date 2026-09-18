# Diagrama de Classes — PetCerto

> Renderiza automaticamente no GitHub (é um diagrama Mermaid dentro do Markdown).

```mermaid
classDiagram
    class Usuario {
        +int id
        +string nome
        +string email
        +string perfil
        +string data_cadastro
        +eh_admin() bool
        +eh_voluntario() bool
        +eh_adotante() bool
    }

    class Animal {
        +int id
        +string nome
        +string especie
        +string raca
        +string porte
        +float idade_anos
        +string nivel_energia
        +string temperamento
        +bool convive_criancas
        +bool convive_outros_pets
        +string necessidades_especiais
        +string espaco_recomendado
        +string status
        +string data_cadastro
        +int cadastrado_por
    }

    class AuthService {
        <<módulo de serviço>>
        +criar_usuario(nome, email, senha, perfil) Usuario
        +autenticar(email, senha) Usuario
        +listar_usuarios() Usuario[]
    }

    class SessionService {
        <<módulo de serviço>>
        +criar_sessao(usuario_id) string
        +usuario_da_sessao(token) Usuario
        +encerrar_sessao(token) void
    }

    class AnimalRepository {
        <<módulo de serviço>>
        +criar_animal(...) Animal
        +listar_animais() Animal[]
        +buscar_animal_por_id(id) Animal
        +atualizar_animal(id, campos) Animal
        +excluir_animal(id) void
    }

    class PetCertoHandler {
        <<API REST>>
        +do_GET()
        +do_POST()
        +do_PUT()
        +do_DELETE()
    }

    class CompatibilidadeMatching {
        <<próxima sprint>>
        +calcular_score_compatibilidade(adotante, animal) float
    }

    AuthService --> Usuario : cria e consulta
    SessionService --> Usuario : identifica por token
    AnimalRepository --> Animal : gerencia
    AnimalRepository --> Usuario : cadastrado_por
    PetCertoHandler --> AuthService : usa
    PetCertoHandler --> SessionService : usa
    PetCertoHandler --> AnimalRepository : usa
    CompatibilidadeMatching ..> Usuario : (futuro) usa perfil do adotante
    CompatibilidadeMatching ..> Animal : (futuro) usa perfil do animal
```

## Observação sobre as classes de serviço

`AuthService`, `SessionService`, `AnimalRepository` e `PetCertoHandler` estão
representados como classes para fins do diagrama, mas no código são módulos
Python com funções (não classes tradicionais com `self`) — uma escolha
comum em backends simples, que não perde nada em termos de organização ou
regras de negócio. As entidades de dados de verdade (o que vai para o banco)
são `Usuario` e `Animal`.
