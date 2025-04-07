### GET `/ranking_ncm`

**Descrição:**
Esta rota permite buscar os NCMs (Nomenclatura Comum do Mercosul) mais exportados ou importados com base em critérios específicos, como ano, país, estado e via de transporte. Os resultados podem ser ordenados por kg liquido, valor FOB, valor agregado ou número de registros.

**Parâmetros da Requisição:**
A requisição aceita os seguintes parâmetros via query string:

| Parâmetro   | Tipo       | Obrigatório | Descrição |
|-------------|-----------|-------------|-------------|
| `tipo`      | `string`  | Sim         | Tipo de transação: `exp` para exportação ou `imp` para importação. |
| `qtd`       | `int`     | Não         | Quantidade de NCMs a serem retornados. Valor padrão: `10`. Deve ser um número inteiro positivo. |
| `anos`      | `list[int]` | Não       | Lista de anos a serem considerados. Valores permitidos: `2014-2024`. |
| `meses`     | `list[int]` | Não       | Lista de meses a serem considerados (1 a 12). |
| `paises`    | `list[int]` | Não       | Lista de identificadores de países a serem considerados. |
| `estados`   | `list[int]` | Não       | Lista de identificadores de estados brasileiros a serem considerados. |
| `vias`      | `list[int]` | Não       | Lista de identificadores de vias de transporte a serem consideradas. |
| `urfs`       | `list[int]` | Não       | Lista de identificadores de unidades da receita federal a serem consideradas.  |
| `crit`      | `string`  | Não         | Critério de ordenação. Valores permitidos: `kg_liquido`, `valor_fob`, `valor_agregado`, `registros`. Padrão: `valor_fob`. |
| `cresc`      | `int`  | Não         | Valores permitidos:`1`, `0`. Indica se a ordenação deve ser crescente ou decrescente. Se o valor for **1**, a lista é ordenada de forma crescente, ou seja, acessa os menos exportados ou importados. Se for **0**, a lista é ordenada de forma decrescente, ou seja, pega os mais exportados ou importados. Padrão: `0`  |


**Exemplo de Requisição:**
```
GET /ranking_ncm?tipo=exp&qtd=10&anos=2020&anos=2021&anos=2022&meses=1&meses=2&crit=valor_fob
```

**Respostas:**

- **200 OK** - Retorna os NCMs mais exportados ou importados conforme os filtros aplicados.
```json
{
  "resposta": [
    {
      "ncm": 12019000,
      "produto_descricao": "Soja, mesmo triturada, exceto para semeadura",
      "sh4_descricao": "Soja, mesmo triturada",
      "total_kg_liquido": "815159416854.00",
      "total_registros": 17540,
      "total_valor_agregado": "0.43",
      "total_valor_fob": "354153807896.00"
    },
    {
      "ncm": 27090010,
      "produto_descricao": "Óleos brutos de petróleo",
      "sh4_descricao": "Óleos brutos de petróleo ou de minerais betuminosos",
      "total_kg_liquido": "639101633867.00",
      "total_registros": 2772,
      "total_valor_agregado": "0.44",
      "total_valor_fob": "279482496698.00"
    }
  ]
}
```

**Notas:**
- Caso nenhum ano seja informado, a consulta considerará todos os anos disponíveis (2014-2024).
- A filtragem por países, estados e vias de transporte é opcional.
- O critério de ordenação padrão é `valor_fob`, mas pode ser alterado conforme necessário.

Essa rota é útil para análises de mercado e acompanhamento do fluxo de importação e exportação de produtos brasileiros.

---

## GET `/busca_por_ncm`
**Descrição:**
Esta rota permite buscar informações (kg liquido, valor FOB, valor agregado e número de registros) de exportação e importação por ncm de acordo com critérios específicos, como ano, país, estado e via de transporte.

**Parâmetros da Requisição:**
A requisição aceita os seguintes parâmetros via query string:

| Parâmetro   | Tipo       | Obrigatório | Descrição |
|-------------|-----------|-------------|-------------|
| `ncm`       | `list[int]` | Sim       | Lista de ncms a serem buscados. |
| `anos`      | `list[int]` | Não       | Lista de anos a serem considerados. Valores permitidos: `2014-2024`. |
| `meses`     | `list[int]` | Não       | Lista de meses a serem considerados (1 a 12). |
| `paises`    | `list[int]` | Não       | Lista de identificadores de países a serem considerados. |
| `estados`   | `list[int]` | Não       | Lista de identificadores de estados brasileiros a serem considerados. |
| `vias`      | `list[int]` | Não       | Lista de identificadores de vias de transporte a serem consideradas. |
| `urfs`       | `list[int]` | Não       | Lista de identificadores de unidades da receita federal a serem consideradas.  |

**Exemplo de Requisição:**
```
GET /busca_por_ncm?ncm=12019000&anos=2020&anos=2021&anos=2022&meses=1&meses=2
```

**Respostas:**

- **200 OK** - Retorna as informações sobre os ncm requisitados de arcordo com os critérios escolhidos.
```json
{
  "resposta": [
    {
      "produto_descricao": "Soja, mesmo triturada, exceto para semeadura",
      "sh4_descricao": "Soja, mesmo triturada",
      "total_kg_liquido_exp": "301588837680.00",
      "total_kg_liquido_imp": null,
      "total_valor_agregado_exp": "0.40",
      "total_valor_agregado_imp": null,
      "total_valor_fob_exp": "121798388937.00",
      "total_valor_fob_imp": null
    }
  ]
}
```
**Notas:**
- É possível acessar as informações de mais de um ncm. Nesse caso, os critérios se mantêm os mesmos para todos os ncm requisitados.

---

## GET `/busca_ncm_hist`

**Descrição:**
Esta rota permite buscar o histórico de dados de exportação ou importação para os ncm escolhidos discriminados por mês e ano.

**Parâmetros da Requisição:**
A requisição aceita os seguintes parâmetros via query string:

| Parâmetro   | Tipo       | Obrigatório | Descrição |
|-------------|-----------|-------------|-------------|
| `tipo`      | `string`  | Sim         | Tipo de transação: `exp` para exportação ou `imp` para importação. |
| `ncm`       | `list[int]` | Sim       | Lista de ncms a serem buscados. |
| `anos`      | `list[int]` | Não       | Lista de anos a serem considerados. Valores permitidos: `2014-2024`. |
| `meses`     | `list[int]` | Não       | Lista de meses a serem considerados (1 a 12). |
| `paises`    | `list[int]` | Não       | Lista de identificadores de países a serem considerados. |
| `estados`   | `list[int]` | Não       | Lista de identificadores de estados brasileiros a serem considerados. |
| `vias`      | `list[int]` | Não       | Lista de identificadores de vias de transporte a serem consideradas. |
| `urfs`       | `list[int]` | Não       | Lista de identificadores de unidades da receita federal a serem consideradas.  |

**Exemplo de Requisição:**
```
GET /busca_ncm_hist?ncm=12019000&anos=2014&meses=1&meses=2&meses=3&tipo=exp
```
**Respostas:**

- **200 OK** - Retorna os NCMs mais exportados ou importados conforme os filtros aplicados.
```json
{
  "resposta": [
    {
      "ano": 2014,
      "descricao": "Soja, mesmo triturada, exceto para semeadura",
      "id_ncm": 12019000,
      "mes": 1,
      "total_kg_liquido": "30583565.00",
      "total_registros": 13,
      "total_valor_agregado": "0.58",
      "total_valor_fob": "17787707.00"
    },
    {
      "ano": 2014,
      "descricao": "Soja, mesmo triturada, exceto para semeadura",
      "id_ncm": 12019000,
      "mes": 2,
      "total_kg_liquido": "2789537176.00",
      "total_registros": 78,
      "total_valor_agregado": "0.50",
      "total_valor_fob": "1385781145.00"
    },
    {
      "ano": 2014,
      "descricao": "Soja, mesmo triturada, exceto para semeadura",
      "id_ncm": 12019000,
      "mes": 3,
      "total_kg_liquido": "6226713306.00",
      "total_registros": 135,
      "total_valor_agregado": "0.51",
      "total_valor_fob": "3146413552.00"
    }
  ]
}
```

## GET `/pesquisa_ncm_por_nome`
**Descrição:**
Rota de pesquisa por nome do produto. 

**Parâmetros da Requisição:**
A requisição aceita os seguintes parâmetros via query string:
| Parâmetro   | Tipo       | Obrigatório | Descrição |
|-------------|-----------|-------------|-------------|
| `nome`      | `string`  | Não         | Termo da pesquisa. |

**Exemplo de Requisição:**
```
GET /pesquisa_ncm_por_nome?nome=ovos%frescos
```
**Respostas:**
- **200 OK** - Retorna id_ncm e descrição de todos os ncm que possuem `<nome>` em sua descrição.
```json
{
  "resposta": [
    {
      "descricao": "Ovos de outras aves, não para incubação ou não frescos",
      "id_ncm": 4079000
    },
    {
      "descricao": "Ovos frescos de outras aves",
      "id_ncm": 4072900
    },
    {
      "descricao": "Outros ovos de aves, com casca, frescos, conservados cozidos",
      "id_ncm": 4070090
    },
    {
      "descricao": "Outros ovos de aves, sem casca, frescos, cozidos em água, etc",
      "id_ncm": 4089900
    },
    {
      "descricao": "Outros ovos frescos de aves da espécie Gallus domesticus",
      "id_ncm": 4072100
    }
  ]
}
```
**Nota:**
Se o parâmetro 'nome' não for fornecido, a rota irá retornar todos os ncm em ordem crescente.