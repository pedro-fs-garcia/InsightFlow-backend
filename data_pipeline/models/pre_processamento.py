from threading import Thread
from typing import List, Literal
import pandas as pd
from psycopg2 import Error
import os

from data_pipeline.models.gera_dataframes import GeradorDeDataFrames

from .tabelasComexStat import TabelasComexStat
from app.utils.logging_config import app_logger, error_logger


class PreProcessador:
    def __init__(self):
        self.tabelas = TabelasComexStat()
        self.base_df = GeradorDeDataFrames()
        self.output_dir:str = "data_pipeline/datasets/dados_agregados"
        self.transacoes_exp = pd.DataFrame({})
        self.transacoes_imp = pd.DataFrame({})

        t1 = Thread(target=self.init_transacoes, args=("EXP", False))
        t2 = Thread(target=self.init_transacoes, args=("IMP", False))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
    
    def init_transacoes(self, tipo: Literal["EXP", "IMP"], mun:bool) -> None:
        tx = self.base_df.gera_transacoes_df(tipo, mun)
        if tipo == "EXP":
            self.transacoes_exp = tx
        else:
            self.transacoes_imp = tx


    def salvar_tabela(self, tabela:pd.DataFrame, file_name:str) -> None:
        os.makedirs(self.output_dir, exist_ok=True)
        output_path = f"{self.output_dir}/{file_name}.csv"
        tabela.to_csv(output_path, index=False, encoding='latin1')
        app_logger.info(f"Tabela salva em: {output_path}") 


    def agregado_anual_estado_pais_ncm(self) -> pd.DataFrame:
        app_logger.info("Criando agregado anual unificado de exportação e importação por estado, país e NCM.")

        # Dados de exportação
        df_export = self.transacoes_exp.groupby(
            ['SG_UF_NCM', 'CO_ANO', 'CO_NCM', 'CO_PAIS'],
            as_index=False
        ).agg({
            'VL_FOB': 'sum',
            'KG_LIQUIDO': 'sum'
        }).rename(columns={
            'VL_FOB': 'VL_FOB_EXP',
            'KG_LIQUIDO': 'KG_LIQUIDO_EXP'
        })

        # Dados de importação
        df_import = self.transacoes_imp.groupby(
            ['SG_UF_NCM', 'CO_ANO', 'CO_NCM', 'CO_PAIS'],
            as_index=False
        ).agg({
            'VL_FOB': 'sum',
            'KG_LIQUIDO': 'sum'
        }).rename(columns={
            'VL_FOB': 'VL_FOB_IMP',
            'KG_LIQUIDO': 'KG_LIQUIDO_IMP'
        })

        # Fazer a junção (merge) pelos campos em comum
        df_final = pd.merge(
            df_export, df_import,
            on=['SG_UF_NCM', 'CO_ANO', 'CO_NCM', 'CO_PAIS'],
            how='outer'  # Outer para garantir que não perca registros que existem só em um dos lados
        )

        # Preencher valores nulos com 0 (onde não tem exportação ou importação)
        df_final[['VL_FOB_EXP', 'KG_LIQUIDO_EXP', 'VL_FOB_IMP', 'KG_LIQUIDO_IMP']] = df_final[[
            'VL_FOB_EXP', 'KG_LIQUIDO_EXP', 'VL_FOB_IMP', 'KG_LIQUIDO_IMP'
        ]].fillna(0)

        app_logger.info("Fim da criação do agregado anual unificado.")
        print("Tamanho do dataframe: ", len(df_final))
        return df_final

    
    def balanca_comercial_mensal_estado_pais(self) -> pd.DataFrame:
        app_logger.info("Criando balanca comercial por estado")
        df_exp_grouped = self.transacoes_exp.groupby(['CO_ANO', 'CO_MES', 'CO_PAIS', 'SG_UF_NCM'], as_index=False).agg(
            total_exportado=('VL_FOB', 'sum')
        )
        df_imp_grouped = self.transacoes_imp.groupby(['CO_ANO', 'CO_MES', 'CO_PAIS', 'SG_UF_NCM'], as_index=False).agg(
            total_importado=('VL_FOB', 'sum')
        )
        df_balanca = pd.merge(
            df_exp_grouped, 
            df_imp_grouped, 
            on=['CO_ANO', 'CO_MES', 'CO_PAIS', 'SG_UF_NCM'], 
            how='outer'
        )
        df_balanca['total_exportado'] = df_balanca['total_exportado'].fillna(0)
        df_balanca['total_importado'] = df_balanca['total_importado'].fillna(0)
        df_balanca['balanca_comercial'] = df_balanca['total_exportado'] - df_balanca['total_importado']
        df_balanca = df_balanca.sort_values(by=['CO_ANO', 'CO_MES'])
        app_logger.info("Fim da criação de balanca comercial por estado")
        return df_balanca
    

    def agregado_por_sh4_anual_estado(self) -> pd.DataFrame:
        app_logger.info("Criando agregado por sh4")
        ncm_df = self.base_df.gera_ncm_df()
        df_exp_merged = self.transacoes_exp.merge(ncm_df[['CO_NCM', 'CO_SH4']], left_on='CO_NCM', right_on='CO_NCM')
        df_exp_grouped = df_exp_merged.groupby(['CO_SH4', 'CO_ANO', 'SG_UF_NCM'], as_index=False).agg(
            valor_fob_exp=('VL_FOB', 'sum'),
            kg_liquido_exp=('KG_LIQUIDO', 'sum')
        )
        
        df_imp_merged = self.transacoes_imp.merge(ncm_df[['CO_NCM', 'CO_SH4']], left_on='CO_NCM', right_on='CO_NCM')
        df_imp_grouped = df_imp_merged.groupby(['CO_SH4', 'CO_ANO', 'SG_UF_NCM'], as_index=False).agg(
            valor_fob_imp=('VL_FOB', 'sum'),
            kg_liquido_imp=('KG_LIQUIDO', 'sum')
        )
        
        df_vlfob_setores = pd.merge(
            df_exp_grouped,
            df_imp_grouped,
            on=['CO_SH4', 'CO_ANO', 'SG_UF_NCM'],
            how='outer'
        )
        
        for col in ['valor_fob_exp', 'valor_fob_imp', 'kg_liquido_exp', 'kg_liquido_imp']:
            df_vlfob_setores[col] = df_vlfob_setores[col].fillna(0)
        app_logger.info("Fim da criação do agregado por sh4")
        return df_vlfob_setores


    def ranking_ncm_estados(self,
        tipo: Literal['EXP', 'IMP'],
        qtd: int = 100,
        anos: tuple[int, ...] = None,
        meses: tuple[int, ...] | None = None,
        paises: tuple[int, ...] | None = None,
        estados: tuple[int, ...] | None = None,
        crit: Literal['valor_fob', 'valor_agregado'] = 'valor_fob',
        cresc: Literal[1, 0] = 0,
    ) -> pd.DataFrame:
        app_logger.info("criando ranking de ncm por estados")
        df_ncm: pd.DataFrame = self.base_df.gera_ncm_df()
        if tipo == 'EXP': 
            df = self.transacoes_exp
        else:
            df = self.transacoes_imp

        if anos:
            print("filtering")
            df = df[df['CO_ANO'].isin(anos)]
        if meses:
            df = df[df['CO_MES'].isin(meses)]
        if paises:
            df = df[df['CO_PAIS'].isin(paises)]
        if estados:
            df = df[df['SG_UF_NCM'].isin(estados)]

        df = df.groupby('CO_NCM', as_index=False).agg({
            'VL_FOB': 'sum',
            'KG_LIQUIDO': 'sum'
        })

        df['valor_agregado'] = df['VL_FOB'] / df['KG_LIQUIDO'].replace(0, pd.NA)

        df = df.merge(df_ncm[['CO_NCM', 'NO_NCM_POR']], left_on='CO_NCM', right_on='CO_NCM', how='left')

        col_map = {
            'valor_fob': 'VL_FOB',
            'kg_liquido': 'KG_LIQUIDO',
            'valor_agregado': 'valor_agregado'
        }
        print("sorting")
        sort_cols = [col_map[crit]]
        if anos: 
            sort_cols.insert(0, 'CO_ANO')

        df = df.sort_values(by=sort_cols, ascending=bool(cresc))
        app_logger.info("Fim do rankeamento de ncm por estados")
        return df
        # return df.head(qtd)


    def salvar_dados_agregados(self, max_threads=2):  # ajuste max_threads conforme a memória disponível
        from concurrent.futures import ThreadPoolExecutor, as_completed

        def gerar_e_salvar(func:function, nome:str, *args, **kwargs):
            df = func(*args, **kwargs)
            self.salvar_tabela(df, nome)

        tarefas = [
            ("mv_agregado_anual", self.agregado_anual_estado_pais_ncm, ()),
            ("mv_balanca_comercial", self.balanca_comercial_mensal_estado_pais, ()),
            ("mv_vlfob_setores", self.agregado_por_sh4_anual_estado, ()),
            # ("ranking_ncm_exp", self.ranking_ncm_estados, ('EXP',)),
            # ("ranking_ncm_exp_por_ano", self.ranking_ncm_estados, ('EXP',), {'anos': tuple(range(2014, 2025))}),
            # ("ranking_ncm_imp", self.ranking_ncm_estados, ('IMP',)),
        ]

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = []
            for nome, func, args, *rest in tarefas:
                kwargs = rest[0] if rest else {}
                futures.append(executor.submit(gerar_e_salvar, func, nome, *args, **kwargs))

            for future in as_completed(futures):
                try:
                    future.result()  # Captura exceções se houver
                except Exception as e:
                    print(f"Erro em uma das tarefas: {future.__str__()} {e}")
