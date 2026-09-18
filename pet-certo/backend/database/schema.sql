-- Schema do banco de dados do PetCerto (backend)
-- Sprint atual: usuarios (login/cadastro/perfis) + animais (CRUD principal)
--
-- Implementado em SQLite por simplicidade de desenvolvimento local.
-- Caso a equipe decida por outro SGBD (PostgreSQL, MySQL...), apenas
-- este arquivo e database/db.py precisam ser adaptados — o restante
-- do backend (auth, crud, api) não depende do banco escolhido.

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    perfil TEXT NOT NULL CHECK (perfil IN ('admin', 'voluntario', 'adotante')),
    data_cadastro TEXT NOT NULL DEFAULT (datetime('now'))
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
