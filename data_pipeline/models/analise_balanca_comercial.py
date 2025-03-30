import pandas as pd
from tabulate import tabulate


class AnaliseBalancaComercial:
    def __init__(self, ano:int):
        self.ano = ano
        self.exp_df = pd.read_csv(f"./datasets/limpo/{ano}/EXP_{ano}.csv", delimiter=',', encoding='latin1')
        self.imp_df = pd.read_csv(f"./datasets/limpo/{ano}/IMP_{ano}.csv", delimiter=',', encoding='latin1')


    def busca_tabelas(self):
        base_url = f"./datasets/limpo/{self.ano}/"
        exp_url = base_url + f"EXP_{self.ano}.csv"
        imp_url = base_url + f"IMP_{self.ano}.csv"
        self.exp_df = pd.read_csv(exp_url, delimiter=',', encoding='latin1')
        self.imp_df = pd.read_csv(imp_url, delimiter=',', encoding='latin1')


    def calcula_balanca_comercial(self):
        if self.exp_df is None or self.imp_df is None:
            print("❌ Erro: Dados não carregados. Execute busca_tabelas() primeiro.")
            return None

        total_exportado = self.exp_df["VL_FOB"].sum()
        total_importado = self.imp_df["VL_FOB"].sum()
        saldo_balanca = total_exportado - total_importado
        relacao_exp_imp = total_exportado / total_importado if total_importado != 0 else float('inf')

        dados_balanca = [
            ["Ano", self.ano],
            ["Total Exportado (US$)", f"{total_exportado:,.2f}"],
            ["Total Importado (US$)", f"{total_importado:,.2f}"],
            ["Saldo Balança Comercial (US$)", f"{saldo_balanca:,.2f}"],
            ["Relação Exp/Imp", f"{relacao_exp_imp:.2f}"]
        ]

        print("\n📊 Resumo da Balança Comercial")
        print(tabulate(dados_balanca, tablefmt="grid"))