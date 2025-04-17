
## GET `/pesquisa_sh4_por_nome`
**Descrição:**
Rota de pesquisa por nome do sh4. 
**Parâmetros da Requisição:**
A requisição aceita os seguintes parâmetros via query string:
| Parâmetro   | Tipo       | Obrigatório | Descrição |
|-------------|-----------|-------------|-------------|
| `nome`      | `string`  | Não         | Termo da pesquisa. |

**Exemplo de Requisição:**
```
GET /pesquisa_sh4_por_nome?nome=ovos%de%aves
```
**Respostas:**
- **200 OK** - Retorna id_sh4 e descrição de todos os sh4 que possuem `<nome>` em sua descrição.
```json
{
  "resposta": [
    {
      "descricao": "Ovos de aves, com casca, frescos, conservados ou cozidos",
      "id_sh4": "0407"
    },
    {
      "descricao": "Ovos de aves, sem casca, e gemas de ovos, frescos, secos, cozidos em água ou vapor, moldados, congelados ou conservados de outro modo, mesmo adicionados de açúcar ou de outros edulcorantes",
      "id_sh4": "0408"
    }
  ]
}
```
---

## 📍 GET `/busca_top_sh4_por_mun`

**Descrição**
Retorna os principais códigos SH4 (NCM de 4 dígitos) exportados ou importados por municípios, de acordo com os filtros fornecidos na requisição. Os resultados podem ser ordenados por valor FOB, peso líquido, valor agregado ou número de registros.


**Limite de Requisições**
- **10 requisições por minuto** por IP.


**Parâmetros (Query Params)**

| Parâmetro     | Tipo                   | Obrigatório | Descrição |
|---------------|------------------------|-------------|-----------|
| `tipo`        | `'exp'` ou `'imp'`     | Sim         | Define se a busca é por exportações (`exp`) ou importações (`imp`). |
| `qtd`         | `int`                  |    Não      | Quantidade de itens no ranking. Valor padrão: `10`. |
| `anos`        | `List[int]`            | Sim         | Um ou mais anos entre `2014` e `2024`. |
| `meses`       | `List[int]`            |    Não      | Um ou mais meses do ano (`1` a `12`). |
| `paises`      | `List[int]`            |    Não      | Códigos dos países relacionados à transação. |
| `municipios`  | `List[int]`            |    Não      | Códigos dos municípios envolvidos na operação. |
| `crit`        | `'kg_liquido'`, `'valor_fob'`, `'valor_agregado'`, `'registros'` |    Não | Critério de ordenação dos resultados. Valor padrão: `valor_fob`. |
| `cresc`      | `int`  | Não         | Valores permitidos:`1`, `0`. Indica se a ordenação deve ser crescente ou decrescente. Se o valor for **1**, a lista é ordenada de forma crescente, ou seja, acessa os menos exportados ou importados. Se for **0**, a lista é ordenada de forma decrescente, ou seja, pega os mais exportados ou importados. Padrão: `0`  |


**Exemplo de Requisição**
```
GET /busca_top_sh4_por_mun?tipo=exp&qtd=5&anos=2022&municipios=4314902&crit=valor_fob
```

**Respostas:**

- **200 OK** - Retorna os NCMs mais exportados ou importados conforme os filtros aplicados.
```json
{
  "resposta": [
    {
      "sh4": "1201",
      "sh4_descricao": "Soja, mesmo triturada",
      "total_kg_liquido": "825581260502.00",
      "total_registros": 46206,
      "total_valor_agregado": "0.43",
      "total_valor_fob": "358398026999.00"
    },
    {
      "sh4": "2709",
      "sh4_descricao": "Óleos brutos de petróleo ou de minerais betuminosos",
      "total_kg_liquido": "653590631307.00",
      "total_registros": 3042,
      "total_valor_agregado": "0.44",
      "total_valor_fob": "284639832475.00"
    }
  ]
}
```


## GET `/busca_vlfob_sh4`
**Descrição:**
Rota de busca de agregados de exportaçõ e importação por sh4. A rota devolve o total em valor FOB que foi importado e exportado de acordo com os códigos sh4 determinados. 
**Parâmetros da Requisição:**
A requisição aceita os seguintes parâmetros via query string:
| Parâmetro   | Tipo       | Obrigatório | Descrição |
|-------------|-----------|-------------|-------------|
| `sh4`       |`List[str]`| Sim         | Um ou mais códigos sh4 cujas informações serão buscadas|
| `anos`      |`List[int]`| Não         | Um ou mais anos entre `2014` e `2024`. |
|`estados`    |`List[int]`| Não         | Códigos dos estados que registringirão a busca|

**Exemplo de Requisição:**
```
GET /busca_vlfob_sh4?sh4=1201
```
**Respostas:**
- **200 OK** - Retorna o somatório do valor fob de exportação e importação para o conjunto de sh4 escolhidos para os estados escolhidos
```json
{
  "resposta": [
    {
      "total_valor_fob_exp": "354215692443.00",
      "total_valor_fob_imp": "1956696335.00"
    }
  ]
}
```


## GET `/busca_vlfob_setores`
**Descrição:**
Rota de busca de agregados de exportaçõ e importação por setores da economia (Agronegócio, Bens de Consumo, Indústria, Mineração, Setor Florestal e Tecnologia). A rota devolve o total em valor FOB que foi importado e exportado de cada setor. 
**Parâmetros da Requisição:**
A requisição aceita os seguintes parâmetros via query string:
| Parâmetro   | Tipo       | Obrigatório | Descrição |
|-------------|-----------|-------------|-------------|
| `anos`      |`List[int]`| Não         | Um ou mais anos entre `2014` e `2024`. |
|`estados`    |`List[int]`| Não         | Códigos dos estados que registringirão a busca|
| `paises`    |`List[int]`| Não         | Códigos dos países a serem considerados na busca|


**Exemplo de Requisição:**
```
GET /busca_vlfob_setores?anos=2024&anos=2023&estados=41&paises=43
```
**Respostas:**
- **200 OK** - Retorna o somatório do valor fob de exportação e importação de cada setor segundo os parâmetros escolhidos
```json
{
  "resposta": {
    "Agronegócio": {
      "total_valor_fob_exp": "1131093.00",
      "total_valor_fob_imp": "0"
    },
    "Bens de consumo": {
      "total_valor_fob_exp": "41674.00",
      "total_valor_fob_imp": "0"
    },
    "Indústria": {
      "total_valor_fob_exp": "121894.00",
      "total_valor_fob_imp": "1569.00"
    },
    "Mineração": {
      "total_valor_fob_exp": "70085.00",
      "total_valor_fob_imp": "107.00"
    },
    "Setor Florestal": {
      "total_valor_fob_exp": "14116.00",
      "total_valor_fob_imp": "0"
    },
    "Tecnologia": {
      "total_valor_fob_exp": "397387.00",
      "total_valor_fob_imp": "0"
    }
  }
}
```