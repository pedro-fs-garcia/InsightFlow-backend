from models.limpador_de_tabela import LimpadorDeTabela

# limpa_comex_stat.dataframe
def executar_limpador_ano(ano:int):
    tipos = ['exp', 'imp', 'exp_mun', 'imp_mun']
    limpador = LimpadorDeTabela()
    for tipo in tipos:
        limpador.gerar_dataframe(ano, tipo)
        limpador.executar()

for ano in range(2014, 2016):
    executar_limpador_ano(ano)