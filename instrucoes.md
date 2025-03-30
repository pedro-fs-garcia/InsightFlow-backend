# Instruções para que o Servidor funcione corretamente

### Preparar o ambiente virtual
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
### Instalar as dependências necessárias
```
pip install -r requirements.txt
```
---
### Executar a limpeza dos dados
Windows
```
python tratar_dados.py
```

Linux
```
python3 tratar_dados.py
```
---

### Inicializar banco de dados
*Essa operação passa todos os dados das tabelas limpas na etapa anterior para o banco de dados (aproximadamente 30 milhões de registros)*  

`Essa operação é lenta e pode levar horas dependendo do processamento do computador`
```
python init_db.py
```
---
### Iniciar o servidor Flask
Windows
```
python run.py
```

Linux
```
python3 run.py
```