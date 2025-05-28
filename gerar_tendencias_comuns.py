import json
from typing import List, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from data_pipeline.models.vidente import Vidente


def salvar_json(data: List[dict], file_name: str):
    output_path = f"data_pipeline/datasets/tendencias/{file_name}.json"
    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


vidente = Vidente()
tarefas = [
    ("tendencia_balanca_comercial", vidente.tendencia_balanca_comercial, ()),
    ("tendencia_balanca_comercial_eSP", vidente.tendencia_balanca_comercial, ("SP", None)),
    ("tendencia_vlfob_exp", vidente.tendencia_vlfob, ("EXP",)),
    ("tendencia_vlfob_imp", vidente.tendencia_vlfob, ("IMP",)),
    ("tendencia_valor_agregado_exp", vidente.tendencia_valor_agregado, ("EXP",)),
    ("tendencia_valor_agregado_imp", vidente.tendencia_valor_agregado, ("IMP",)),
]

# Exemplos de uso:

# ("tendencia_vlfob_ncm_exp", vidente.tendencia_vlfob_ncm, ("EXP", "84198999.0")),
# ("tendencia_vlfob_ncm_imp", vidente.tendencia_vlfob_ncm, ("IMP", "84198999.0")),

# ("tendencia_vlfob_sh4_exp", vidente.tendencia_vlfob_sh4, ("EXP", "101")),
# ("tendencia_vlfob_sh4_imp", vidente.tendencia_vlfob_sh4, ("IMP", "101")),

# ("tendencia_vlfob_setores_exp", vidente.tendencia_vlfob_setores, ("EXP", "agronegocio")),
# ("tendencia_vlfob_setores_imp", vidente.tendencia_vlfob_setores, ("IMP", "agronegocio")),

# ("tendencia_ranking_ncm_exp", vidente.tendencia_ranking_ncm, ("EXP",)),
# ("tendencia_ranking_ncm_imp", vidente.tendencia_ranking_ncm, ("IMP",)),

# ("tendencia_ranking_sh4_exp", vidente.tendencia_ranking_sh4, ("EXP",)),
# ("tendencia_ranking_sh4_imp", vidente.tendencia_ranking_sh4, ("IMP",)),

# ("maiores_evolucoes_ncm_exp", lambda: vidente.maiores_evolucoes_ncm("EXP")["maiores_evolucoes_exp"], ()),
# ("maiores_reducoes_ncm_exp", lambda: vidente.maiores_evolucoes_ncm("EXP")["maiores_reducoes_exp"], ()),

# ("maiores_evolucoes_ncm_imp", lambda: vidente.maiores_evolucoes_ncm("IMP")["maiores_evolucoes_imp"], ()),
# ("maiores_reducoes_ncm_imp", lambda: vidente.maiores_evolucoes_ncm("IMP")["maiores_reducoes_imp"], ()),

# ("maiores_evolucoes_sh4_exp", lambda: vidente.maiores_evolucoes_sh4("EXP")["maiores_evolucoes_exp"], ()),
# ("maiores_reducoes_sh4_exp", lambda: vidente.maiores_evolucoes_sh4("EXP")["maiores_reducoes_exp"], ()),

# ("maiores_evolucoes_sh4_imp", lambda: vidente.maiores_evolucoes_sh4("IMP")["maiores_evolucoes_imp"], ()),
# ("maiores_reducoes_sh4_imp", lambda: vidente.maiores_evolucoes_sh4("IMP")["maiores_reducoes_imp"], ()),


def salvar_tendencias_sequencial():
    for nome, func, args in tarefas:
        try:
            print(f"[INFO] Executando: {nome}")
            resultado = func(*args)
            salvar_json(resultado, nome)
            print(f"[SUCESSO] Salvo: {nome}.json")
        except Exception as e:
            print(f"[ERRO] Falha em {nome}: {e}")


def salvar_tendencias_paralelo(max_threads=2):
    def gerar_e_salvar(func: Callable, nome: str, *args, **kwargs):
        df = func(*args, **kwargs)
        salvar_json(df, nome)

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = []
        for nome, func, args, *rest in tarefas:
            kwargs = rest[0] if rest else {}
            futures.append(executor.submit(gerar_e_salvar, func, nome, *args, **kwargs))

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"[ERRO] Falha ao executar uma das tarefas: {e}")


if __name__ == "__main__":
    salvar_tendencias_sequencial()
    