create_tables_script = '''
CREATE TABLE municipio 
( 
    id_municipio INT PRIMARY KEY,  
    nome VARCHAR(100)  
); 

CREATE TABLE estado 
( 
    id_estado INT PRIMARY KEY,  
    sigla VARCHAR(2),  
    nome VARCHAR(100),  
    id_municipio INT,  
    FOREIGN KEY(id_municipio) REFERENCES municipio(id_municipio)
); 

CREATE TABLE produto 
( 
    id_produto INT PRIMARY KEY,  
    descricao VARCHAR(255),  
    codigo_ncm VARCHAR(10),  
    codigo_sh4 VARCHAR(10)  
); 

CREATE TABLE transacao_comercial 
( 
    id_transacao INT PRIMARY KEY,  
    valor_fob DECIMAL(10,2),  
    valor_seguro DECIMAL(10,2),  
    ano INT,  
    mes INT,  
    tipo_transacao VARCHAR(50),  
    quantidade INT,  
    valor_frete DECIMAL(10,2)  
); 

CREATE TABLE pais 
( 
    id_pais INT PRIMARY KEY,  
    nome VARCHAR(100)  
); 

CREATE TABLE origem_destino 
( 
    id_transacao INT PRIMARY KEY,  
    tipo VARCHAR(50),  
    FOREIGN KEY(id_transacao) REFERENCES transacao_comercial(id_transacao)
); 

CREATE TABLE modal_transporte 
( 
    id_modal INT PRIMARY KEY,  
    descricao VARCHAR(255)  
); 

CREATE TABLE transporte_transacao 
( 
    id_transacao INT PRIMARY KEY,  
    id_transacao_comercial INT,  
    descricao_adicional VARCHAR(255),  
    FOREIGN KEY(id_transacao_comercial) REFERENCES transacao_comercial(id_transacao)  
); 

CREATE TABLE processamento_rf 
( 
    id_transacao INT PRIMARY KEY,  
    status VARCHAR(50),  
    id_transacao_comercial INT,  
    FOREIGN KEY(id_transacao_comercial) REFERENCES transacao_comercial(id_transacao)  
); 

CREATE TABLE unidade_receita_federal 
( 
    id_unidade INT PRIMARY KEY,  
    nome VARCHAR(100),  
    localizacao VARCHAR(255),  
    id_processamento_rf INT,  
    FOREIGN KEY(id_processamento_rf) REFERENCES processamento_rf(id_transacao)  
); 

CREATE TABLE participa 
( 
    id_transacao INT,  
    id_estado INT,  
    PRIMARY KEY(id_transacao, id_estado),  
    FOREIGN KEY(id_transacao) REFERENCES transacao_comercial(id_transacao),  
    FOREIGN KEY(id_estado) REFERENCES estado(id_estado)  
); 

CREATE TABLE registra 
( 
    id_municipio INT,  
    id_transacao INT,  
    PRIMARY KEY(id_municipio, id_transacao),  
    FOREIGN KEY(id_municipio) REFERENCES municipio(id_municipio),  
    FOREIGN KEY(id_transacao) REFERENCES transacao_comercial(id_transacao)  
); 

CREATE TABLE envolve 
( 
    id_produto INT,  
    id_transacao INT,  
    PRIMARY KEY(id_produto, id_transacao),  
    FOREIGN KEY(id_produto) REFERENCES produto(id_produto),  
    FOREIGN KEY(id_transacao) REFERENCES transacao_comercial(id_transacao)  
); 

CREATE TABLE possui 
( 
    id_transacao_origem INT,  
    id_transacao_destino INT,  
    PRIMARY KEY(id_transacao_origem, id_transacao_destino),  
    FOREIGN KEY(id_transacao_origem) REFERENCES origem_destino(id_transacao),  
    FOREIGN KEY(id_transacao_destino) REFERENCES transacao_comercial(id_transacao)  
); 

CREATE TABLE usado_em 
( 
    id_transacao INT,  
    id_modal INT,  
    PRIMARY KEY(id_transacao, id_modal),  
    FOREIGN KEY(id_transacao) REFERENCES transporte_transacao(id_transacao),  
    FOREIGN KEY(id_modal) REFERENCES modal_transporte(id_modal)  
); 

CREATE TABLE referencia 
( 
    id_transacao INT,  
    id_pais INT,  
    PRIMARY KEY(id_transacao, id_pais),  
    FOREIGN KEY(id_transacao) REFERENCES origem_destino(id_transacao),  
    FOREIGN KEY(id_pais) REFERENCES pais(id_pais)  
);

-- ALTER TABLE statements
ALTER TABLE estado ADD FOREIGN KEY(id_municipio) REFERENCES municipio(id_municipio);
ALTER TABLE transporte_transacao ADD FOREIGN KEY(id_transacao_comercial) REFERENCES transacao_comercial(id_transacao);
ALTER TABLE unidade_receita_federal ADD FOREIGN KEY(id_processamento_rf) REFERENCES processamento_rf(id_transacao);
ALTER TABLE processamento_rf ADD FOREIGN KEY(id_transacao_comercial) REFERENCES transacao_comercial(id_transacao);
ALTER TABLE participa ADD FOREIGN KEY(id_transacao) REFERENCES transacao_comercial(id_transacao);
ALTER TABLE participa ADD FOREIGN KEY(id_estado) REFERENCES estado(id_estado);
ALTER TABLE registra ADD FOREIGN KEY(id_municipio) REFERENCES municipio(id_municipio);
ALTER TABLE registra ADD FOREIGN KEY(id_transacao) REFERENCES transacao_comercial(id_transacao);
ALTER TABLE envolve ADD FOREIGN KEY(id_produto) REFERENCES produto(id_produto);
ALTER TABLE envolve ADD FOREIGN KEY(id_transacao) REFERENCES transacao_comercial(id_transacao);
ALTER TABLE possui ADD FOREIGN KEY(id_transacao_origem) REFERENCES origem_destino(id_transacao);
ALTER TABLE possui ADD FOREIGN KEY(id_transacao_destino) REFERENCES transacao_comercial(id_transacao);
ALTER TABLE usado_em ADD FOREIGN KEY(id_transacao) REFERENCES transporte_transacao(id_transacao);
ALTER TABLE usado_em ADD FOREIGN KEY(id_modal) REFERENCES modal_transporte(id_modal);
ALTER TABLE referencia ADD FOREIGN KEY(id_transacao) REFERENCES origem_destino(id_transacao);
ALTER TABLE referencia ADD FOREIGN KEY(id_pais) REFERENCES pais(id_pais);
'''