## Exemplo de requisição em typescript para a rota `/ranking_ncm`

```typescript
async function busca_top_ncm(
    tipo: string, 
    qtd?: number, 
    anos?: number[], 
    meses?: number[], 
    paises?: number[], 
    estados?: number[], 
    vias?: number[], 
    urfs?: number[],
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
        appendListParams('urfs', urfs);

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