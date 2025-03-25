import pandas as pd
from tabulate import tabulate

from .tabelasComexStat import TabelasComexStat

class AnaliseDeTabela:
    def __init__(self, tabela_url):
        self.df = pd.read_csv(tabela_url, delimiter=',', encoding='latin1')
        self.tabelas = TabelasComexStat()
        return
    
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
        print("\nProdutos de maior Valor Agregado")
        print(tabulate(top_10_ncm_lista, headers=["NCM", "Valor Agregado(vl_fob/kg_liquido)"], tablefmt="grid", floatfmt=".2f"))
    

    def ncm_por_fob(self):
        top_10_ncm = self.df.groupby("CO_NCM")["VL_FOB"].sum().nlargest(10).reset_index()
        auxiliar_ncm = self.tabelas.auxiliar('NCM')
        df_ncm = pd.read_csv(auxiliar_ncm, delimiter=';', encoding='latin1')
        top_10_ncm = top_10_ncm.merge(df_ncm, on="CO_NCM", how="left")
        top_10_ncm = top_10_ncm[["NO_NCM_POR", "VL_FOB"]]
        top_10_ncm_lista = top_10_ncm.values.tolist()
        print("\nProdutos de maior Valor FOB")
        print(tabulate(top_10_ncm_lista, headers=["NCM", "Valor FOB"], tablefmt="grid", floatfmt=".2f"))
    

    def ncm_por_kg(self):
        top_10_ncm = self.df.groupby("CO_NCM")["KG_LIQUIDO"].sum().nlargest(10).reset_index()
        auxiliar_ncm = self.tabelas.auxiliar('NCM')
        df_ncm = pd.read_csv(auxiliar_ncm, delimiter=';', encoding='latin1')
        top_10_ncm = top_10_ncm.merge(df_ncm, on="CO_NCM", how="left")
        top_10_ncm = top_10_ncm[["NO_NCM_POR", "KG_LIQUIDO"]]
        top_10_ncm_lista = top_10_ncm.values.tolist()
        print("\nProdutos de maior KG Liquido")
        print(tabulate(top_10_ncm_lista, headers=["NCM", "KG Liquido"], tablefmt="grid", floatfmt=".2f"))


    def analisar_exportacoes(self):
        total_fob = self.df['VL_FOB'].sum()
        total_peso = self.df['KG_LIQUIDO'].sum()
        total_transacoes = len(self.df)
        top_10_paises = self.df['CO_PAIS'].value_counts().head(10)
        top_estados = self.df['SG_UF_NCM'].value_counts()
        
        resultados = {
            'Total Transações': total_transacoes,
            'Total FOB': total_fob,
            'Total Peso Líquido': total_peso,
            'Top 10 Países': top_10_paises,
            'Top Estados': top_estados
        }

        for chave, valor in resultados.items():
            print(f"\n{chave}:")
            print(valor)
        
        self.ncm_por_va()
        self.ncm_por_fob()
        self.ncm_por_kg()

        return resultados
    
# Exemplo de uso:
# at = AnaliseDeTabela('datasets/limpo/2014/EXP_2014_MUN.csv')
# at.analisar_exportacoes()