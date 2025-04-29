from typing import Literal
from data_pipeline.models.tabelasComexStat import TabelasComexStat
import pandas as pd
from app.utils.logging_config import app_logger, error_logger

class GeradorDeDataFrames():
    def __init__(self):
        self.tabelas = TabelasComexStat()
    

    def gera_tabela_url(self, ano:int, nome_arquivo:str, mun:bool):
        if mun:
            nome_arquivo += f"_MUN"
        tabela_url = f"./data_pipeline/datasets/limpo/{ano}/{nome_arquivo}.csv"
        return tabela_url


    def gera_transacoes_df(self, tipo: Literal["EXP", "IMP"], mun: bool):
        dfs = []
        for ano in range(2014, 2025):
            nome = f"{tipo}_{ano}"
            app_logger.info(f"Gerando dataframe de transações {nome}")
            ano_df = pd.read_csv(self.gera_tabela_url(ano, nome, mun), delimiter=',', encoding='latin1')
            dfs.append(ano_df)
        return pd.concat(dfs, ignore_index=True)

    
    def gera_paises_df(self) -> None:
        app_logger.info("Gerando dataframe de países")
        pais_df = pd.read_csv(self.tabelas.auxiliar('PAIS'), delimiter=';' ,encoding='latin1')
        pais_df = pais_df[['CO_PAIS', 'NO_PAIS']]
        return pais_df
    
    
    def gera_estados_df(self):
        app_logger.info("Gerando dataframe de estados")
        estados_df = pd.read_csv(self.tabelas.auxiliar('UF'), delimiter=';', encoding='latin1')
        estados_df = estados_df[['CO_UF', 'SG_UF', 'NO_UF', 'NO_REGIAO']]
        return estados_df
    

    def gera_municipios_df(self):
        app_logger.info("Gerando dataframe de municípios")
        mun_df = pd.read_csv(self.tabelas.auxiliar('UF_MUN'), delimiter=';', encoding='latin1')
        estados_df = pd.read_csv(self.tabelas.auxiliar('UF'), delimiter=';', encoding='latin1')
        mun_df = mun_df.merge(estados_df, on="SG_UF", how="left")
        mun_df = mun_df[['CO_MUN_GEO', 'NO_MUN_MIN', 'CO_UF']]
        return mun_df
    

    def gera_vias_df(self):
        app_logger.info("Gerando dataframe de vias")
        vias_df = pd.read_csv(self.tabelas.auxiliar('VIA'), delimiter=';', encoding='latin1')
        vias_df = vias_df[['CO_VIA', 'NO_VIA']]
        return vias_df
    
    
    def gera_urfs_df(self):
        app_logger.info("Gerando dataframe de urfs")
        urfs_df = pd.read_csv(self.tabelas.auxiliar('URF'), delimiter=';', encoding='latin1')
        urfs_df = urfs_df[['CO_URF', 'NO_URF']]
        return urfs_df
    
    
    def gera_sh4_df(self):
        app_logger.info("Gerando dataframe de sh4")
        file_url = 'data_pipeline/tabelas_auxiliares/codigos.csv'
        sh_df = pd.read_csv(file_url, delimiter=';', encoding='utf-8', dtype={'CO_SH4': str, 'CO_SH2': str})
        sh_df = sh_df[['CO_SH4', 'NO_SH4_POR', 'CO_SH2', 'NO_SH2_POR']]
        return sh_df
    

    def gera_ncm_df(self):
        app_logger.info("Gerando dataframe de ncm")
        ncm_df = pd.read_csv(self.tabelas.auxiliar('NCM'), delimiter=";", encoding="latin1", dtype={'CO_NCM': int})
        unidades_df = pd.read_csv(self.tabelas.auxiliar('NCM_UNIDADE'), delimiter=";", encoding="latin1")
        ncm_df = ncm_df.merge(unidades_df[['CO_UNID', 'NO_UNID']], on='CO_UNID', how='left')
        file_url = 'data_pipeline/tabelas_auxiliares/codigos.csv'
        sh_df = pd.read_csv(file_url, delimiter=';', encoding='latin1', dtype={'CO_NCM': int, 'CO_SH4': str, 'CO_SH2': str})
        ncm_df = ncm_df.merge(sh_df[['CO_NCM', 'CO_SH4', 'CO_SH2']], on='CO_NCM', how='left')
        ncm_df = ncm_df.where(pd.notna(ncm_df), None)
        ncm_df = ncm_df[['CO_NCM', 'NO_NCM_POR', 'NO_UNID', 'CO_SH4', 'CO_SH2', 'CO_CGCE_N3']]
        return ncm_df