create_tables_script = '''
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_transacao_enum') THEN
        CREATE TYPE tipo_transacao_enum AS ENUM ('exp', 'imp');
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS estado (
    id_estado SERIAL PRIMARY KEY,
    sigla VARCHAR(2),
    nome VARCHAR(100),
    regiao VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS municipio (
    id_municipio SERIAL PRIMARY KEY,
    nome VARCHAR(100),
    id_estado INT,
    FOREIGN KEY (id_estado) REFERENCES estado(id_estado)
);

CREATE TABLE IF NOT EXISTS bloco (
    id_bloco SERIAL PRIMARY KEY,
    nome_bloco VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS pais (
    id_pais SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    id_bloco INT,
    FOREIGN KEY (id_bloco) REFERENCES bloco(id_bloco)
);

CREATE TABLE IF NOT EXISTS unidade_receita_federal (
    id_unidade SERIAL PRIMARY KEY,
    nome VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS modal_transporte (
    id_modal_transporte SERIAL PRIMARY KEY,
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
    id_transacao SERIAL,
    ano INT,
    mes INT,
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
) PARTITION BY RANGE (ano);

-- Adicionar a chave primária na tabela particionada
ALTER TABLE exportacao_estado ADD PRIMARY KEY (id_transacao, ano);

CREATE TABLE IF NOT EXISTS importacao_estado (
    id_transacao SERIAL,
    ano INT,
    mes INT,
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
) PARTITION BY RANGE (ano);

-- Adicionar a chave primária na tabela particionada
ALTER TABLE importacao_estado ADD PRIMARY KEY (id_transacao, ano);

-- Criar partições para os anos
DO $$
DECLARE
    ano_atual INT := EXTRACT(YEAR FROM CURRENT_DATE);
    ano_inicio INT := 2014;
BEGIN
    FOR ano IN ano_inicio..ano_atual LOOP
        EXECUTE format('
            CREATE TABLE IF NOT EXISTS exportacao_estado_%s PARTITION OF exportacao_estado
            FOR VALUES FROM (%s) TO (%s);
        ', ano, ano, ano + 1);
        
        EXECUTE format('
            CREATE TABLE IF NOT EXISTS importacao_estado_%s PARTITION OF importacao_estado
            FOR VALUES FROM (%s) TO (%s);
        ', ano, ano, ano + 1);
    END LOOP;
END $$;

CREATE TABLE IF NOT EXISTS importacao_municipio (
    id_transacao SERIAL PRIMARY KEY,
    ano INT,
    mes INT,
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
    id_transacao SERIAL PRIMARY KEY,
    ano INT,
    mes INT,
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

CREATE INDEX IF NOT EXISTS idx_ano_id_produto ON exportacao_estado(ano, id_produto);
CREATE INDEX IF NOT EXISTS idx_ano_mes_estado ON exportacao_estado(ano, mes, id_estado);
CREATE INDEX IF NOT EXISTS idx_ano_mes_pais ON exportacao_estado(ano, mes, id_pais);
CREATE INDEX IF NOT EXISTS idx_ano_mes_estado_imp ON importacao_estado(ano, mes, id_estado);
CREATE INDEX IF NOT EXISTS idx_ano_mes_pais_imp ON importacao_estado(ano, mes, id_pais);
CREATE INDEX IF NOT EXISTS idx_ano_mes_municipio_exp ON exportacao_municipio(ano, mes, id_municipio);
CREATE INDEX IF NOT EXISTS idx_ano_mes_municipio_imp ON importacao_municipio(ano, mes, id_municipio);
CREATE INDEX IF NOT EXISTS idx_produto_sh4 ON produto(id_sh4);
CREATE INDEX IF NOT EXISTS idx_produto_sh2 ON produto(id_sh2);
CREATE INDEX IF NOT EXISTS idx_municipio_estado ON municipio(id_estado);
CREATE INDEX IF NOT EXISTS idx_pais_bloco ON pais(id_bloco);

CREATE EXTENSION IF NOT EXISTS unaccent;

-- Views Materializadas para consultas comuns
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_exportacao_estado_anual AS
SELECT 
    ano,
    id_estado,
    id_produto,
    id_pais,
    SUM(quantidade) as quantidade_total,
    SUM(valor_fob) as valor_fob_total,
    SUM(kg_liquido) as kg_liquido_total,
    SUM(valor_agregado) as valor_agregado_total
FROM exportacao_estado
GROUP BY ano, id_estado, id_produto, id_pais;

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_importacao_estado_anual AS
SELECT 
    ano,
    id_estado,
    id_produto,
    id_pais,
    SUM(quantidade) as quantidade_total,
    SUM(valor_fob) as valor_fob_total,
    SUM(kg_liquido) as kg_liquido_total,
    SUM(valor_agregado) as valor_agregado_total,
    SUM(valor_seguro) as valor_seguro_total,
    SUM(valor_frete) as valor_frete_total
FROM importacao_estado
GROUP BY ano, id_estado, id_produto, id_pais;

-- Índices para as views materializadas
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_exportacao_estado_anual ON mv_exportacao_estado_anual(ano, id_estado, id_produto, id_pais);
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_importacao_estado_anual ON mv_importacao_estado_anual(ano, id_estado, id_produto, id_pais);

-- Função para atualizar as views materializadas
CREATE OR REPLACE FUNCTION atualizar_views_materializadas()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_exportacao_estado_anual;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_importacao_estado_anual;
END;
$$ LANGUAGE plpgsql;
'''