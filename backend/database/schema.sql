-- ===========================================================
-- Banco de Dados Pet Certo (PostgreSQL)
-- Schema oficial definido por Henrique (Banco de Dados e Documentação).
-- Esta versão é usada exatamente como entregue pelo autor do modelo;
-- o backend inteiro foi adaptado para funcionar em cima dela.
-- ===========================================================

-- ---------------------------------------------------
-- Tabela: Usuario (Tabela Pai / Base)
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS Usuario (
    idUsuario SERIAL PRIMARY KEY,
    login VARCHAR(255) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    nomeCompleto VARCHAR(255) NOT NULL
);

-- ---------------------------------------------------
-- Tabelas Filhas (Herança de Usuario)
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS Adotante (
    idUsuario INT PRIMARY KEY,
    cpf VARCHAR(14) NOT NULL UNIQUE,
    endereco TEXT NOT NULL,
    scorePerfil DECIMAL(5,2),
    CONSTRAINT fk_adotante_usuario FOREIGN KEY (idUsuario)
        REFERENCES Usuario (idUsuario) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Instituicao (
    idUsuario INT PRIMARY KEY,
    cnpj VARCHAR(18) NOT NULL UNIQUE,
    localizacao TEXT NOT NULL,
    infoAbrigo TEXT,
    CONSTRAINT fk_instituicao_usuario FOREIGN KEY (idUsuario)
        REFERENCES Usuario (idUsuario) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Administrador (
    idUsuario INT PRIMARY KEY,
    permissoes TEXT,
    infoAdmin TEXT,
    CONSTRAINT fk_administrador_usuario FOREIGN KEY (idUsuario)
        REFERENCES Usuario (idUsuario) ON DELETE CASCADE ON UPDATE CASCADE
);

-- ---------------------------------------------------
-- Tabela: RegistroAdministrativo
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS RegistroAdministrativo (
    idRegistroAdmin SERIAL PRIMARY KEY,
    idAdministrador INT NOT NULL,
    tipoAtividade VARCHAR(100) NOT NULL,
    dataHora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    descricao TEXT,
    CONSTRAINT fk_registro_admin FOREIGN KEY (idAdministrador)
        REFERENCES Administrador (idUsuario) ON DELETE CASCADE ON UPDATE CASCADE
);

-- ---------------------------------------------------
-- Gestão de Animais e Características
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS Animal (
    idAnimal SERIAL PRIMARY KEY,
    idInstituicao INT NOT NULL,
    nome VARCHAR(255) NOT NULL,
    dataNascimento DATE,
    status VARCHAR(50) NOT NULL DEFAULT 'Disponível',
    CONSTRAINT fk_animal_instituicao FOREIGN KEY (idInstituicao)
        REFERENCES Instituicao (idUsuario) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS CaracteristicaAnimal (
    idCaracteristica SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL UNIQUE
);

-- Tabela Associativa (Muitos para Muitos entre Animal e Característica)
CREATE TABLE IF NOT EXISTS AnimalCaracteristica (
    idAnimal INT NOT NULL,
    idCaracteristica INT NOT NULL,
    PRIMARY KEY (idAnimal, idCaracteristica),
    CONSTRAINT fk_ac_animal FOREIGN KEY (idAnimal)
        REFERENCES Animal (idAnimal) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_ac_caracteristica FOREIGN KEY (idCaracteristica)
        REFERENCES CaracteristicaAnimal (idCaracteristica) ON DELETE CASCADE ON UPDATE CASCADE
);

-- ---------------------------------------------------
-- Interações e Análises
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS Favorito (
    idFavorito SERIAL PRIMARY KEY,
    idAdotante INT NOT NULL,
    idAnimal INT NOT NULL,
    dataFavorito TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_favorito_adotante_animal UNIQUE (idAdotante, idAnimal),
    CONSTRAINT fk_favorito_adotante FOREIGN KEY (idAdotante)
        REFERENCES Adotante (idUsuario) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_favorito_animal FOREIGN KEY (idAnimal)
        REFERENCES Animal (idAnimal) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Recomendacao (
    idRecomendacao SERIAL PRIMARY KEY,
    idAdotante INT NOT NULL,
    idAnimal INT NOT NULL,
    dataGerada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_recomendacao_adotante FOREIGN KEY (idAdotante)
        REFERENCES Adotante (idUsuario) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_recomendacao_animal FOREIGN KEY (idAnimal)
        REFERENCES Animal (idAnimal) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Compatibilidade (
    idCompatibilidade SERIAL PRIMARY KEY,
    idAdotante INT NOT NULL,
    idAnimal INT NOT NULL,
    score INT CHECK (score BETWEEN 0 AND 100),
    fatores JSONB, -- Suporte a dados estruturados no Postgres
    CONSTRAINT fk_compatibilidade_adotante FOREIGN KEY (idAdotante)
        REFERENCES Adotante (idUsuario) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_compatibilidade_animal FOREIGN KEY (idAnimal)
        REFERENCES Animal (idAnimal) ON DELETE CASCADE ON UPDATE CASCADE
);

-- ---------------------------------------------------
-- Fluxo do Processo de Adoção
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS ManifestacaoInteresse (
    idManifestacao SERIAL PRIMARY KEY,
    idAdotante INT NOT NULL,
    idAnimal INT NOT NULL,
    dataManifestacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'Pendente',
    CONSTRAINT fk_manifestacao_adotante FOREIGN KEY (idAdotante)
        REFERENCES Adotante (idUsuario) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_manifestacao_animal FOREIGN KEY (idAnimal)
        REFERENCES Animal (idAnimal) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS ProcessoAdocao (
    idProcesso SERIAL PRIMARY KEY,
    idManifestacao INT NOT NULL UNIQUE,
    status VARCHAR(50) NOT NULL DEFAULT 'Em Andamento',
    CONSTRAINT fk_processo_manifestacao FOREIGN KEY (idManifestacao)
        REFERENCES ManifestacaoInteresse (idManifestacao) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS EtapaAdocao (
    idEtapa SERIAL PRIMARY KEY,
    idProcesso INT NOT NULL,
    nome VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    dataInicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dataFim TIMESTAMP,
    CONSTRAINT fk_etapa_processo FOREIGN KEY (idProcesso)
        REFERENCES ProcessoAdocao (idProcesso) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS HorarioVisita (
    idHorario SERIAL PRIMARY KEY,
    idInstituicao INT NOT NULL,
    dataHora TIMESTAMP NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Disponível',
    CONSTRAINT fk_horario_instituicao FOREIGN KEY (idInstituicao)
        REFERENCES Instituicao (idUsuario) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Visita (
    idVisita SERIAL PRIMARY KEY,
    idProcesso INT NOT NULL,
    idHorario INT UNIQUE,
    dataVisita TIMESTAMP NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Agendada',
    resultado TEXT,
    CONSTRAINT fk_visita_processo FOREIGN KEY (idProcesso)
        REFERENCES ProcessoAdocao (idProcesso) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_visita_horario FOREIGN KEY (idHorario)
        REFERENCES HorarioVisita (idHorario) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Documento (
    idDocumento SERIAL PRIMARY KEY,
    idProcesso INT NOT NULL,
    nome VARCHAR(255) NOT NULL,
    caminhoArquivo VARCHAR(255) NOT NULL,
    dataEnvio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_documento_processo FOREIGN KEY (idProcesso)
        REFERENCES ProcessoAdocao (idProcesso) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS HistoricoProcesso (
    idHistorico SERIAL PRIMARY KEY,
    idProcesso INT NOT NULL,
    dataHora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acao VARCHAR(255) NOT NULL,
    mudanca TEXT,
    CONSTRAINT fk_historico_processo FOREIGN KEY (idProcesso)
        REFERENCES ProcessoAdocao (idProcesso) ON DELETE CASCADE ON UPDATE CASCADE
);
