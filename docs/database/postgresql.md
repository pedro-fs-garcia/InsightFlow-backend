# 📌 Instalação do PostgreSQL no Windows e Linux

## 🖥️ Windows

### 1️⃣ Baixar o Instalador  
- Acesse o site oficial: [Download PostgreSQL para Windows](https://www.postgresql.org/download/windows/)  
- Clique em **"Download the installer"** e baixe a versão mais recente.

### 2️⃣ Executar o Instalador  
- Abra o arquivo baixado (`postgresql-xx.x-x-windows-x64.exe`).  
- Siga as instruções do assistente de instalação.

### 3️⃣ Configurar Durante a Instalação  
- Escolha o diretório de instalação (ou deixe o padrão).  
- Selecione os componentes:  
  ✅ **PostgreSQL Server**  
  ✅ **pgAdmin** (interface gráfica para gerenciar o banco)  
- Defina uma senha para o usuário `postgres`. **Anote essa senha!**  
- Escolha a porta do PostgreSQL (padrão: `5432`).

### 4️⃣ Finalizar a Instalação  
- Após a instalação, inicie o **pgAdmin** para testar a conexão.  
- Para acessar via terminal, abra o **Prompt de Comando** e digite:  
  ```bash
  psql -U postgres
  ```
  (Insira a senha definida na instalação).

### 5️⃣ Acessar um banco de dados específico
- Para se conectar a um banco de dados específico, digite o nome do banco após  -d :
```bash
psql -U postgres -d insightflow
```
---

## 🐧 Linux (Ubuntu/Debian)

### 1️⃣ Atualizar o Sistema  
```bash
sudo apt update
sudo apt upgrade
```

### 2️⃣ Instalar o PostgreSQL  
```bash
sudo apt install postgresql postgresql-contrib -y
```

### 3️⃣ Iniciar e Habilitar o Serviço  
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 4️⃣ Acessar o PostgreSQL  
- O PostgreSQL cria automaticamente um usuário chamado **postgres**. Para acessar o terminal do banco, use:  
  ```bash
  sudo -i -u postgres
  psql
  ```
- Para sair do `psql`, digite:  
  ```sql
  \q
  ```

### 5️⃣ Alterar a Senha do Usuário `postgres`  
Dentro do `psql`, digite:  
```sql
ALTER USER postgres WITH PASSWORD 'sua_senha';
```

---

## 🚀 Testando a Instalação  
Independente do sistema operacional, teste a conexão:  
```bash
psql -U postgres -h localhost
```
Digite a senha e veja se consegue acessar o banco. ✅


## Conecte-se ao insightflow:
```bash
psql -U postgres -h localhost -d insightflow
```