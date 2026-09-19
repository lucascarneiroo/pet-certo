# Modelo Entidade-Relacionamento (MER) — Pet Certo

Banco de dados: PostgreSQL. Modelagem definida por Henrique (Banco de Dados
e Documentação) e adotada como oficial pelo backend.

O usuário é modelado por herança: `Usuario` é a tabela-base (login, senha,
nome) e `Adotante`, `Instituicao` e `Administrador` são tabelas filhas —
cada uma reaproveita o `idUsuario` como chave primária e estrangeira. O
perfil de alguém não é uma coluna, é "em qual tabela filha essa pessoa tem
uma linha".

```mermaid
erDiagram
    USUARIO ||--o| ADOTANTE : "é"
    USUARIO ||--o| INSTITUICAO : "é"
    USUARIO ||--o| ADMINISTRADOR : "é"
    ADMINISTRADOR ||--o{ REGISTRO_ADMINISTRATIVO : registra

    INSTITUICAO ||--o{ ANIMAL : cadastra
    ANIMAL ||--o{ ANIMAL_CARACTERISTICA : possui
    CARACTERISTICA_ANIMAL ||--o{ ANIMAL_CARACTERISTICA : classifica

    ADOTANTE ||--o{ FAVORITO : favorita
    ANIMAL ||--o{ FAVORITO : "é favoritado"
    ADOTANTE ||--o{ RECOMENDACAO : recebe
    ANIMAL ||--o{ RECOMENDACAO : "é recomendado"
    ADOTANTE ||--o{ COMPATIBILIDADE : possui
    ANIMAL ||--o{ COMPATIBILIDADE : possui

    ADOTANTE ||--o{ MANIFESTACAO_INTERESSE : manifesta
    ANIMAL ||--o{ MANIFESTACAO_INTERESSE : recebe
    MANIFESTACAO_INTERESSE ||--o| PROCESSO_ADOCAO : origina
    PROCESSO_ADOCAO ||--o{ ETAPA_ADOCAO : possui
    PROCESSO_ADOCAO ||--o{ VISITA : agenda
    PROCESSO_ADOCAO ||--o{ DOCUMENTO : recebe
    PROCESSO_ADOCAO ||--o{ HISTORICO_PROCESSO : registra
    INSTITUICAO ||--o{ HORARIO_VISITA : oferece
    HORARIO_VISITA ||--o| VISITA : reserva

    USUARIO {
        int idUsuario PK
        string login
        string senha
        string nomeCompleto
    }
    ADOTANTE {
        int idUsuario PK_FK
        string cpf
        string endereco
        decimal scorePerfil
    }
    INSTITUICAO {
        int idUsuario PK_FK
        string cnpj
        string localizacao
        string infoAbrigo
    }
    ADMINISTRADOR {
        int idUsuario PK_FK
        string permissoes
        string infoAdmin
    }
    REGISTRO_ADMINISTRATIVO {
        int idRegistroAdmin PK
        int idAdministrador FK
        string tipoAtividade
        timestamp dataHora
        string descricao
    }
    ANIMAL {
        int idAnimal PK
        int idInstituicao FK
        string nome
        date dataNascimento
        string status
    }
    CARACTERISTICA_ANIMAL {
        int idCaracteristica PK
        string nome
    }
    ANIMAL_CARACTERISTICA {
        int idAnimal PK_FK
        int idCaracteristica PK_FK
    }
    FAVORITO {
        int idFavorito PK
        int idAdotante FK
        int idAnimal FK
        timestamp dataFavorito
    }
    RECOMENDACAO {
        int idRecomendacao PK
        int idAdotante FK
        int idAnimal FK
        timestamp dataGerada
    }
    COMPATIBILIDADE {
        int idCompatibilidade PK
        int idAdotante FK
        int idAnimal FK
        int score
        jsonb fatores
    }
    MANIFESTACAO_INTERESSE {
        int idManifestacao PK
        int idAdotante FK
        int idAnimal FK
        timestamp dataManifestacao
        string status
    }
    PROCESSO_ADOCAO {
        int idProcesso PK
        int idManifestacao FK
        string status
    }
    ETAPA_ADOCAO {
        int idEtapa PK
        int idProcesso FK
        string nome
        string status
        timestamp dataInicio
        timestamp dataFim
    }
    HORARIO_VISITA {
        int idHorario PK
        int idInstituicao FK
        timestamp dataHora
        string status
    }
    VISITA {
        int idVisita PK
        int idProcesso FK
        int idHorario FK
        timestamp dataVisita
        string status
        string resultado
    }
    DOCUMENTO {
        int idDocumento PK
        int idProcesso FK
        string nome
        string caminhoArquivo
        timestamp dataEnvio
    }
    HISTORICO_PROCESSO {
        int idHistorico PK
        int idProcesso FK
        timestamp dataHora
        string acao
        string mudanca
    }
```

## Por que características são etiquetas, e não colunas

`CaracteristicaAnimal` + `AnimalCaracteristica` formam um relacionamento
muitos-para-muitos livre: qualquer característica pode ser cadastrada como
uma linha, sem alterar a estrutura da tabela `Animal`. Para o algoritmo de
compatibilidade continuar funcionando de forma objetiva, o backend usa um
conjunto padrão e fixo de etiquetas (ver `backend/database/tags_padrao.py`
e `GET /api/tags`), agrupadas em categorias (espécie, porte, energia,
espaço, experiência, e três marcações booleanas). O modelo do banco
continua genérico; quem restringe o vocabulário é a camada de aplicação.
