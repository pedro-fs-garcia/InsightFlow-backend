# 📘 Documentação da API – Estado

---

## GET `/ranking_estado`

**Descrição:**  
Esta rota permite rankear os estados brasileiros com base nas exportações (`exp`) ou importações (`imp`), considerando filtros como ano, mês, NCM, país, via de transporte, entre outros.  
Agora é possível consultar **vários tipos ao mesmo tempo** (`tipo=exp&tipo=imp`).

### Exemplo de Requisição:
```
GET /ranking_estado?tipo=exp&tipo=imp&qtd=10&anos=2020&anos=2021&meses=1&meses=2&crit=valor_fob
```

### Parâmetros:

| Parâmetro   | Tipo         | Obrigatório | Descrição |
|-------------|--------------|-------------|-----------|
| `tipo`      | `list[str]`  | ✅ Sim      | Tipo de transação: `exp` (exportação) ou `imp` (importação). Aceita mais de um. |
| `qtd`       | `int`        | ❌ Não      | Número máximo de estados no ranking. Padrão: `10`. |
| `anos`      | `list[int]`  | ❌ Não      | Anos considerados. Permitidos: `2014-2024`. |
| `meses`     | `list[int]`  | ❌ Não      | Meses considerados (1 a 12). |
| `ncm`       | `list[int]`  | ❌ Não      | Lista de códigos NCM. |
| `paises`    | `list[int]`  | ❌ Não      | Lista de países. |
| `vias`      | `list[int]`  | ❌ Não      | Vias de transporte. |
| `urfs`      | `list[int]`  | ❌ Não      | Unidades da Receita Federal. |
| `crit`      | `string`     | ❌ Não      | Critério de ordenação: `kg_liquido`, `valor_fob`, `valor_agregado`, `registros`. Padrão: `valor_fob`. |
| `cresc`     | `int`        | ❌ Não      | 0 para decrescente (padrão), 1 para crescente. |

### Exemplo de Resposta:
```json
{
  "resposta": [
    {
      "tipo": "exp",
      "dados": [
        {
          "id_estado": 35,
          "sigla_estado": "SP",
          "nome_estado": "São Paulo",
          "total_valor_fob": "123456789.00",
          "total_kg_liquido": "987654321.00",
          "total_valor_agregado": "0.32",
          "total_registros": 4532
        }
      ]
    },
    {
      "tipo": "imp",
      "dados": [
        {
          "id_estado": 33,
          "sigla_estado": "MG",
          "nome_estado": "Minas Gerais",
          "total_valor_fob": "102345678.00",
          "total_kg_liquido": "765432109.00",
          "total_valor_agregado": "0.28",
          "total_registros": 5120
        }
      ]
    }
  ]
}
```

---

## GET `/busca_estado_hist`

**Descrição:**  
Busca a série histórica (por mês) de exportações e/ou importações dos estados brasileiros com base nos filtros fornecidos.

### Exemplo de Requisição:
```
GET /busca_estado_hist?tipo=exp&tipo=imp&estados=33&estados=35&anos=2020&anos=2021&meses=1&meses=2
```

### Parâmetros:

| Parâmetro   | Tipo         | Obrigatório | Descrição |
|-------------|--------------|-------------|-----------|
| `tipo`      | `list[str]`  | ✅ Sim      | Um ou mais tipos: `exp`, `imp`. |
| `estados`   | `list[int]`  | ✅ Sim      | Lista de estados (por ID) a consultar. |
| `anos`      | `list[int]`  | ❌ Não      | Lista de anos (2014 a 2024). |
| `meses`     | `list[int]`  | ❌ Não      | Lista de meses (1 a 12). |
| `ncm`       | `list[int]`  | ❌ Não      | Lista de códigos NCM. |
| `paises`    | `list[int]`  | ❌ Não      | Lista de países. |
| `vias`      | `list[int]`  | ❌ Não      | Vias de transporte. |
| `urfs`      | `list[int]`  | ❌ Não      | Unidades da Receita Federal. |

### Exemplo de Resposta:
```json
{
  "resposta": [
    {
      "tipo": "exp",
      "dados": [
        {
          "ano": 2020,
          "mes": 1,
          "id_estado": 35,
          "sigla_estado": "SP",
          "nome_estado": "São Paulo",
          "valor_fob_total_exp": "1000000.00",
          "kg_liquido_total_exp": "500000.00",
          "valor_agregado_total_exp": "2.00",
          "total_registros": 250
        }
      ]
    },
    {
      "tipo": "imp",
      "dados": [
        {
          "ano": 2020,
          "mes": 1,
          "id_estado": 35,
          "sigla_estado": "SP",
          "nome_estado": "São Paulo",
          "valor_fob_total_imp": "1200000.00",
          "kg_liquido_total_imp": "480000.00",
          "valor_agregado_total_imp": "2.50",
          "total_registros": 300
        }
      ]
    }
  ]
}
```

---

## GET `/pesquisa_estado_por_nome`

**Descrição:**  
Permite pesquisar estados pelo nome (autocompletar). Se o parâmetro `nome` não for fornecido, retorna todos os estados ordenados alfabeticamente.

### Exemplo de Requisição:
```
GET /pesquisa_estado_por_nome?nome=Rio
```

### Parâmetros:

| Parâmetro | Tipo     | Obrigatório | Descrição                      |
|-----------|----------|-------------|--------------------------------|
| `nome`    | `string` | ❌ Não      | Parte do nome do estado.       |

### Exemplo de Resposta:
```json
{
  "resposta": [
    { "id_estado": 36, "nome": "Rio de Janeiro", "sigla": "RJ" },
    { "id_estado": 24, "nome": "Rio Grande do Norte", "sigla": "RN" },
    { "id_estado": 45, "nome": "Rio Grande do Sul", "sigla": "RS" }
  ]
}
```
