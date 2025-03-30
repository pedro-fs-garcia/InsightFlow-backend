from typing import Literal
import pandas as pd
from tabulate import tabulate
import matplotlib.pyplot as plt

from .tabelasComexStat import TabelasComexStat

class AnaliseDeTabela:
    def __init__(self, ano:int, tipo:Literal["exp", "imp"], mun:bool):
        self.ano = ano
        self.tipo = tipo
        self.mun = mun
        self.tabelas = TabelasComexStat()
        tabela_url = self.gera_tabela_url()
        self.df = pd.read_csv(tabela_url, delimiter=',', encoding='latin1')
    

    def gera_tabela_url(self):
        nome_arquivo = f"{self.tipo.upper()}_{self.ano}"
        if self.mun:
            nome_arquivo += f"_MUN"
        tabela_url = f"./datasets/limpo/{self.ano}/{nome_arquivo}.csv"
        return tabela_url

    
    def geral(self):
        total_fob = self.df['VL_FOB'].sum()
        total_peso = self.df['KG_LIQUIDO'].sum()
        total_transacoes = len(self.df)
        total_va = total_fob/total_peso
        resultados = {
            'Total de Transações': total_transacoes,
            'Valor FOB Total': total_fob,
            'Peso Líquido Total': total_peso,
            'Valor Agregado total' : total_va
        }
        print(f"\n📌 Dados gerais da tabela de {self.tipo}ortação do ano de {self.ano}:")
        print(tabulate(resultados.items(), headers=["info", "valor"], tablefmt="grid", floatfmt=",.2f"))


    def ncm_por_va(self):
        top_10_ncm = (
            self.df.groupby("CO_NCM")
            .apply(lambda x: x["VL_FOB"].sum() / x["KG_LIQUIDO"].sum() if x["KG_LIQUIDO"].sum() != 0 else 0)
            .nlargest(10)
            .reset_index(name="VALOR_AGREGADO")
        )
        auxiliar_ncm = self.tabelas.auxiliar('NCM')
        df_ncm = pd.read_csv(auxiliar_ncm, delimiter=';', encoding='latin1')
        top_10_ncm = top_10_ncm.merge(df_ncm, on="CO_NCM", how="left")
        top_10_ncm = top_10_ncm[["NO_NCM_POR", "VALOR_AGREGADO"]]
        top_10_ncm_lista = top_10_ncm.values.tolist()
        print("\n📌 Produtos de maior Valor Agregado")
        print(tabulate(top_10_ncm_lista, headers=["NCM", "Valor Agregado(vl_fob/kg_liquido)"], tablefmt="grid", floatfmt=",.2f"))
    

    def ncm_por_fob(self):
        top_10_ncm = self.df.groupby("CO_NCM")["VL_FOB"].sum().nlargest(10).reset_index()
        auxiliar_ncm = self.tabelas.auxiliar('NCM')
        df_ncm = pd.read_csv(auxiliar_ncm, delimiter=';', encoding='latin1')
        top_10_ncm = top_10_ncm.merge(df_ncm, on="CO_NCM", how="left")
        top_10_ncm = top_10_ncm[["NO_NCM_POR", "VL_FOB"]]
        top_10_ncm["VL_FOB"] = top_10_ncm["VL_FOB"].apply(lambda x: f"{x:,.2f}")
        top_10_ncm_lista = top_10_ncm.values.tolist()
        print("\n📌 Produtos de maior Valor FOB")
        print(tabulate(top_10_ncm_lista, headers=["NCM", "Valor FOB"], tablefmt="grid"))
    

    def ncm_por_kg(self):
        top_10_ncm = self.df.groupby("CO_NCM")["KG_LIQUIDO"].sum().nlargest(10).reset_index()
        auxiliar_ncm = self.tabelas.auxiliar('NCM')
        df_ncm = pd.read_csv(auxiliar_ncm, delimiter=';', encoding='latin1')
        top_10_ncm = top_10_ncm.merge(df_ncm, on="CO_NCM", how="left")
        top_10_ncm = top_10_ncm[["NO_NCM_POR", "KG_LIQUIDO"]]
        top_10_ncm["KG_LIQUIDO"] = top_10_ncm["KG_LIQUIDO"].apply(lambda x: f"{x:,.2f}")
        top_10_ncm_lista = top_10_ncm.values.tolist()
        print("\n📌 Produtos de maior KG Liquido")
        print(tabulate(top_10_ncm_lista, headers=["NCM", "KG Liquido"], tablefmt="grid", floatfmt=",.2f"))

    
    def top_10_paises(self):
        top_10 = self.df['CO_PAIS'].value_counts().head(10).reset_index()
        auxiliar_pais = self.tabelas.auxiliar('PAIS')
        df_pais = pd.read_csv(auxiliar_pais, delimiter=';', encoding='latin1')
        top_10 = top_10.merge(df_pais, on="CO_PAIS", how="left")
        top_10 = top_10[["NO_PAIS", "count"]]
        top_10["count"] = top_10["count"].apply(lambda x: f"{x:,.2f}")
        top_10.columns = ['Nome do País', 'Quantidade de Registros']
        print("\n📌 Top 10 Países com Mais Registros:")
        print(tabulate(top_10.values.tolist(), headers=['Nome do País', 'Quantidade de registros'], tablefmt="grid", floatfmt=",.2f"))

        # Somar o valor agregado por país
        pais_destino = self.df.groupby(['CO_PAIS'])[['VL_FOB', 'KG_LIQUIDO']].mean().reset_index()
        pais_destino['VALOR_AGREGADO'] = pais_destino['VL_FOB'] / pais_destino['KG_LIQUIDO']
        pais_destino_ranked = pais_destino.sort_values(by='VALOR_AGREGADO', ascending=False)
        top_10_paises = pais_destino_ranked.head(10)
        top_10_paises = top_10_paises.merge(df_pais[['CO_PAIS', 'NO_PAIS']], on='CO_PAIS', how='left')
        resultado = top_10_paises[['NO_PAIS', 'VALOR_AGREGADO']]
        print("\n📌 Top 10 países por valor agregado total (Valor FOB total / KG líquido total):")
        print(tabulate(resultado, headers=["País", "Valor Agregado Total"], tablefmt="grid", floatfmt=",.2f"))
    
    
    def top_estados(self):
        top_estados = self.df['SG_UF_NCM'].value_counts().reset_index()
        top_estados.columns = ['SG_UF_NCM', 'Quantidade de Registros']

        estado_destino = self.df.groupby('SG_UF_NCM')[['VL_FOB', 'KG_LIQUIDO']].sum().reset_index()
        estado_destino['VALOR_AGREGADO'] = estado_destino['VL_FOB'] / estado_destino['KG_LIQUIDO']

        estados_completos = top_estados.merge(estado_destino[['SG_UF_NCM', 'VALOR_AGREGADO']], on='SG_UF_NCM', how='left')
        estados_completos = estados_completos.sort_values(by='VALOR_AGREGADO', ascending=False)

        estados_completos["Quantidade de Registros"] = estados_completos["Quantidade de Registros"].apply(lambda x: f"{x:,}")
        estados_completos["VALOR_AGREGADO"] = estados_completos["VALOR_AGREGADO"].apply(lambda x: f"{x:,.2f}")
        print("\n📌 Ranking de estados por quantidade de registros e valor agregado total:")
        print(tabulate(estados_completos.values.tolist(), headers=['Estado', 'Quantidade de Registros', 'Valor Agregado Total'], tablefmt="grid"))
    

    def top_vias(self):
        top_vias = self.df['CO_VIA'].value_counts().head(10).reset_index()
        auxiliar_vias = self.tabelas.auxiliar("VIA")
        df_via = pd.read_csv(auxiliar_vias, delimiter=";", encoding="latin1")
        top_vias = top_vias.merge(df_via, on="CO_VIA", how="left")
        top_vias = top_vias[["NO_VIA", "count"]]
        top_vias["count"] = top_vias["count"].apply(lambda x: f"{x:,.2f}")
        top_vias.columns = ["Via", "Quantidade de registros"]
        print("\n📌 Top 10 vias mais utilizadas:")
        print(tabulate(top_vias.values.tolist(), headers=['Via', 'Quantidade de registros'], tablefmt="grid", floatfmt=",.2f"))


    def analisar_tabela(self):
        self.geral()
        self.top_10_paises()
        self.top_estados()
        self.ncm_por_va()
        self.ncm_por_fob()
        self.ncm_por_kg()
        self.top_vias()
    

# Exemplo de uso:
# at = AnaliseDeTabela(2014, "exp", False)
# at.analisar_tabela()