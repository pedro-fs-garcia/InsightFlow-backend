## GET `/ranking_bloco`

**Descrição:**
 Esta rota permite rankear os blocos econômicos para os quais o Brasil mais exporta ou dos quais o Brasil mais importa com base em critários específicos, como ano, mes, ncm, estado, via e urf. Os resultados podem ser ordenados por kg liquido, valor FOB, valor agregado ou número de registros.

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

**Exemplo de Requisição:**
**Exemplo de Requisição:**
```
GET /ranking_bloco?tipo=exp&qtd=3&anos=2014&meses=1&meses=2&crit=valor_fob
```
**Respostas:**
- **200 OK** - Retorna os países mais ou menos importadores ou exportadores de acordo com os filtros aplicados.
```json
{
  "resposta": [
    {
      "id_bloco": 39,
      "nome_bloco": "Ásia (Exclusive Oriente Médio)",
      "total_kg_liquido": "40998597025.00",
      "total_registros": 6924,
      "total_valor_agregado": "0.20",
      "total_valor_fob": "8276145228.00"
    },
    {
      "id_bloco": 22,
      "nome_bloco": "União Europeia - UE",
      "total_kg_liquido": "10717991571.00",
      "total_registros": 12953,
      "total_valor_agregado": "0.44",
      "total_valor_fob": "4699343583.00"
    },
    {
      "id_bloco": 107,
      "nome_bloco": "América do Norte",
      "total_kg_liquido": "5319780865.00",
      "total_registros": 12035,
      "total_valor_agregado": "0.80",
      "total_valor_fob": "4232807305.00"
    }
  ]
}
```

---

## GET `/pesquisa_bloco_por_nome`
**Descrição:**
Rota de pesquisa por nome do bloco econômico.

**Parâmetros da Requisição:**
A requisição aceita os seguintes parâmetros via query string:
| Parâmetro   | Tipo       | Obrigatório | Descrição |
|-------------|-----------|-------------|-------------|
| `nome`      | `string`  | Não         | Termo da pesquisa. |

**Exemplo de Requisição:**
```
GET /pesquisa_bloco_por_nome?nome=eur
```
**Respostas:**
- **200 OK** - Retorna id e nome de todos os países que possuem `<nome>` em seu nome.
```json
{
  "resposta": [
    {
      "id_bloco": 112,
      "nome_bloco": "Europa"
    },
    {
      "id_bloco": 22,
      "nome_bloco": "União Europeia - UE"
    }
  ]
}
```
**Nota:**
Se o parâmetro 'nome' não for fornecido, a rota irá retornar todos os países em ordem alfabética.