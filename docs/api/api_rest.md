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

## Rotas
### Rota `/busca_top_ncm`

**Descrição:**
Esta rota permite buscar os NCMs (Nomenclatura Comum do Mercosul) mais exportados ou importados com base em critérios específicos, como ano, país, estado e via de transporte. Os resultados podem ser ordenados por kg liquido, valor FOB, valor agregado ou número de registros.

**Método HTTP:**
- `GET`

**Rate Limit:**
- 10 requisições por minuto

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
| `crit`      | `string`  | Não         | Critério de ordenação. Valores permitidos: `kg_liquido`, `valor_fob`, `valor_agregado`, `registros`. Padrão: `valor_fob`. |

**Exemplo de Requisição:**
```
GET /busca_top_ncm?tipo=exp&qtd=10&anos=2020&anos=2021&anos=2022&meses=1&meses=2&crit=valor_fob
```

**Respostas:**

- **200 OK** - Retorna os NCMs mais exportados ou importados conforme os filtros aplicados.
```json
{
  "resposta": [
    {
      "ncm": 12019000,
      "produto_descricao": "Soja, mesmo triturada, exceto para semeadura",
      "total_valor_fob": 23270543089.00
    },
    {
      "ncm": 26011100,
      "produto_descricao": "Minérios de ferro e seus concentrados, exceto as piritas de ferro ustuladas",
      "total_valor_fob": 19982659626.00
    }
  ]
}
```

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


**Notas:**
- Caso nenhum ano seja informado, a consulta considerará todos os anos disponíveis (2014-2024).
- A filtragem por países, estados e vias de transporte é opcional.
- O critério de ordenação padrão é `valor_fob`, mas pode ser alterado conforme necessário.

Essa rota é útil para análises de mercado e acompanhamento do fluxo de importação e exportação de produtos brasileiros.




```typescript
async function busca_top_ncm(
    tipo: string, 
    qtd?: number, 
    anos?: number[], 
    meses?: number[], 
    paises?: number[], 
    estados?: number[], 
    vias?: number[], 
    crit?: string
): Promise<any> {
    try {
        // Constrói a URL com parâmetros de query
        const url = new URL('<base_url>/busca_top_ncm');
        
        // Adiciona parâmetros obrigatórios
        url.searchParams.append('tipo', tipo);
        if (qtd) url.searchParams.append('qtd', qtd.toString());
        if (crit) url.searchParams.append('crit', crit);

        // Adiciona listas de parâmetros
        const appendListParams = (paramName: string, values?: number[]) => {
            values?.forEach(value => url.searchParams.append(paramName, value.toString()));
        };

        appendListParams('anos', anos);
        appendListParams('meses', meses);
        appendListParams('paises', paises);
        appendListParams('estados', estados);
        appendListParams('vias', vias);

        const response = await fetch(url.toString(), {
            method: 'GET',
            headers: {
                "Accept": "application/json"
            }
        });

        const data = await response.json();

        if (response.status === 200) {
            return data.resposta;
        } else {
            throw new Error(data.error || 'Erro desconhecido');
        }

    } catch (error) {
        console.error("Erro ao acessar servidor:", error);
        alert(error instanceof Error ? error.message : 'Erro desconhecido');
        throw error;
    }
}
```
