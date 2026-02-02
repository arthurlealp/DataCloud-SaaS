# 🚀 Guia de Deploy - DataCloud SaaS

Este guia explica como fazer deploy do projeto gratuitamente usando Streamlit Community Cloud.

## 📋 Pré-requisitos

- ✅ Projeto no GitHub (público)
- ✅ Conta no GitHub
- ✅ 5 minutos do seu tempo

---

## 🌟 Deploy no Streamlit Community Cloud (GRÁTIS)

### **Passo 1: Acesse o Streamlit Cloud**

1. Vá para: https://share.streamlit.io/
2. Clique em **"Sign up"** ou **"Sign in"**
3. Faça login com sua conta **GitHub**
4. Autorize o Streamlit a acessar seus repositórios

### **Passo 2: Criar Novo App**

1. Clique no botão **"New app"**
2. Preencha os campos:
   ```
   Repository: arthurlealp/DataCloud-SaaS
   Branch: main
   Main file path: app.py
   ```
3. (Opcional) Escolha uma URL customizada:
   ```
   App URL: datacloud-saas.streamlit.app
   ```

### **Passo 3: Configurar Variáveis de Ambiente (Secrets)**

1. Clique em **"Advanced settings..."** antes de fazer deploy
2. Ou após deploy, vá em **"Settings → Secrets"**
3. Adicione as variáveis em formato TOML:

```toml
# Ambiente
ENV = "production"
DEBUG = false
LOG_LEVEL = "INFO"

# Metas de Negócio (ajuste conforme necessário)
META_RECEITA_MENSAL = 60000.00
META_CHURN_MAX = 0.05
META_LTV_MINIMO = 1000.00

# Dashboard
REQUIRE_AUTH = false  # Mude para true se quiser autenticação
PAGE_SIZE = 50
CACHE_TTL = 300

# Diretórios (Streamlit Cloud já configura automaticamente)
DATA_DIR = "data"
LOG_DIR = "logs"
```

### **Passo 4: Deploy! 🎉**

1. Clique em **"Deploy!"**
2. Aguarde 2-3 minutos enquanto o Streamlit:
   - Clona seu repositório
   - Instala dependências do `requirements.txt`
   - Inicializa o banco de dados
   - Inicia o app

3. Seu app estará disponível em:
   ```
   https://datacloud-saas-arthurlealp.streamlit.app
   ```

---

## 🗄️ Inicialização do Banco de Dados

O Streamlit Cloud cria um banco SQLite vazio na primeira execução. Você tem duas opções:

### **Opção A: Rodar Seed Script Manualmente**

1. No dashboard do Streamlit Cloud, vá em **"Manage app → Terminal"**
2. Execute:
   ```bash
   python utils/seed.py
   ```

### **Opção B: Modificar app.py para Inicializar Automaticamente**

Adicione no início do `app.py`:

```python
import os
from pathlib import Path

# Verifica se banco existe, se não, cria
if not Path("data/saas.db").exists():
    import subprocess
    subprocess.run(["python", "utils/seed.py"])
```

> ⚠️ **Atenção:** Em produção, usar um banco PostgreSQL é mais recomendado para múltiplos usuários simultâneos.

---

## 🔄 Deploy Automático (CI/CD)

Após configurado, **qualquer push** na branch `main` dispara um **deploy automático**!

```bash
# Faça alterações localmente
git add .
git commit -m "feat: nova feature"
git push

# Streamlit Cloud detecta automaticamente e redeploy em ~2min
```

---

## 🛠️ Troubleshooting

### **Erro: ModuleNotFoundError**
- Verifique se `requirements.txt` está atualizado
- Certifique-se que todas as dependências estão listadas

### **Erro: No such file or directory: data/saas.db**
- Execute o seed script manualmente (Opção A acima)
- Ou adicione inicialização automática (Opção B)

### **App muito lento**
- SQLite tem limitações de concorrência
- Para produção, considere migrar para PostgreSQL (veja seção abaixo)

### **Erro de memória**
- Streamlit Cloud tem limite de ~1GB RAM (plano gratuito)
- Otimize queries e use cache efetivamente

---

## 🚀 Alternativas de Deploy

### **1. Render (Grátis com PostgreSQL)**
- Site: https://render.com
- Suporta PostgreSQL gratuitamente
- Mais robusto para produção

### **2. Railway (Grátis por 500h/mês)**
- Site: https://railway.app
- Deploy automático do GitHub
- Suporta PostgreSQL, Redis

### **3. Heroku (Pago após trial)**
- Site: https://heroku.com
- Mais caro, mas muito confiável
- Fácil configuração de add-ons

### **4. Google Cloud Run**
- Site: https://cloud.google.com/run
- Serverless, escala automaticamente
- Gratuito até 2 milhões de requests/mês

---

## 📊 Monitoramento

### **Streamlit Cloud Analytics**
- Acesse **"Analytics"** no dashboard
- Veja número de visualizações
- Monitore uso de recursos

### **Logs**
- Vá em **"Manage app → Logs"**
- Veja erros em tempo real
- Útil para debug

---

## 🎯 Próximos Passos (Produção)

Para um ambiente de produção real:

1. **Migrar para PostgreSQL**
   - Mais robusto para múltiplos usuários
   - Usa serviços como Supabase (grátis até 500MB)

2. **Adicionar Autenticação Real**
   - Substituir usuários hardcoded
   - Usar banco de dados para usuários
   - Implementar OAuth (Google, GitHub)

3. **Configurar Domínio Customizado**
   - Em vez de `.streamlit.app`
   - Usar seu próprio domínio

4. **Adicionar Analytics**
   - Google Analytics
   - Plausible (privacy-friendly)

5. **Implementar Backups**
   - Backup automático do banco
   - Restauração em caso de falha

---

## ✅ Checklist de Deployment

Antes de fazer deploy, verifique:

- [ ] `requirements.txt` está atualizado
- [ ] `.streamlit/config.toml` existe
- [ ] `packages.txt` existe (mesmo que vazio)
- [ ] `.gitignore` não inclui arquivos necessários
- [ ] Código está funcionando localmente
- [ ] Secrets configurados corretamente
- [ ] Banco de dados será inicializado

---

## 🆘 Suporte

- **Documentação Oficial:** https://docs.streamlit.io/streamlit-community-cloud
- **Fórum da Comunidade:** https://discuss.streamlit.io/
- **Issues do Projeto:** https://github.com/arthurlealp/DataCloud-SaaS/issues

---

**Desenvolvido por Arthur Leal** | [GitHub](https://github.com/arthurlealp/DataCloud-SaaS)
