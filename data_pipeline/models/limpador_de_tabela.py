import os
import pandas as pd
import matplotlib.pyplot as plt
from models.tabelasComexStat import TabelasComexStat


class LimpadorDeTabela:
    def __init__(self):
        self.tabelas_cs = TabelasComexStat()
        self.ano:int
        self.tipo:str
        self.df_raw: pd.DataFrame
        self.df: pd.DataFrame
        self.nome_arquivo: str
        self.peso_zero: pd.DataFrame = pd.DataFrame({})
        self.qt_estat_zero: pd.DataFrame = pd.DataFrame({})
        self.sigla_nd:pd.DataFrame = pd.DataFrame({})
        self.vl_fob_zero: pd.DataFrame = pd.DataFrame({})
        self.va_nan_inf: pd.DataFrame = pd.DataFrame({})
        self.co_via_invalida:pd.DataFrame = pd.DataFrame({})
        self.rotas_absurdas:pd.DataFrame = pd.DataFrame({})
        self.pais_invalido:pd.DataFrame = pd.DataFrame({})
        self.municipio_invalido:pd.DataFrame = pd.DataFrame({})
        self.estado_invalido:pd.DataFrame = pd.DataFrame({})
        self.urf_invalido:pd.DataFrame = pd.DataFrame({})


    def gerar_dataframe(self, ano:int, tipo:str):
        '''
            - tipos suportados: 'exp', 'exp_mun', 'imp', 'imp_mun'
        '''
        tipo = tipo.lower()
        self.ano = ano
        if tipo == 'exp':
            url = self.tabelas_cs.exportacao_ncm(str(ano))
            self.nome_arquivo = f'EXP_{ano}'
            self.tipo = tipo
        elif tipo == 'imp':
            url = self.tabelas_cs.importacao_ncm(str(ano))
            self.nome_arquivo = f'IMP_{ano}'
            self.tipo = tipo
        elif tipo == 'exp_mun':
            url = self.tabelas_cs.exportacao_mun(str(ano))
            self.nome_arquivo = f'EXP_{ano}_MUN'
            self.tipo = tipo
        elif tipo == 'imp_mun':
            url = self.tabelas_cs.importacao_mun(str(ano))
            self.nome_arquivo = f'IMP_{ano}_MUN'
            self.tipo = tipo
        
        print(f'Buscando tabela {self.nome_arquivo}.csv')

        if os.path.exists(f'datasets/limpo/{self.ano}/{self.nome_arquivo}.csv'):
            return False
        
        self.df_raw = pd.read_csv(url, delimiter=';', encoding='latin1')
        self.df = self.df_raw
        return True


    def criar_valor_agregado(self):
        # Criar coluna de valor agregado (VL_FOB por KG_LIQUIDO)
        self.df_raw['VALOR_AGREGADO'] = self.df_raw['VL_FOB'] / self.df_raw['KG_LIQUIDO']
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
        self.va_nan_inf = self.df_raw[self.df_raw['VALOR_AGREGADO'].isna() | self.df_raw['VALOR_AGREGADO'].isin([float('inf'), float('-inf')])]
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
    

    def remover_municipio_nao_definido(self):
        municipios_invalidos = [9999999]
        self.municipio_invalido = self.df_raw[self.df_raw['CO_MUN'].isin(municipios_invalidos)]
        self.df = self.df[~self.df['CO_MUN'].isin(municipios_invalidos)].copy()

    
    def remover_urf_nao_definido(self):
        urf_invalidos = [0, 9999999, 8110000, 1010109, 815400]
        self.urf_invalido = self.df_raw[self.df_raw['CO_URF'].isin(urf_invalidos)]
        self.df = self.df[~self.df['CO_URF'].isin(urf_invalidos)].copy()
    
    def remover_estado_nao_definido(self):
        estados_invalidos = ['EX', 'CB', 'MN', 'RE', 'ED', 'ND', 'ZN']
        self.estado_invalido = self.df_raw[self.df_raw['SG_UF_NCM'].isin(estados_invalidos)]
        self.df = self.df[~self.df['SG_UF_NCM'].isin(estados_invalidos)].copy()

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


    def gerar_grafico_vias_invalidas(self):
        if not 'CO_VIA' in self.df.columns or len(self.co_via_invalida) <= 0:
            return
        rotas_url = self.tabelas_cs.auxiliar('VIA')
        rotas = pd.read_csv(rotas_url, delimiter=';', encoding='latin1')
        df_merged = self.co_via_invalida.merge(rotas[['CO_VIA', 'NO_VIA']], on='CO_VIA', how='left')
        contagem_por_via = df_merged.groupby('NO_VIA').size().reset_index(name='Quantidade')

        plt.figure(figsize=(10, 6))
        plt.bar(contagem_por_via['NO_VIA'], contagem_por_via['Quantidade'], color='skyblue')

        plt.xlabel('Nome da via')
        plt.ylabel('Quantidade de Registros')
        plt.title(f'Quantidade de Registros por via {self.nome_arquivo}')

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()


    def gerar_grafico_paises_invalidos(self):
        if not 'CO_PAIS' in self.df.columns or len(self.pais_invalido) <= 0:
            return
        paises_url = self.tabelas_cs.auxiliar('PAIS')
        paises = pd.read_csv(paises_url, delimiter=';', encoding='latin1')
        df_merged = self.pais_invalido.merge(paises[['CO_PAIS', 'NO_PAIS']], on='CO_PAIS', how='left')
        contagem_por_pais = df_merged.groupby('NO_PAIS').size().reset_index(name='Quantidade')
        plt.figure(figsize=(10, 6))
        plt.bar(contagem_por_pais['NO_PAIS'], contagem_por_pais['Quantidade'], color='skyblue')

        plt.xlabel('Nome do país')
        plt.ylabel('Quantidade de Registros')
        plt.title(f'Quantidade de Registros por país inválido {self.nome_arquivo}')

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()


    def gerar_grafico_estados_invalidos(self):
        if not 'SG_UF_NCM' in self.df.columns or len(self.estado_invalido) <= 0:
            return
        estados_url = self.tabelas_cs.auxiliar('UF')
        estados = pd.read_csv(estados_url, delimiter=';', encoding='latin1')
        df_merged = self.estado_invalido.merge(estados[['SG_UF', 'NO_UF']], left_on='SG_UF_NCM', right_on='SG_UF', how='left')
        contagem_por_estado = df_merged.groupby('SG_UF_NCM').size().reset_index(name='Quantidade')
        plt.figure(figsize=(10, 6))
        plt.bar(contagem_por_estado['SG_UF_NCM'], contagem_por_estado['Quantidade'], color='skyblue')

        plt.xlabel('Nome do estado')
        plt.ylabel('Quantidade de Registros')
        plt.title(f'Quantidade de Registros por estado inválido {self.nome_arquivo}')

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()


    def gerar_relatorio_registros_excluidos(self):
        len_df_raw = len(self.df_raw)
        len_df = len(self.df)
        linhas_invalidas = {
            'Quantidade de linhas iniciais': len_df_raw,
            'Registros inválidos por KG Líquido = 0': len(getattr(self, 'peso_zero', [])),
            'Registros inválidos por Quantidade Estatística = 0': len(getattr(self, 'qt_estat_zero', [])),
            'Registros inválidos por Siglas ND': len(getattr(self, 'sigla_nd', [])),
            'Registros inválidos por Valor FOB = 0': len(getattr(self, 'vl_fob_zero', [])),
            'Registros inválidos por Valores Infinitos/NaN': len(getattr(self, 'va_nan_inf', [])),
            'Registros inválidos por Vias de transporte inválidas': len(getattr(self, 'co_via_invalida', [])),
            'Registros inválidos por Rotas absurdas': len(getattr(self, 'rotas_absurdas', [])),
            'Registros inválidos por Países não definidos': len(getattr(self, 'pais_invalido', [])),
            'Registros inválidos por Estados não definidos': len(getattr(self, 'estado_invalido', [])),
            'Registros inválidos por Município não declarado': len(getattr(self, 'municipio_invalido', [])),
            'Registros inválidos por URF não informada': len(getattr(self, 'urf_invalido', [])),
            'Quantidade de linhas finais': len_df,
            'Total de linhas excluídas': len_df_raw - len_df
        }
        print(f"\n📊 Estatísticas dos Dados Brutos (Ano: {self.ano})")
        print(self.df_raw.describe())
        print(f"\n📊 Estatísticas dos Dados Limpos (Ano: {self.ano})")
        print(self.df.describe())
        
        from tabulate import tabulate
        print("\n📌 Resumo das Linhas Excluídas:\n")
        tabela_remocoes = [[key, value] for key, value in linhas_invalidas.items()]
        print(tabulate(tabela_remocoes, headers=["Critério", "Quantidade"], tablefmt="grid"))
        
        relatorio = pd.DataFrame(list(linhas_invalidas.items()), columns=['Critério', 'Quantidade'])

        output_dir = f'datasets/relatorios/{self.ano}'
        os.makedirs(output_dir, exist_ok=True)
        relatorio_path = f'{output_dir}/{self.nome_arquivo}_rel.csv'
        relatorio.to_csv(relatorio_path, index=False, encoding='latin1')
        print(f"\n✅ Relatório de limpeza salvo em: {relatorio_path}")

        self.gerar_grafico_vias_invalidas()
        self.gerar_grafico_paises_invalidos()
        self.gerar_grafico_estados_invalidos()


    def salvar_registros_excluidos(self):
        def salvar_tabela(df:pd.DataFrame, nome:str):
            try:
                output_dir = f'datasets/registros_excluidos/{self.ano}'
                os.makedirs(output_dir, exist_ok=True)
                path = f'{output_dir}/{self.tipo}_{self.ano}_{nome}.csv'
                df.to_csv(path, index=False, encoding='latin1')
                print(f'tabela {nome} salva em {path}')
            except AttributeError as e:
                print(e.name)
                pass
        mapa = {
            'qt_estat_zero': self.qt_estat_zero,
            'sigla_nd': self.sigla_nd,
            'vl_fob_zero':self.vl_fob_zero,
            'va_nan_inf': self.va_nan_inf,
            'via_invalida': self.co_via_invalida,
            'rotas_absurdas': self.rotas_absurdas,
            'pais_invalido': self.pais_invalido,
            'estado_invalido': self.estado_invalido,
            'municipio_invalido': self.municipio_invalido,
            'urf_invalido': self.urf_invalido
        }
        for key, value in mapa.items():
            salvar_tabela(value, key)


    def salvar_tabela_limpa(self):
        output_dir = f'datasets/limpo/{self.ano}'
        os.makedirs(output_dir, exist_ok=True)
        output_path = f'{output_dir}/{self.nome_arquivo}.csv'
        self.df.to_csv(output_path, index=False, encoding='latin1')
        print(f"Dados limpos salvos em: {output_path}")


    def limpar(self):
        colunas = self.df.columns
        print(f'Iniciando limpeza da tabela {self.nome_arquivo}')
        self.criar_valor_agregado()
        self.remover_peso_zero()
        if 'QT_ESTAT' in colunas: self.remover_qt_zero() 
        self.remover_vl_fob_zero()
        self.remover_sigla_nd()
        self.remover_va_inf_nan()
        if 'CO_VIA' in colunas: 
            self.remover_via_invalida()
            self.remover_rotas_absurdas()
        self.remover_pais_nao_definido()
        if 'CO_MUN' in colunas: self.remover_municipio_nao_definido()
        if 'SG_UF_NCM' in colunas: self.remover_estado_nao_definido()
        if 'CO_URF' in colunas: self.remover_urf_nao_definido()
        

    def limpar_e_salvar_tabelas(self):
        self.limpar()
        self.salvar_tabela_limpa()
        self.salvar_registros_excluidos()
        self.gerar_relatorio_registros_excluidos()


# exemplo de uso:
# tratar = LimpadorDeTabela()
# tratar.gerar_dataframe(2014, 'exp')
# tratar.executar()
