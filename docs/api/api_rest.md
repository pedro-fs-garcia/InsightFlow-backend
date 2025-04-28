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

- **200 OK** - Retorna os dados requisitados em formato json conforme exemplos listados em suas respectivas rotas em formato json conforme o template a seguir.
```json
{
  "resposta": [
    {
      "descricao": "Ovos de outras aves, não para incubação ou não frescos",
      "id_ncm": 4079000
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

## Rotas
- [Documentação das rotas de NCM](ncm_api.md)  
- [Documentação das rotas de SH4](sh4_api.md)
- [Documentação das rotas de país](pais_api.md)
- [Documentação das rotas de bloco](bloco_api.md)
