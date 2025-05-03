import json
from typing import List, Literal
import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet

from data_pipeline.models.gera_dataframes import GeradorDeDataFrames
from app.utils.logging_config import app_logger, error_logger
from data_pipeline.models.pre_processamento import PreProcessador


class Vidente():
    def __init__(self):
        self.gd = GeradorDeDataFrames()
        self.output_dir = 'data_pipeline/datasets/dados_agregados'

        return


    def gerar_profecia(self, df_prophet:pd.DataFrame, nome_arquivo:str, titulo_graf:str, ylabel:str):
        profeta = Prophet()
        profeta.fit(df_prophet)
        futuro = profeta.make_future_dataframe(periods=24, freq='MS')
        previsao = profeta.predict(futuro)

        if len(df_prophet) < 2:
            print("Dados insuficientes para modelagem.")
            return

        profeta.plot(previsao)
        plt.title(titulo_graf)
        plt.xlabel('Data')
        plt.ylabel(ylabel)
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/{nome_arquivo}.png', dpi=300)
        plt.close()

        resultado = previsao[['ds', 'yhat']].copy()
        resultado['ds'] = resultado['ds'].astype(str)
        app_logger.info("Análise de tendencias por NCM finalizada")
        return resultado.to_dict(orient='records')


    def tendencia_vlfob_ncm(self, 
        tipo:Literal['EXP', 'IMP'], 
        ncm: int,
        estado: int | None = None, 
        pais: int | None = None,
    ) -> List[dict]:
        app_logger.info("Iniciando análies de tendências por NCM")
        df = self.gd.gera_transacoes_df(tipo, False)
        df = df.rename(columns={'SG_UF_NCM':'SG_UF'})
        df = df.merge(self.gd.gera_estados_df(), on="SG_UF", how="left")
        df = df.drop(columns=['NO_UF', 'NO_REGIAO', 'SG_UF'])
        df['CO_NCM'] = df['CO_NCM'].astype(int)
        df['CO_ANO'] = df['CO_ANO'].astype(int)
        df['CO_MES'] = df['CO_MES'].astype(int)
        
        df['DATA'] = pd.to_datetime(df['CO_ANO'].astype(str) + '-' + df['CO_MES'].astype(str).str.zfill(2))

        df = df[df['CO_NCM'] == ncm]
        if estado:
            df = df[df['CO_UF'] == estado]
        if pais:
            df = df[df['CO_PAIS'] == pais]

        df = df.groupby('DATA')[['VL_FOB']].sum().reset_index()
        df_prophet = df[['DATA', 'VL_FOB']].rename(columns={'DATA': 'ds', 'VL_FOB': 'y'})

        nome = f"tendencia_anual_ncm_{ncm}"
        if estado:
            nome += f"_{estado}"
        if pais:
            nome += f"_{pais}"

        self.gerar_profecia(df_prophet, nome, f"Previsão de Valor FOB de {tipo}", "Valor FOB ($)")


    def tendencia_saldo_ncm(self, 
        ncm: int,
        estado: int | None = None, 
        pais: int | None = None,
    ) -> List[dict]:
        dfs = []
        for tipo in ('IMP', 'EXP'):
            df = self.gd.gera_transacoes_df(tipo, False)
            df['CO_NCM'] = df['CO_NCM'].astype(int)
            df['CO_ANO'] = df['CO_ANO'].astype(int)
            df['CO_MES'] = df['CO_MES'].astype(int)
            df['DATA'] = pd.to_datetime(df['CO_ANO'].astype(str) + '-' + df['CO_MES'].astype(str).str.zfill(2))
            
            df = df[df['CO_NCM'] == ncm]
            if estado:
                df = df.rename(columns={'SG_UF_NCM':'SG_UF'})
                df = df.merge(self.gd.gera_estados_df(), on="SG_UF", how="left")
                df = df.drop(columns=['NO_UF', 'NO_REGIAO', 'SG_UF', 'KG_LIQUIDO'])
                df = df[df['CO_UF'] == estado]
            if pais:
                df = df[df['CO_PAIS'] == pais]

            df = df.groupby('DATA')[['VL_FOB']].sum().reset_index()
            dfs.append(df)

        df_imp = dfs[0].rename(columns={'VL_FOB': 'VL_FOB_IMP'})
        df_exp = dfs[1].rename(columns = {'VL_FOB': 'VL_FOB_EXP'})
        del dfs
        # Fazer a junção (merge) pelos campos em comum
        df_final = pd.merge(
            df_exp, df_imp,
            on=['DATA'],
            how='outer'  # Outer para garantir que não perca registros que existem só em um dos lados
        )
        del df_exp
        del df_imp

        # Preencher valores nulos com 0 (onde não tem exportação ou importação)
        df_final[['VL_FOB_EXP', 'VL_FOB_IMP']] = df_final[['VL_FOB_EXP', 'VL_FOB_IMP']].fillna(0)

        df_final['balanca_comercial'] = df_final['VL_FOB_EXP'] - df_final['VL_FOB_IMP']
        print(df_final.head(10))

        df_prophet = df_final[['DATA', 'balanca_comercial']].rename(columns={'DATA': 'ds', 'balanca_comercial': 'y'})
        del df_final

        nome = f"tendencia_saldo_ncm_{ncm}"
        if estado:
            nome += f"_{estado}"
        if pais:
            nome += f"_{pais}"

        self.gerar_profecia(df_prophet, nome, f"Previsao de Balança Comercial para {ncm}", "Saldo ($)")


    def tendencia_saldo_setores(self, 
        estado: int | None = None,
        pais: int | None = None 
    ) -> List[dict]:
        app_logger.info("Iniciando análise de tendências de setor economico")
        with open('data_pipeline/tabelas_auxiliares/setores.json', 'r', encoding='utf-8') as f:
            setores = json.load(f)

        ncm_df = self.gd.gera_ncm_df()[['CO_NCM', 'CO_SH4']]
        ncm_df['CO_NCM'] = ncm_df['CO_NCM'].astype('int32')
        ncm_df['CO_SH4'] = ncm_df['CO_SH4'].astype(str)
        
        # Processa exportações e importações em chunks
        def process_transactions_in_chunks(tipo: str, chunk_size: int = 100000):
            chunks = []
            df = self.gd.gera_transacoes_df(tipo, False)
            
            for i in range(0, len(df), chunk_size):
                chunk = df.iloc[i:i + chunk_size].copy()
                
                chunk['CO_NCM'] = chunk['CO_NCM'].astype('int32')
                chunk['CO_ANO'] = chunk['CO_ANO'].astype('int16')
                chunk['CO_MES'] = chunk['CO_MES'].astype('int8')
                chunk['DATA'] = pd.to_datetime(
                    chunk['CO_ANO'].astype(str) + '-' + 
                    chunk['CO_MES'].astype(str).str.zfill(2)
                )
                
                if estado:
                    chunk = chunk.rename(columns={'SG_UF_NCM':'SG_UF'})
                    estados_df = self.gd.gera_estados_df()
                    estados_df['CO_UF'] = estados_df['CO_UF'].astype('int32')
                    chunk = chunk.merge(estados_df, on="SG_UF", how="left")
                    chunk = chunk.drop(columns=['NO_UF', 'NO_REGIAO', 'SG_UF'])
                    chunk = chunk[chunk['CO_UF'] == estado]
                if pais:
                    chunk = chunk[chunk['CO_PAIS'] == pais]

                chunk = chunk.merge(ncm_df, on='CO_NCM', how='left')
                chunk = chunk.groupby(['CO_SH4', 'DATA'], as_index=False)['VL_FOB'].sum()
                chunk = chunk.rename(columns={'VL_FOB': f'vl_fob_{tipo.lower()}'})
                
                chunks.append(chunk)
                del chunk

            result = pd.concat(chunks, ignore_index=True)
            del chunks
            return result

        df_exp = process_transactions_in_chunks('EXP')
        df_imp = process_transactions_in_chunks('IMP')

        df_vlfob_setores = pd.merge(
            df_exp,
            df_imp,
            on=['CO_SH4', 'DATA'],
            how='outer'
        )
        
        del df_exp, df_imp

        df_vlfob_setores['vl_fob_exp'] = df_vlfob_setores['vl_fob_exp'].fillna(0)
        df_vlfob_setores['vl_fob_imp'] = df_vlfob_setores['vl_fob_imp'].fillna(0)
        df_vlfob_setores['saldo'] = df_vlfob_setores['vl_fob_exp'] - df_vlfob_setores['vl_fob_imp']
        
        setores_to_process = {
            'agronegocio': setores['Agronegócio']['sh4'],
            'industria': setores['Indústria']['sh4'],
            'mineracao': setores['Mineração']['sh4'],
            'florestal': setores['Setor Florestal']['sh4'],
            'tecnologia': setores['Tecnologia']['sh4'],
            'bens_consumo': setores['Bens de consumo']['sh4']
        }

        for setor_nome, sh4_codes in setores_to_process.items():
            sh4_codes = [str(code) for code in sh4_codes]
            
            df_setor = df_vlfob_setores[df_vlfob_setores['CO_SH4'].isin(sh4_codes)]
            df_setor = df_setor.groupby('DATA')['saldo'].sum().reset_index()
            df_prophet = df_setor.rename(columns={'DATA': 'ds', 'saldo': 'y'})
            
            self.gerar_profecia(
                df_prophet, 
                f"tendencia_setor_{setor_nome}", 
                f"Setor {setor_nome.replace('_', ' ').title()}", 
                "Valor FOB ($)"
            )
            
            del df_setor, df_prophet

        return


    def tendencia_vlfob(self, 
        crit:Literal['total_exportado', 'total_importado', 'balanca_comercial'], 
        estado: int | None = None, 
        pais: int | None = None
    ) -> List[dict]:
        
        if crit not in ['total_exportado', 'total_importado', 'balanca_comercial']:
            error_logger.error("Parâmetro imválido para 'crit'. 'crit' deve ser um desses valores: ['total_exportado', 'total_importado', 'balanca_comercial']")
            return
        
        app_logger.info(f"Iniciando análise de tendências de balança comercial")
        df = pd.read_csv(f'{self.output_dir}/mv_balanca_comercial.csv')
        df = df.rename(columns={'SG_UF_NCM':'SG_UF'})
        df = df.merge(self.gd.gera_estados_df(), on="SG_UF", how="left")
        df = df.drop(columns=['NO_UF', 'NO_REGIAO', 'SG_UF'])
        print(df.columns)
        df['CO_ANO'] = df['CO_ANO'].astype(int)
        df['CO_MES'] = df['CO_MES'].astype(int)
        df['DATA'] = pd.to_datetime(df['CO_ANO'].astype(str) + '-' + df['CO_MES'].astype(str).str.zfill(2))

        if estado:
            df = df[df['CO_UF'] == estado]
        if pais:
            df = df[df['CO_PAIS'] == pais]

        df = df.groupby('DATA')[['total_exportado', 'total_importado', 'balanca_comercial']].sum().reset_index()
        df_prophet = df[['DATA', crit]].rename(columns={'DATA': 'ds', crit: 'y'})

        nome = crit
        if estado:
            nome += f"_{estado}"
        if pais:
            nome += f"_{pais}"

        self.gerar_profecia(df_prophet, nome, f"Previsão de {crit}", f"{crit} ($)")

