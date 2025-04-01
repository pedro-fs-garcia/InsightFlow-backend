create_tables_script = '''
CREATE TABLE IF NOT EXISTS estado (
    id_estado INT PRIMARY KEY,
    sigla VARCHAR(2),
    nome VARCHAR(100),
    regiao VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS municipio (
    id_municipio INT PRIMARY KEY,
    nome VARCHAR(100),
    id_estado INT,
    FOREIGN KEY (id_estado) REFERENCES estado(id_estado)
);

CREATE TABLE IF NOT EXISTS bloco (
    id_bloco INT PRIMARY KEY,
    nome_bloco VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS pais (
    id_pais INT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    id_bloco INT,
    FOREIGN KEY (id_bloco) REFERENCES bloco(id_bloco)
);

CREATE TABLE IF NOT EXISTS unidade_receita_federal (
    id_unidade INT PRIMARY KEY,
    nome VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS modal_transporte (
    id_modal_transporte INT PRIMARY KEY,
    descricao VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS cgce_n3 (
    id_n3 VARCHAR(3) PRIMARY KEY,
    descricao TEXT
);

CREATE TABLE IF NOT EXISTS sh2 (
    id_sh2 VARCHAR(2) PRIMARY KEY,
    descricao TEXT
);

CREATE TABLE IF NOT EXISTS sh4 (
    id_sh4 VARCHAR(4) PRIMARY KEY,
    descricao TEXT
);

CREATE TABLE IF NOT EXISTS produto (
    id_ncm INT PRIMARY KEY,
    descricao TEXT,
    unidade_medida VARCHAR(50),
    id_sh4 VARCHAR(4),
    id_cgce_n3 VARCHAR(3),
    id_sh2 VARCHAR(2),
    FOREIGN KEY (id_sh4) REFERENCES sh4 (id_sh4),
    FOREIGN KEY (id_cgce_n3) REFERENCES cgce_n3 (id_n3),
    FOREIGN KEY (id_sh2) REFERENCES sh2 (id_sh2)
);

CREATE TABLE IF NOT EXISTS exportacao_estado (
    id_transacao INT PRIMARY KEY AUTO_INCREMENT,
    ano INT,
    mes INT,
    tipo_transacao ENUM('exp', 'imp'),
    id_produto INT,
    id_pais INT,
    id_estado INT,
    id_unidade_receita_federal INT,
    quantidade BIGINT,
    valor_fob DECIMAL(15,2),
    kg_liquido DECIMAL(15,2),
    valor_agregado DECIMAL(15,2),
    id_modal_transporte INT,
    FOREIGN KEY (id_modal_transporte) REFERENCES modal_transporte(id_modal_transporte),
    FOREIGN KEY (id_unidade_receita_federal) REFERENCES unidade_receita_federal (id_unidade),
    FOREIGN KEY (id_produto) REFERENCES produto (id_ncm),
    FOREIGN KEY (id_pais) REFERENCES pais (id_pais),
    FOREIGN KEY (id_estado) REFERENCES estado (id_estado)
);

CREATE TABLE IF NOT EXISTS importacao_estado (
    id_transacao INT PRIMARY KEY AUTO_INCREMENT,
    ano INT,
    mes INT,
    tipo_transacao ENUM('exp', 'imp'),
    id_produto INT,
    id_pais INT,
    id_estado INT,
    id_unidade_receita_federal INT,
    quantidade BIGINT,
    valor_fob DECIMAL(15,2),
    kg_liquido DECIMAL(15,2),
    valor_agregado DECIMAL(15,2),
    valor_seguro DECIMAL(15,2),
    valor_frete DECIMAL(15,2),
    id_modal_transporte INT,
    FOREIGN KEY (id_modal_transporte) REFERENCES modal_transporte(id_modal_transporte),
    FOREIGN KEY (id_unidade_receita_federal) REFERENCES unidade_receita_federal (id_unidade),
    FOREIGN KEY (id_produto) REFERENCES produto (id_ncm),
    FOREIGN KEY (id_pais) REFERENCES pais (id_pais),
    FOREIGN KEY (id_estado) REFERENCES estado (id_estado)
);

CREATE TABLE IF NOT EXISTS importacao_municipio (
    id_transacao INT PRIMARY KEY AUTO_INCREMENT,
    ano INT,
    mes INT,
    tipo_transacao ENUM('exp', 'imp'),
    id_sh4 VARCHAR(4),
    id_pais INT,
    id_municipio INT,
    valor_fob DECIMAL(15,2),
    kg_liquido DECIMAL(15,2),
    valor_agregado DECIMAL(15,2),
    valor_seguro DECIMAL(15,2),
    valor_frete DECIMAL(15,2),
    FOREIGN KEY (id_sh4) REFERENCES sh4 (id_sh4),
    FOREIGN KEY (id_pais) REFERENCES pais (id_pais),
    FOREIGN KEY (id_municipio) REFERENCES municipio (id_municipio)
);

CREATE TABLE IF NOT EXISTS exportacao_municipio (
    id_transacao INT PRIMARY KEY AUTO_INCREMENT,
    ano INT,
    mes INT,
    tipo_transacao ENUM('exp', 'imp'),
    id_sh4 VARCHAR(4),
    id_pais INT,
    id_municipio INT,
    valor_fob DECIMAL(15,2),
    kg_liquido DECIMAL(15,2),
    valor_agregado DECIMAL(15,2),
    FOREIGN KEY (id_sh4) REFERENCES sh4 (id_sh4),
    FOREIGN KEY (id_pais) REFERENCES pais (id_pais),
    FOREIGN KEY (id_municipio) REFERENCES municipio (id_municipio)
);
'''