from mysql.connector import Error, connect
import pandas as pd

from data_pipeline.models.tabelasComexStat import TabelasComexStat
from app.utils.logging_config import app_logger, error_logger


class BuildDatabase:
    def __init__(self, config:dict):
        self.conn = connect(**config)
        self.tabelas = TabelasComexStat()


    def close_connection(self):
        if self.conn: self.conn.close()


    def registra_paises(self) -> None:
        pais_df = pd.read_csv(self.tabelas.auxiliar('PAIS'), delimiter=';' ,encoding='latin1')
        try:
            with self.conn.cursor() as cur:
                for _, row in pais_df.iterrows():
                    id_pais = row['CO_PAIS']
                    nome = row['NO_PAIS']
                    cur.execute(
                        "INSERT INTO pais (id_pais, nome, id_bloco) VALUES (%s, %s)",
                        (id_pais, nome)
                    )
                self.conn.commit()
                app_logger.info("Paises cadastrados no banco de dados com sucesso")
        except Error as e:
            self.conn.rollback()
            error_logger.error("Erro ao cadastrar paises no banco de dados: %s", str(e))

    
    def registra_blocos(self) -> None:
        bloco_df = pd.read_csv(self.tabelas.auxiliar('PAIS_BLOCO'), delimiter=';', encoding='latin1')
        blocos = bloco_df.drop_duplicates(subset=["CO_BLOCO"])
        try:
            with self.conn.cursor() as cur:        
                for _, row in blocos.iterrows():
                    id_bloco = row["CO_BLOCO"]
                    nome_bloco = row["NO_BLOCO"]
                    cur.execute(
                        "INSERT INTO bloco (id_bloco, nome) VALUES (%s, %s) ON DUPLICATE KEY UPDATE nome = VALUES(nome)", 
                        (id_bloco, nome_bloco)
                    )
                for _, row in bloco_df.iterrows():
                    id_pais = row['CO_PAIS']
                    id_bloco = row['CO_BLOCO']
                    cur.execute(
                        "UPDATE pais SET id_bloco = %s WHERE id_pais = %s",
                        (id_bloco, id_pais)
                    )
                self.conn.commit()
                app_logger.info("Blocos cadastrados no banco de dados com sucesso")
        except Error as e:
            self.conn.rollback()
            error_logger.error("Erro ao cadastrar blocos no banco de dados: %s", str(e))

    
    def registra_estados(self) -> None:
        estados_df = pd.read_csv(self.tabelas.auxiliar('UF'), delimiter=';', encoding='latin1')
        try:
            with self.conn.cursor() as cur:
                for _, row in estados_df.iterrows():
                    id_estado = row['CO_UF']
                    sigla = row['SG_UF']
                    nome=row['NO_UF']
                    regiao = row['NO_REGIAO']
                    cur.execute(
                        "INSERT INTO estado (id_estado, sigla, nome, regiao) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE sigla = VALUES(sigla), nome = VALUES(nome), regiao = VALUES(regiao)",
                        (id_estado, sigla, nome, regiao)
                    )
                self.conn.commit()
                app_logger.info("Estados cadastrados no banco de dados com sucesso")
        except Error as e:
            self.conn.rollback()
            error_logger.error("Erro ao cadastrar estados no banco de dados: %s", str(e))


    def registra_municipios(self) -> None:
        mun_df = pd.read_csv(self.tabelas.auxiliar('UF_MUN'), delimiter=';', encoding='latin1')
        estados_df = pd.read_csv(self.tabelas.auxiliar('UF'), delimiter=';', encoding='latin1')
        mun_df = mun_df.merge(estados_df, on="SG_UF", how="left")
        try:
            with self.conn.cursor() as cur:
                for _, row in mun_df.iterrows():
                    id_municipio = row['CO_MUN_GEO']
                    nome = row['NO_MUN_MIN']
                    id_estado = row['CO_UF']
                    cur.execute(
                        "INSERT INTO municipio (id_municipio, nome, id_estado) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE nome = VALUES(nome), id_estado = VALUES(id_estado)",
                        (id_municipio, nome, id_estado)
                    )
                self.conn.commit()
                app_logger.info("Municípios cadastrados no banco de dados com sucesso")
        except Error as e:
            self.conn.rollback()
            error_logger.error("Erro ao cadastrar municipios no banco de dados: %s", str(e))


    def registra_modal_transporte(self) -> None:
        via_df = pd.read_csv(self.tabelas.auxiliar('VIA'), delimiter=';', encoding='latin1')
        try:
            with self.conn.cursor() as cur:
                for _, row in via_df.iterrows():
                    id_modal = row['CO_VIA']
                    descricao = ['NO_VIA']
                    cur.execute(
                        "INSERT INTO modal_transporte (id_modal, descricao) VALUES (%s, %s) ON DUPLICATE KEY UPDATE descricao = VALUES(descricao)",
                        (id_modal, descricao)
                    )
                self.conn.commit()
                app_logger.info("Modais de transporte cadastrados no banco de dados com sucesso")
        except Error as e:
            self.conn.rollback()
            error_logger.error("Erro ao cadastrar modais de transporte no banco de dados: %s", str(e))


    def registra_urfs(self) -> None:
        urf_df = pd.read_csv(self.tabelas.auxiliar('URF'), delimiter=';', encoding='latin1')
        try:
            with self.conn.cursor() as cur:
                for _, row in urf_df:
                    id_unidade = row['CO_URF']
                    nome = row['NO_URF'].split(' - ')[1]
                    cur.execute(
                        "INSERT INTO unidade_receita_federal (id_unidade, nome) VALUES (%s, %s) ON DUPLICATE KEY UPDATE nome = VALUES(nome)",
                        (id_unidade, nome)
                    )
                self.conn.commit()
                app_logger.info("URFs cadastrados no banco de dados com sucesso")
        except Error as e:
            self.conn.rollback()
            error_logger.error("Erro ao cadastrar URFs no banco de dados: %s", str(e))


    def registra_cgce_n3(self) -> None:
        cg_df = pd.read_csv(self.tabelas.auxiliar('NCM_CGCE'), delimiter=';', encoding='latin1')
        cg_df = cg_df.drop_duplicates(subset=['CO_CGCE_N3'])
        try:
            with self.conn.cursor() as cur:
                for _, row in cg_df.iterrows():
                    id_n3 = row['CO_CGCE_N3']
                    descricao = row['NO_CGCE_N3']
                    cur.execute(
                        "INSERT INTO cgce_n3 (id_n3, descricao) VALUES (%s, %s) ON DUPLICATE KEY UPDATE descricao = VALUES(descricao)",
                        (id_n3, descricao)
                    )
                self.conn.commit()
                app_logger.info("Códigos CGCE_N3 cadastrados no banco de dados com sucesso")
        except Error as e:
            self.conn.rollback()
            error_logger.error("Erro ao cadastrar códigos CGCE_N3 no banco de dados: %s", str(e))
        

    def registra_sh(self) -> None:
        file_url = 'data_pipeline/tabelas_auxiliares/codigos.csv'
        sh_df = pd.read_csv(file_url, delimiter=';', encoding='latin1')
        sh4 = sh_df.drop_duplicates(subset=['CO_SH4'])
        sh2 = sh_df.drop_duplicates(subset=['CO_SH2'])
        try:
            with self.conn.cursor() as cur:
                for _, row in sh4.iterrows():
                    id_sh4 = row['CO_SH4']
                    descricao = row['NO_SH4_POR']
                    cur.execute(
                        "INSERT INTO sh4 (id_sh4, descricao) VALUES (%s, %s) ON DUPLICATE KEY UPDATE descricao = VALUES(descricao)",
                        (id_sh4, descricao)
                    )
                
                for _, row in sh2.iterrows():
                    id_sh2 = row['CO_SH2']
                    descricao = row['NO_SH2_POR']
                    cur.execute(
                        "INSERT INTO sh2 (id_sh2, descricao) VALUES (%s, %s) ON DUPLICATE KEY UPDATE descricao = VALUES(descricao)",
                        (id_sh2, descricao)
                    )

                self.conn.commit()
                app_logger.info("códigos SH2 cadastrados no banco de dados com sucesso")
        except Error as e:
            self.conn.rollback()
            error_logger.error("Erro ao cadastrar códigos SH2 no banco de dados: %s", str(e))


    def registra_produto(self) -> None:
        try:
            with self.conn.cursor() as cur:
                a = 0
                self.conn.commit()
                app_logger.info("Produtos cadastrados no banco de dados com sucesso")
        except Error as e:
            self.conn.rollback()
            error_logger.error("Erro ao cadastrar produtos no banco de dados: %s", str(e))


    def registra_transacao_comercial(self) -> None:
        try:
            with self.conn.cursor() as cur:
                a = 0
                self.conn.commit()
                app_logger.info("Transações comerciais cadastrados no banco de dados com sucesso")
        except Error as e:
            self.conn.rollback()
            error_logger.error("Erro ao cadastrar transações comerciais no banco de dados: %s", str(e))
        return
        

    def buid_db(self) -> None:
        self.registra_paises()
        self.registra_blocos()
        self.registra_estados()
        self.registra_municipios()
        self.registra_modal_transporte()
        self.registra_urfs()
        self.registra_cgce_n3()
        self.registra_sh()
        self.registra_produto()
        self.registra_transacao_comercial()
        