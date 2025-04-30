from data_pipeline.models.pre_processamento import PreProcessador

if __name__ == "__main__":
    proc = PreProcessador()
    proc.salvar_dados_agregados()