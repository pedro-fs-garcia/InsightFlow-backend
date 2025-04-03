# InsightFlow - Backend

Backend do projeto InsightFlow, projeto acadêmico para matérias de Estrutura de dados, Engenharia de Software II e Programação Orientada a Objetos.

Este Backend é uma REST API implementada em Flask - Python, que fornecerá dados de desempenho do comércio exterior brasileiro, reunindo informações de exportação e importação dos anos de 2014 a 2024 fornecidas pelo Ministério do Desenvolvimento, Indústria, Comércio e Serviços. Através desta API será possível consultar dados e análises que identifiquem a performance de estados, municípios e produtos no comércio exterior brasileiro.

## Tecnologias utilizadas no Backend
<p align="center">
  <img alt="Python" height="30" width="40" src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg">
  <img alt="Flask" height="30" width="40" src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/flask/flask-original.svg">
  <img alt="Pandas" height="30" width="40" src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/pandas/pandas-original-wordmark.svg" />
  <img alt="MySQL" height="30" width="40" src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/mysql/mysql-original.svg">
  <img alt="Git" height="30" width="40" src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/git/git-original.svg">
  <img alt="Git" height="30" width="40" src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/github/github-original.svg">
  <img alt="VSCode" height="30" width="40" src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/vscode/vscode-original.svg">
  <img alt="VSCode" height="30" width="40" src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/jira/jira-original.svg">
</p>

## Instruções para que o Servidor funcione corretamente
 - Siga os passos a seguir para que o banco de dados seja salvo corretamente e o servidor seja devidamente inicializado
---
### 1️⃣ Instalar e configurar o PostgreSQL
- Acesse o documento a seguir e siga o passo a passo para a correta instalação:  
[Passo a passo para instalação]()
---
### 2️⃣ Preparar o ambiente virtual
#### Windows
```
python -m venv venv
venv\Scripts\activate
```

#### Linux
```
python3 -m venv venv
source venv/bin/activate
```
---
### 3️⃣ Instalar as dependências necessárias
```
pip install -r requirements.txt
```

---
### 4️⃣ Configurar variáveis de ambiente
crie um arquivo chamado `.env` na raíz do projeto e preencha ou substitua as variáveis a seguir de acordo com o seu ambiente local:
```
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_NAME=insightflow
DB_PORT=5432

BACKEND_SERVER=http://localhost:5000
FRONTEND_SERVER=http://localhost:5173
```
---
### 5️⃣ Executar a limpeza dos dados
Caso os dados ainda não estejam limpos e salvos localmente em data_pipeline/datasets/limpo, execute o comando abaixo para fazê-lo:

Windows
```
python tratar_dados.py
```

Linux
```
python3 tratar_dados.py
```
---

### 6. Inicializar banco de dados
*Essa operação passa todos os dados das tabelas limpas na etapa anterior para o banco de dados (aproximadamente 30 milhões de registros)*  

`Essa operação é lenta e pode levar horas dependendo do processamento do computador`
```
python init_db.py
```
---
### 7. Iniciar o servidor Flask
Windows
```
python run.py
```

Linux
```
python3 run.py
```