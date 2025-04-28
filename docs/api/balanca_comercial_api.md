## GET `/busca_balanca_comercial`
 **Descrição:**
 Esta rota permite acessar a balança comercial do Brasil de acordo os filtros selecionados. A balança comercial é a diferença entre o total importado e o total exportado em USD. Usamos o valor FOB para este cálculo.

**Exemplo de Requisição:**
```
GET /busca_balanca_comercial?anos=2014
```

**Parâmetros da Requisição:**
A requisição aceita os seguintes parâmetros via query string:

| Parâmetro   | Tipo       | Obrigatório | Descrição |
|-------------|-----------|-------------|-------------|
| `anos`      | `list[int]` | Não       | Lista de anos a serem considerados. Valores permitidos: `2014-2024`. |
| `meses`     | `list[int]` | Não       | Lista de meses a serem considerados (1 a 12). |
| `paises`   | `list[int]` | Não       | Lista de identificadores de paises a serem considerados. |
| `estados`   | `list[int]` | Não       | Lista de identificadores de estados brasileiros a serem considerados. |

**Respostas:**
- **200 OK** - Retorna a balança comercial de acordo com os critérios especificados. Se nenhum critério for especificado, será retornada a balança comercial do período de 2014 a 2024.
```json
{
  "resposta": [
    {
      "ano": 2014,
      "balanca_comercial": "-18276460186.00",
      "total_exportado": "207382721205.00",
      "total_importado": "225659181391.00"
    },
    {
      "ano": 2015,
      "balanca_comercial": "6453885754.00",
      "total_exportado": "174952767143.00",
      "total_importado": "168498881389.00"
    }
  ]
}
```