-- Schema do banco de dados do PetCerto (backend)
--
-- Implementado em SQLite por simplicidade de desenvolvimento local.
-- Caso a equipe decida por outro SGBD (PostgreSQL, MySQL...), apenas
-- este arquivo e database/db.py precisam ser adaptados — o restante
-- do backend (auth, crud, api) não depende do banco escolhido.

CREATE TABLE IF NOT EXISTS instituicoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cidade TEXT,
    status TEXT NOT NULL DEFAULT 'pendente' CHECK (status IN ('verificada', 'pendente', 'revisao')),
    data_cadastro TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    perfil TEXT NOT NULL CHECK (perfil IN ('admin', 'voluntario', 'adotante')),
    instituicao_id INTEGER,               -- só preenchido para perfil = voluntario
    data_cadastro TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (instituicao_id) REFERENCES instituicoes (id)
);

CREATE TABLE IF NOT EXISTS animais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    especie TEXT NOT NULL CHECK (especie IN ('cachorro', 'gato', 'outro')),
    raca TEXT,
    porte TEXT NOT NULL CHECK (porte IN ('pequeno', 'medio', 'grande')),
    idade_anos REAL NOT NULL DEFAULT 0,
    nivel_energia TEXT NOT NULL CHECK (nivel_energia IN ('baixo', 'medio', 'alto')),
    temperamento TEXT,
    convive_criancas INTEGER NOT NULL DEFAULT 0,      -- 0 = nao, 1 = sim
    convive_outros_pets INTEGER NOT NULL DEFAULT 0,   -- 0 = nao, 1 = sim
    necessidades_especiais TEXT,
    espaco_recomendado TEXT NOT NULL CHECK (espaco_recomendado IN ('apartamento', 'casa_com_quintal', 'indiferente')),
    status TEXT NOT NULL DEFAULT 'disponivel' CHECK (status IN ('disponivel', 'em_processo', 'adotado')),
    data_cadastro TEXT NOT NULL DEFAULT (datetime('now')),
    cadastrado_por INTEGER,
    FOREIGN KEY (cadastrado_por) REFERENCES usuarios (id)
);

-- Fluxo de adoção: cada linha é o pedido de UM adotante por UM animal.
-- "etapa" acompanha o processo (Interesse -> ... -> Conclusão, conforme
-- as telas do frontend); "status" indica se está andando, foi aprovado,
-- recusado ou cancelado.
CREATE TABLE IF NOT EXISTS solicitacoes_adocao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    animal_id INTEGER NOT NULL,
    adotante_id INTEGER NOT NULL,
    etapa TEXT NOT NULL DEFAULT 'interesse'
        CHECK (etapa IN ('interesse', 'analise', 'visita', 'documentos', 'aprovacao', 'concluida')),
    status TEXT NOT NULL DEFAULT 'em_andamento'
        CHECK (status IN ('em_andamento', 'aprovada', 'recusada', 'cancelada')),
    observacoes TEXT,
    data_solicitacao TEXT NOT NULL DEFAULT (datetime('now')),
    data_atualizacao TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (animal_id) REFERENCES animais (id),
    FOREIGN KEY (adotante_id) REFERENCES usuarios (id)
);

-- Visita agendada como parte de uma solicitação de adoção específica.
CREATE TABLE IF NOT EXISTS visitas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    solicitacao_id INTEGER NOT NULL,
    data_agendada TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'agendada'
        CHECK (status IN ('agendada', 'realizada', 'cancelada', 'reagendada')),
    observacoes TEXT,
    data_cadastro TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (solicitacao_id) REFERENCES solicitacoes_adocao (id)
);
