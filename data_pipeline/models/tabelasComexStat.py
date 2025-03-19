class TabelasComexStat:
    def __init__(self):
        self.link_base_ncm = "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/"
        self.link_base_mun = "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/mun/"
        self.link_base_aux = "https://balanca.economia.gov.br/balanca/bd/tabelas/"


    def exportacao_ncm(self, ano:str) -> str:
        '''
            Este método recebe o ano de interesse e retorna o link correspondente à tabela de exportação detalhada por NCM
        '''
        return f"{self.link_base_ncm}EXP_{ano}.csv"


    def importacao_ncm(self, ano:str) -> str:
        '''
            Este método recebe o ano de interesse e retorna o link correspondente à tabela de importação detalhada por NCM
        '''
        return f"{self.link_base_ncm}IMP_{ano}.csv"


    def exportacao_mun(self, ano:str) -> str:
        '''
            Este método recebe o ano de interesse e retorna o link correspondente à tabela de exportação detalhaa por município
        '''
        return f"{self.link_base_mun}EXP_{ano}_MUN.csv"


    def importacao_mun(self, ano:str) -> str:
        '''
            Este método recebe o ano de interesse e retorna o link correspondente à tabela de importação detalhada por município
        '''
        return f"{self.link_base_mun}IMP_{ano}_MUN.csv"


    def auxiliar(self, tabela) -> str:
        '''
            Esta função recebe o nome da tabela auxiliar
            e retorna o link correnspondente.

            Elas podem ser:
                NCM
                NCM_SH
                NCM_CUCI
                NCM_ISIC
                ISIC_CUCI
                NCM_CGCE
                NCM_FAT_AGREG
                NCM_PPE
                NCM_PPI
                NCM_UNIDADE
                PAIS
                PAIS_BLOCO
                UF_MUN
                UF
                VIA
                URF
        '''
        return f"{self.link_base_aux}{tabela}.csv"


# Base de dados detalhada por NCM
link_base_ncm = "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/"

EXP_2014 = link_base_ncm + "EXP_2014.csv"
EXP_2015 = link_base_ncm + "EXP_2015.csv"
EXP_2016 = link_base_ncm + "EXP_2016.csv"
EXP_2017 = link_base_ncm + "EXP_2017.csv"
EXP_2018 = link_base_ncm + "EXP_2018.csv"
EXP_2019 = link_base_ncm + "EXP_2019.csv"
EXP_2020 = link_base_ncm + "EXP_2020.csv"
EXP_2021 = link_base_ncm + "EXP_2021.csv"
EXP_2022 = link_base_ncm + "EXP_2022.csv"
EXP_2023 = link_base_ncm + "EXP_2023.csv"
EXP_2024 = link_base_ncm + "EXP_2024.csv"

IMP_2014 = link_base_ncm + "IMP_2014.csv"
IMP_2015 = link_base_ncm + "IMP_2015.csv"
IMP_2016 = link_base_ncm + "IMP_2016.csv"
IMP_2017 = link_base_ncm + "IMP_2017.csv"
IMP_2018 = link_base_ncm + "IMP_2018.csv"
IMP_2019 = link_base_ncm + "IMP_2019.csv"
IMP_2020 = link_base_ncm + "IMP_2020.csv"
IMP_2021 = link_base_ncm + "IMP_2021.csv"
IMP_2022 = link_base_ncm + "IMP_2022.csv"
IMP_2023 = link_base_ncm + "IMP_2023.csv"
IMP_2024 = link_base_ncm + "IMP_2024.csv"

# Base de dados detalhada por Município da empresa exportadora/importadora e posição no sistema harmonizado (SH4)
link_base_mun = "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/mun/"

EXP_2014_MUN = link_base_mun + "EXP_2014_MUN.csv"
EXP_2015_MUN = link_base_mun + "EXP_2015_MUN.csv"
EXP_2016_MUN = link_base_mun + "EXP_2016_MUN.csv"
EXP_2017_MUN = link_base_mun + "EXP_2017_MUN.csv"
EXP_2018_MUN = link_base_mun + "EXP_2018_MUN.csv"
EXP_2019_MUN = link_base_mun + "EXP_2019_MUN.csv"
EXP_2020_MUN = link_base_mun + "EXP_2020_MUN.csv"
EXP_2021_MUN = link_base_mun + "EXP_2021_MUN.csv"
EXP_2022_MUN = link_base_mun + "EXP_2022_MUN.csv"
EXP_2023_MUN = link_base_mun + "EXP_2023_MUN.csv"
EXP_2024_MUN = link_base_mun + "EXP_2024_MUN.csv"

IMP_2014_MUN = link_base_mun + "IMP_2014_MUN.csv"
IMP_2015_MUN = link_base_mun + "IMP_2015_MUN.csv"
IMP_2016_MUN = link_base_mun + "IMP_2016_MUN.csv"
IMP_2017_MUN = link_base_mun + "IMP_2017_MUN.csv"
IMP_2018_MUN = link_base_mun + "IMP_2018_MUN.csv"
IMP_2019_MUN = link_base_mun + "IMP_2019_MUN.csv"
IMP_2020_MUN = link_base_mun + "IMP_2020_MUN.csv"
IMP_2021_MUN = link_base_mun + "IMP_2021_MUN.csv"
IMP_2022_MUN = link_base_mun + "IMP_2022_MUN.csv"
IMP_2023_MUN = link_base_mun + "IMP_2023_MUN.csv"
IMP_2024_MUN = link_base_mun + "IMP_2024_MUN.csv"

#Tabelas de correlações de códigos e classificações
link_base_aux = "https://balanca.economia.gov.br/balanca/bd/tabelas/"

NCM = link_base_aux + "NCM.csv"
NCM_SH = link_base_aux + "NCM_SH.csv"
NCM_CUCI = link_base_aux + "NCM_CUCI.csv"
NCM_ISIC = link_base_aux + "NCM_ISIC.csv"
ISIC_CUCI = link_base_aux + "ISIC_CUCI.csv"
NCM_CGCE = link_base_aux + "NCM_CGCE.csv"
NCM_FAT_AGREG = link_base_aux + "NSM_FAT_AGREG.csv"
NCM_PPE = link_base_aux + "NCM_PPE.csv"
NCM_PPI = link_base_aux + "NCM_PPI.csv"
NCM_UNIDADE = link_base_aux + "NCM_UNIDADE.csv"
PAIS = link_base_aux + "PAIS.csv"
PAIS_BLOCO = link_base_aux + "PAIS_BLOCO.csv"
UF_MUN = link_base_aux + "UF_MUN.csv"
UF = link_base_aux + "UF.csv"
VIA = link_base_aux + "VIA.csv"
URF = link_base_aux + "URF.csv"


#exempolo de uso:
# tabelas = TabelasComexStat()
# exportacao_por_mun_2024 = tabelas.exportacao_mun('2024')
# exportacao_por_ncm_2024 = tabelas.exportacao_ncm('2024')
# ncm = tabelas.auxiliar('NCM')