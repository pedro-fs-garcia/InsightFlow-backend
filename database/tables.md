```sql
CREATE TABLE estado (
    id_estado INT PRIMARY KEY,
    sigla VARCHAR(2) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    regiao VARCHAR(100) NOT NULL
);

CREATE TABLE municipio (
    id_municipio INT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    id_estado INT NOT NULL,
    FOREIGN KEY (id_estado) REFERENCES estado(id_estado)
);

CREATE TABLE bloco (
    id_bloco INT PRIMARY KEY,
    nome_bloco VARCHAR(100) NOT NULL
);

CREATE TABLE pais (
    id_pais INT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    id_bloco INT,
    FOREIGN KEY (id_bloco) REFERENCES bloco(id_bloco)
);

CREATE TABLE unidade_receita_federal (
    id_unidade INT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    localizacao VARCHAR(255) NOT NULL
);

CREATE TABLE sh2 (
    id_sh2 INT PRIMARY KEY,
    descricao VARCHAR(255) NOT NULL
);

CREATE TABLE sh4 (
    id_sh4 INT PRIMARY KEY,
    descricao VARCHAR(255) NOT NULL
);

CREATE TABLE cgce_n3 (
    id_n3 INT PRIMARY KEY,
    descricao VARCHAR(255) NOT NULL
);

CREATE TABLE modal_transporte (
    id_modal INT PRIMARY KEY,
    descricao VARCHAR(255) NOT NULL
);

CREATE TABLE produto (
    id_ncm INT PRIMARY KEY,
    descricao VARCHAR(255) NOT NULL,
    id_sh4 INT NOT NULL,
    id_cgce_n3 INT NOT NULL,
    id_sh2 INT NOT NULL,
    FOREIGN KEY (id_sh4) REFERENCES sh4(id_sh4),
    FOREIGN KEY (id_cgce_n3) REFERENCES cgce_n3(id_n3),
    FOREIGN KEY (id_sh2) REFERENCES sh2(id_sh2)
);

CREATE TABLE transacao_comercial (
    id_transacao INT PRIMARY KEY AUTO_INCREMENT,
    valor_fob DECIMAL(15,2) NOT NULL,
    valor_seguro DECIMAL(15,2),
    ano INT NOT NULL,
    mes INT NOT NULL,
    tipo_transacao ENUM('exp', 'imp') NOT NULL,
    quantidade INT,
    valor_frete DECIMAL(15,2),
    kg_liquido DECIMAL(15,2),
    nome_unid VARCHAR(50),
    id_unidade_receita_federal INT NOT NULL,
    id_produto INT NOT NULL,
    id_pais INT NOT NULL,
    id_municipio INT,
    id_estado INT NOT NULL,
    id_modal INT NOT NULL,
    FOREIGN KEY (id_unidade_receita_federal) REFERENCES unidade_receita_federal(id_unidade),
    FOREIGN KEY (id_produto) REFERENCES produto(id_ncm),
    FOREIGN KEY (id_pais) REFERENCES pais(id_pais),
    FOREIGN KEY (id_municipio) REFERENCES municipio(id_municipio),
    FOREIGN KEY (id_estado) REFERENCES estado(id_estado),
    FOREIGN KEY (id_modal) REFERENCES modal_transporte(id_modal)
);


```