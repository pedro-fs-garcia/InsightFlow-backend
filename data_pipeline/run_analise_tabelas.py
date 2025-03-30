from models.analise_balanca_comercial import AnaliseBalancaComercial
from models.analise_de_tabela import AnaliseDeTabela


def start():
    ano = 2014
    bal_com = AnaliseBalancaComercial(ano)
    bal_com.calcula_balanca_comercial()

    at = AnaliseDeTabela(ano, "exp", False)
    at.analisar_tabela()


if __name__ == '__main__':
    start()