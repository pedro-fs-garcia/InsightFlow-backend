# Limpeza e Filtragem de Dados do Comex Stat (2014-2024)

import pandas as pd

from models.tabelasComexStat import TabelasComexStat


class LimpadorDeTabela:
    def __init__(self):
        self.tabelas_cs = TabelasComexStat()
        self.ano:int
        self.tipo:str
        self.df_raw: pd.DataFrame
        self.df: pd.DataFrame
        self.nome_arquivo: pd.DataFrame
        self.estado_inicial:dict

        self.peso_zero: pd.DataFrame
        self.qt_estat_zero: pd.DataFrame
        self.sigla_nd:pd.DataFrame
        self.vl_fob_zero: pd.DataFrame
        self.va_nan_inf: pd.DataFrame
        self.co_via_invalida:pd.DataFrame
        self.rotas_absurdas:pd.DataFrame = []
        self.pais_invalido:pd.DataFrame

        self.estado_final:dict


    def gerar_dataframe(self, ano:int, tipo:str):
        '''
            - tipos suportados: 'exp', 'exp_mun', 'imp', 'imp_mun'
        '''
        tipo = tipo.lower()
        if tipo == 'exp':
            self.df_raw = pd.read_csv(self.tabelas_cs.exportacao_ncm(str(ano)), delimiter=';', encoding='latin1')
            self.nome_arquivo = f'EXP_{ano}'
            self.tipo = tipo
        elif tipo == 'imp':
            self.df_raw = pd.read_csv(self.tabelas_cs.importacao_ncm(str(ano)), delimiter=';', encoding='latin1')
            self.nome_arquivo = f'IMP_{ano}'
            self.tipo = tipo
        elif tipo == 'exp_mun':
            self.df_raw = pd.read_csv(self.tabelas_cs.exportacao_mun(str(ano)), delimiter=';', encoding='latin1')
            self.nome_arquivo = f'EXP_{ano}_MUN'
            self.tipo = tipo
        elif tipo == 'imp_mun':
            self.df_raw = pd.read_csv(self.tabelas_cs.importacao_mun(str(ano)), delimiter=';', encoding='latin1')
            self.nome_arquivo = f'IMP_{ano}_MUN'
            self.tipo = tipo
        self.df = self.df_raw
        self.estado_inicial = self.gerar_estado()
        self.ano = ano


    def gerar_estado(self) -> dict:
        estado = {}
        estado['linhas'] = len(self.df)
        return estado


    def criar_valor_agregado(self):
        # Criar coluna de valor agregado (VL_FOB por KG_LIQUIDO)
        self.df['VALOR_AGREGADO'] = self.df['VL_FOB'] / self.df['KG_LIQUIDO']


    def remover_peso_zero(self):
        self.peso_zero = self.df[self.df['KG_LIQUIDO'] <= 0]
        self.df = self.df[self.df['KG_LIQUIDO'] > 0]


    def remover_qt_zero(self):
        self.qt_estat_zero = self.df_raw[self.df_raw['QT_ESTAT'] <= 0]
        self.df = self.df[self.df['QT_ESTAT'] > 0]

    
    def remover_vl_fob_zero(self):
        self.vl_fob_zero = self.df_raw[self.df_raw['VL_FOB'] <= 0]
        self.df = self.df[self.df['VL_FOB'] > 0]
    

    def remover_sigla_nd(self):
        self.sigla_nd = self.df_raw[self.df_raw.isin(["ND"]).any(axis=1)]
        self.df = self.df[~self.df.isin(["ND"]).any(axis=1)].copy()


    # def remover_sigla_nd(self):
    #     if 'MUN' in self.nome_arquivo:
    #         self.sigla_nd = self.df_raw[self.df_raw['SG_UF_MUN'] == 'ND']
    #         self.df = self.df[self.df['SG_UF_MUN'] != 'ND'].copy()
    #     else:
    #         self.sigla_nd = self.df_raw[self.df_raw['SG_UF_NCM'] == 'ND']
    #         self.df = self.df[self.df['SG_UF_NCM'] != 'ND'].copy()


    def remover_va_inf_nan(self):
        self.va_nan_inf = self.df_raw['VALOR_AGREGADO'].isna().sum() | self.df_raw['VALOR_AGREGADO'].isin([float('inf'), float('-inf')])
        self.df = self.df.dropna(subset=['VALOR_AGREGADO'])
        self.df = self.df[~self.df['VALOR_AGREGADO'].isin([float('inf'), float('-inf')])]


    def remover_via_invalida(self):
        vias_validas = [1, 2, 3, 4, 5, 6, 7, 8, 13, 11, 15, 14]
        vias_invalidas = [0, 9, 10, 99, 12]
        self.co_via_invalida = self.df_raw[self.df_raw['CO_VIA'].isin(vias_invalidas)]
        self.df = self.df[self.df['CO_VIA'].isin(vias_validas)]


    def remover_pais_nao_definido(self):
        paises_invalidos = [0, 990, 994, 995, 997, 998, 999]
        self.pais_invalido = self.df_raw[self.df_raw['CO_PAIS'].isin(paises_invalidos)]
        self.df = self.df[~self.df['CO_PAIS'].isin(paises_invalidos)].copy()


    def remover_rotas_absurdas(self):
        paises_url = self.tabelas_cs.auxiliar('PAIS_BLOCO')
        pais_bloco = pd.read_csv(paises_url, delimiter=';', encoding='latin1')

        df_merged = self.df.merge(pais_bloco[['CO_PAIS', 'CO_BLOCO', 'NO_BLOCO']], on='CO_PAIS', how='left')

        '''
            51 - africa
            105 - am central e caribe
            107 - am do norte
            48 - am do sul
            39 - asia
            53 - sudeste asiatico
            112 - europa
            111 - mercosul
            61 - oceania
            41 - oriente medio
            22 - uniao europeia
        '''
        # Dicionário atualizado de compatibilidade entre vias de transporte e blocos econômicos
        vias_invalidas = {
            6: [51, 105, 107, 39, 53, 112, 61, 41, 22],  # Ferroviária
            7: [51, 105, 107, 39, 53, 112, 61, 41, 22],  # Rodoviária
            2: [51, 39, 53, 112, 61, 41, 22],  # Fluvial
            3: [51, 105, 107, 39, 53, 112, 61, 41, 22],  # Lacustre
            13: [51, 105, 107, 39, 53, 112, 61, 41, 22], # Reboque
            14: [51, 105, 107, 39, 53, 112, 61, 41, 22],  # Dutos: Oceania (não há dutos transoceânicos ligando a outros países)
            15: [51, 105, 107, 39, 53, 112, 61, 41, 22], # Vicinal fronteiriço
            8: [105, 107, 39, 53, 112, 61, 41, 22] # conduto/rede de transmissão
        }

        df_merged['via_invalida'] = df_merged.apply(
            lambda row: row['CO_BLOCO'] in vias_invalidas.get(row['CO_VIA'], []),
            axis=1
        )
        
        self.rotas_absurdas = df_merged[df_merged['via_invalida']].drop(columns=['via_invalida','CO_BLOCO','NO_BLOCO']).copy()

        # Filtrando os registros de df_maior que não estão em df_menor
        # diferenca_df = df_maior[~df_maior.isin(df_menor)].dropna()
        self.df = self.df[~self.df.isin(self.rotas_absurdas)].dropna()


    def gerar_relatorio(self):
        total_excluido = len(self.df_raw) + len(self.qt_estat_zero) + len(self.sigla_nd) + len(self.vl_fob_zero) + len(self.va_nan_inf) + len(self.co_via_invalida) + len(self.rotas_absurdas)
        linhas_invalidas = {
            'Quantidade de linhas iniciais': len(self.df_raw),
            'Quantidade Zero': len(self.qt_estat_zero),
            'siglas ND': len(self.sigla_nd),
            'VL_FOB zero': len(self.vl_fob_zero),
            'Valores Infinitos/NaN': len(self.va_nan_inf),
            'Vias inválidas': len(self.co_via_invalida),
            'Rotas absurdas': len(self.rotas_absurdas),
            'Países não definidos': len(self.pais_invalido),
            'Quantidade de linhas finais': len(self.df),
            'Total de linhas excluídas': len(self.df_raw) - len(self.df)
        }
        print(linhas_invalidas)
        relatorio = pd.DataFrame(list(linhas_invalidas.items()), columns=['Dado', 'Valor'])
        relatorio_path = f'data_pipeline/datasets/relatorios/{self.nome_arquivo}_rel.csv'
        relatorio.to_csv(relatorio_path, index=False, encoding='latin1')
        print(f"Relatório de limpeza salvo em: {relatorio_path}")


    def salvar_registros_excluidos(self):
        def salvar_tabela(df:pd.DataFrame, nome:str):
            path = f'data_pipeline/datasets/registros_excluidos/{self.tipo}_{self.ano}_{nome}.csv'
            df.to_csv(path, index=False, encoding='latin1')
            print(f'tabela {nome} salva em {path}')      
        mapa = {
            'qt_estat_zero': self.qt_estat_zero,
            'sigla_nd': self.sigla_nd,
            'vl_fob_zero':self.vl_fob_zero,
            'va_nan_inf': self.va_nan_inf,
            'via_invalida': self.co_via_invalida,
            'rotas_absurdas': self.rotas_absurdas,
            'pais_invalido': self.pais_invalido,
        }
        for key, value in mapa.items():
            salvar_tabela(value, key)


    def executar(self):        
        # Análise inicial dos dados
        print("Resumo dos dados:")
        print(self.df.info())
        print("\nEstatísticas descritivas:")
        print(self.df.describe())
        print("\nColunas")
        print(self.df.columns)

        self.criar_valor_agregado()
        self.remover_peso_zero()
        self.remover_qt_zero()
        self.remover_vl_fob_zero()
        self.remover_sigla_nd()
        self.remover_va_inf_nan()
        self.remover_via_invalida()
        self.remover_pais_nao_definido()
        self.remover_rotas_absurdas()

        self.gerar_relatorio()

        output_path = f'data_pipeline/datasets/limpo/{self.nome_arquivo}.csv'
        self.df.to_csv(output_path, index=False, encoding='latin1')

        print(f"Dados limpos salvos em: {output_path}")
        # print(self.df.describe())

        self.salvar_registros_excluidos()


# exemplo de uso:
# tratar = LimpadorDeTabela()
# tratar.gerar_dataframe(2014, 'exp')
# tratar.executar()
