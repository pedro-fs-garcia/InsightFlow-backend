# API REST - InsightFlow

API para consulta de informações sobre importação e exportação.

## URLs base:
 - Produção: `https://insightflow.com.br`
 - Desenvolvimento: `http://localhost:5000`

## Códigos de status:
```
200 OK - Requisição bem-sucedida

201 Created - Recurso criado

400 Bad Request - Erro na requisição

401 Unauthorized - Não autenticado

403 Forbidden - Sem permissão

404 Not Found - Recurso não encontrado

500 Internal Server Error - Erro no servidor
```

**Rate Limit:**
- 10 requisições por minuto

**Respostas:**

- **200 OK** - Retorna os dados requisitados em formato json conforme exemplos listados em suas respectivas rotas.


- **400 Bad Request** - Se a requisição contiver parâmetros inválidos.
```json
{
  "error": "Erro na requisição: [\"Ano inválido: 2025. Utilize um ano entre 2014 e 2024.\"]"
}
```

- **500 Internal Server Error** - Se houver falha ao recuperar os dados do banco.
```json
{
  "error": "Ocorreu um erro inesperado ao buscar informações no banco de dados"
}
```

## Rotas
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
---
### GET `/ranking_pais`
 **Descrição:**
 Esta rota permite rankear os países para os quais o Brasil mais exporta ou dos quais o Brasil mais importa com base em critários específicos, como ano, mes, ncm, estado, via e urf. Os resultados podem ser ordenados por kg liquido, valor FOB, valor agregado ou número de registros.

**Exemplo de Requisição:**
```
GET /ranking_pais?tipo=exp&qtd=10&anos=2020&anos=2021&anos=2022&meses=1&meses=2&crit=valor_fob
```

**Parâmetros da Requisição:**
A requisição aceita os seguintes parâmetros via query string:

| Parâmetro   | Tipo       | Obrigatório | Descrição |
|-------------|-----------|-------------|-------------|
| `tipo`      | `string`  | Sim         | Tipo de transação: `exp` para exportação ou `imp` para importação. |
| `qtd`       | `int`     | Não         | Quantidade de NCMs a serem retornados. Valor padrão: `10`. Deve ser um número inteiro positivo. |
| `anos`      | `list[int]` | Não       | Lista de anos a serem considerados. Valores permitidos: `2014-2024`. |
| `meses`     | `list[int]` | Não       | Lista de meses a serem considerados (1 a 12). |
| `ncm`       | `list[int]` | Não       | Lista de ncms a serem considerados. |
| `estados`   | `list[int]` | Não       | Lista de identificadores de estados brasileiros a serem considerados. |
| `vias`      | `list[int]` | Não       | Lista de identificadores de vias de transporte a serem consideradas. |
| `urfs`      | `list[int]` | Não       | Lista de identificadores de unidades da receita federal a serem consideradas.  |
| `crit`      | `string`  | Não         | Critério de ordenação. Valores permitidos: `kg_liquido`, `valor_fob`, `valor_agregado`, `registros`. Padrão: `valor_fob`. |
| `cresc`      | `int`  | Não         | Valores permitidos:`1`, `0`. Indica se a ordenação deve ser crescente ou decrescente. Se o valor for **1**, a lista é ordenada de forma crescente, ou seja, acessa os países de menos exportadores ou importadores. Se for **0**, a lista é ordenada de forma decrescente, ou seja, pega os países mains exportadores ou importadores. Padrão: `0`  |

**Respostas:**
- **200 OK** - Retorna os países mais ou menos importadores ou exportadores de acordo com os filtros aplicados.
```json
{
  "resposta": [
    {
      "id_pais": 160,
      "pais_nome": "China",
      "total_kg_liquido": "3626059174576.00",
      "total_registros": 203233,
      "total_valor_agregado": "0.20",
      "total_valor_fob": "721583440326.00"
    },
    {
      "id_pais": 249,
      "pais_nome": "Estados Unidos",
      "total_kg_liquido": "346568159631.00",
      "total_registros": 781777,
      "total_valor_agregado": "0.86",
      "total_valor_fob": "297699151306.00"
    }
  ]
}
```