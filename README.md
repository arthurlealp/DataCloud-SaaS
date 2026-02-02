# DataCloud SaaS Analytics

Projeto desenvolvido para praticar **arquitetura de software**, **organização em camadas**, **ETL** e **construção de dashboards** no contexto de métricas SaaS.

## Objetivo

Aplicar na prática os seguintes conceitos:

- **Clean Architecture** (separação em camadas)
- **Repository Pattern** (abstração de persistência)
- **Pipeline ETL** (extração, transformação, carga)
- **Validação de dados** com Pydantic
- **Dashboards interativos** com Streamlit
- **Boas práticas** de organização de projetos Python

O domínio escolhido foi **SaaS (Software as a Service)** para trabalhar com métricas reais: MRR, ARR, LTV e Churn.

---

## Stack

| Categoria                | Tecnologia                                   |
| ------------------------ | -------------------------------------------- |
| **Backend**        | Python 3.10+, Pandas, Pydantic               |
| **Interface**      | Streamlit, Altair                            |
| **Banco de Dados** | SQLite (estrutura preparada para migração) |
| **Validação**    | Pydantic Schemas                             |

---

## Arquitetura

O projeto foi estruturado seguindo **Clean Architecture**, dividido em quatro camadas:

```
src/
├── domain/          # Entidades, regras de negócio e schemas
├── infrastructure/  # Repositórios e acesso ao banco
├── application/     # Casos de uso, ETL e cálculo de métricas
└── presentation/    # Interface (autenticação, componentes)
```

### Separação de Responsabilidades

- **Domain**: Regras de negócio puras, sem dependências externas
- **Infrastructure**: Implementação concreta de persistência (SQLite)
- **Application**: Orquestração de casos de uso e processamento
- **Presentation**: Camada de visualização (Streamlit)

**Vantagem:** Trocar o banco de dados requer alteração apenas na camada `infrastructure`.

---

## Funcionalidades Implementadas

- ✅ Autenticação simples com hash SHA-256
- ✅ Pipeline ETL para processamento de dados
- ✅ Cálculo de KPIs SaaS:
  - MRR (Monthly Recurring Revenue)
  - ARR (Annual Recurring Revenue)
  - LTV (Lifetime Value)
  - Churn Rate
  - Ticket Médio
- ✅ Sistema de alertas configurável (3 níveis)
- ✅ Cache com `st.cache_data` (TTL 5min)
- ✅ Exportação em CSV e Excel
- ✅ Paginação para grandes volumes

---

## Decisões Técnicas

### Repository Pattern

Utilizado para **desacoplar** regras de negócio do mecanismo de persistência. Mudanças no banco não afetam a lógica de aplicação.

### Pydantic

Validação de dados **na entrada** para evitar inconsistências propagadas até o dashboard.

### Cache

Uso de `@st.cache_data(ttl=300)` para reduzir tempo de resposta de ~3s para <0.5s em consultas repetidas.

### SQLite

Escolhido por **simplicidade** e **portabilidade** (zero configuração). Estrutura preparada para futura migração para PostgreSQL.

---

## 🧠 Desafios e Aprendizados

### Refatoração Arquitetural

**Problema:** Inicialmente, todo o código estava em um único arquivo (~500 linhas). Funcional, mas difícil de manter.

**Solução:** Refatorei para Clean Architecture com 4 camadas distintas. O código ficou mais fácil de entender e estender.

### Performance do Streamlit

**Problema:** Cada clique recarregava TUDO do banco. Tempo de resposta: ~3s.

**Solução:** Implementei cache com `st.cache_data`, otimizei queries SQL com índices e adicionei paginação.

**Resultado:** Tempo reduzido para <0.5s.

### Tentativa de Deploy

**Desafio:** Tentei deploy no Streamlit Community Cloud e encontrei:

- Incompatibilidade do Pydantic 2.5 com Python 3.13
- Problemas com `subprocess.run()` no ambiente cloud
- Dificuldade em popular banco SQLite remotamente

**Aprendizado:** Deploy não é "apertar um botão". Cada ambiente tem suas peculiaridades. Próximo passo: estudar Docker para ambientes mais consistentes.

### Validação com Pydantic

**Descoberta:** 90% dos bugs vinham de **dados inconsistentes** (datas inválidas, valores None inesperados).

**Impacto:** Erros capturados na entrada. Dashboard nunca mais quebrou por dado inválido.

---

## Execução Local

```bash
# 1. Clone o repositório
git clone https://github.com/arthurlealp/DataCloud-SaaS.git
cd DataCloud-SaaS

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Inicialize o banco de dados
python utils/seed.py

# 4. Rode o dashboard
streamlit run app.py
```

**Acesso:** http://localhost:8501

**Credenciais (se autenticação estiver ativa):**

- Admin: `admin` / `admin123`
- Viewer: `viewer` / `viewer123`

---

## Estrutura do Projeto

```
DataCloud-SaaS/
├── src/
│   ├── domain/         # Schemas Pydantic, entidades
│   ├── infrastructure/ # Repositórios, database
│   ├── application/    # ETL, KPIs, alertas, exportação
│   └── presentation/   # Autenticação
├── config/             # Settings, logging
├── database/           # Schema SQL
├── utils/              # Seed, helpers
├── app.py              # Dashboard Streamlit
├── main.py             # CLI do pipeline ETL
└── requirements.txt
```

---

## Pontos de Aprendizado

Durante o desenvolvimento, pratiquei:

- ✅ Organização de código em camadas
- ✅ Tratamento estruturado de exceções
- ✅ Uso consistente de type hints
- ✅ Logging com rotação de arquivos
- ✅ Gestão de dependências e compatibilidade
- ✅ Otimização de consultas e cache
- ✅ Problemas comuns de deploy cloud

---

## Próximos Passos

- [ ] Migração para PostgreSQL (multi-tenancy)
- [ ] Exposição de API REST com FastAPI
- [ ] Testes automatizados completos (pytest)
- [ ] CI/CD com GitHub Actions
- [ ] Containerização com Docker
- [ ] Machine Learning para previsão de churn

---

## 👨‍💻 Autor

**Arthur Leal Pacheco**
Data Engineer

[![LinkedIn](https://img.shields.io/badge/-LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/arthur-leal-pacheco-b95058353/)
[![GitHub](https://img.shields.io/badge/-GitHub-181717?style=flat&logo=github&logoColor=white)](https://github.com/arthurlealp)

---

## Licença

MIT License - Livre para uso e modificação.
