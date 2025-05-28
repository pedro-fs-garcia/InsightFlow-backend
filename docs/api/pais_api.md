## GET `/ranking_pais`
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
      "nome_pais": "China",
      "total_kg_liquido": "3626059174576.00",
      "total_registros": 203233,
      "total_valor_agregado": "0.20",
      "total_valor_fob": "721583440326.00"
    },
    {
      "id_pais": 249,
      "nome_pais": "Estados Unidos",
      "total_kg_liquido": "346568159631.00",
      "total_registros": 781777,
      "total_valor_agregado": "0.86",
      "total_valor_fob": "297699151306.00"
    }
  ]
}
```


### GET `/busca_pais_hist`
 **Descrição:**
Esta rota permite buscar informações (kg liquido, valor FOB, valor agregado e número de registros) de exportação e importação por país de acordo com critérios específicos, como ano, país, estado e via de transporte.

**Parâmetros da Requisição:**
A requisição aceita os seguintes parâmetros via query string:

| Parâmetro   | Tipo       | Obrigatório | Descrição |
|-------------|-----------|-------------|-------------|
| `tipo`      | `string`  | Sim         | Tipo de transação: `exp` para exportação ou `imp` para importação. |
| `paises`    | `list[int]` | Sim       | Países cujos históricos serão retornados. É possível buscar mais de um país. |
| `anos`      | `list[int]` | Não       | Lista de anos a serem considerados. Valores permitidos: `2014-2024`. |
| `meses`     | `list[int]` | Não       | Lista de meses a serem considerados (1 a 12). |
| `ncm`       | `list[int]` | Não       | Lista de ncms a serem considerados. |
| `estados`   | `list[int]` | Não       | Lista de identificadores de estados brasileiros a serem considerados. |
| `vias`      | `list[int]` | Não       | Lista de identificadores de vias de transporte a serem consideradas. |
| `urfs`      | `list[int]` | Não       | Lista de identificadores de unidades da receita federal a serem consideradas.  |

**Exemplo de Requisição:**
```
GET /busca_pais_hist?tipo=ex&anos=2014&meses=1&meses=2
```

**Respostas:**
- **200 OK** - Retorna o histórico dos países ordenados por ano e mês de acordo com os filtros aplicados.
```json
{
  "resposta": [
    {
      "ano": 2014,
      "id_pais": 43,
      "kg_liquido_total": "481565.00",
      "mes": 1,
      "nome_bloco": "América Central e Caribe",
      "nome_pais": "Antígua e Barbuda",
      "total_registros": 17,
      "valor_agregado_total": "1.27",
      "valor_fob_total": "613477.00"
    },
    {
      "ano": 2014,
      "id_pais": 43,
      "kg_liquido_total": "412141.00",
      "mes": 2,
      "nome_bloco": "América Central e Caribe",
      "nome_pais": "Antígua e Barbuda",
      "total_registros": 14,
      "valor_agregado_total": "0.89",
      "valor_fob_total": "368843.00"
    },
  ]
}
```

## GET `/pesquisa_pais_por_nome`
**Descrição:**
Rota de pesquisa por nome do país. 

**Parâmetros da Requisição:**
A requisição aceita os seguintes parâmetros via query string:
| Parâmetro   | Tipo       | Obrigatório | Descrição |
|-------------|-----------|-------------|-------------|
| `nome`      | `string`  | Não         | Termo da pesquisa. |

**Exemplo de Requisição:**
```
GET /pesquisa_pais_por_nome?nome=ind
```
**Respostas:**
- **200 OK** - Retorna id e nome de todos os países que possuem `<nome>` em seu nome.
```json
{
  "resposta": [
    {
      "id_pais": 365,
      "nome": "Indonésia"
    },
    {
      "id_pais": 361,
      "nome": "Índia"
    },
    {
      "id_pais": 782,
      "nome": "Território Britânico do Oceano Índico"
    }
  ]
}
```
**Nota:**
Se o parâmetro 'nome' não for fornecido, a rota irá retornar todos os países em ordem alfabética.