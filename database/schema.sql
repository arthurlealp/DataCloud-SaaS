-- ============================================
-- DataCloud SaaS - Schema do Banco de Dados
-- Execute este script para criar a estrutura
-- ============================================

-- === TABELAS ===

-- Tabela de Planos
CREATE TABLE IF NOT EXISTS planos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    preco_mensal REAL NOT NULL,
    limite_usuarios INTEGER NOT NULL,
    armazenamento_gb REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Empresas
CREATE TABLE IF NOT EXISTS empresas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    razao_social TEXT NOT NULL,
    cnpj TEXT UNIQUE NOT NULL,
    email TEXT,
    telefone TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Assinaturas
CREATE TABLE IF NOT EXISTS assinaturas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER NOT NULL,
    plano_id INTEGER NOT NULL,
    status TEXT CHECK (
        status IN (
            'Ativo',
            'Cancelado',
            'Trial',
            'Inativo'
        )
    ) DEFAULT 'Trial',
    data_inicio DATE NOT NULL,
    proxima_cobranca DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (empresa_id) REFERENCES empresas (id) ON DELETE CASCADE,
    FOREIGN KEY (plano_id) REFERENCES planos (id) ON DELETE RESTRICT
);

-- === ÍNDICES PARA PERFORMANCE ===

CREATE INDEX IF NOT EXISTS idx_assinaturas_empresa ON assinaturas (empresa_id);

CREATE INDEX IF NOT EXISTS idx_assinaturas_plano ON assinaturas (plano_id);

CREATE INDEX IF NOT EXISTS idx_assinaturas_status ON assinaturas (status);

CREATE INDEX IF NOT EXISTS idx_empresas_cnpj ON empresas (cnpj);

-- === VIEW OTIMIZADA ===

DROP VIEW IF EXISTS vw_assinaturas_detalhadas;

CREATE VIEW vw_assinaturas_detalhadas AS
SELECT
    -- IDs
    a.id AS assinatura_id,
    e.id AS empresa_id,
    p.id AS plano_id,

-- Status e Datas
a.status, a.data_inicio, a.proxima_cobranca,

-- Dados da Empresa
e.razao_social, e.cnpj, e.email, e.telefone,

-- Dados do Plano
p.nome AS nome_plano,
p.preco_mensal,
p.limite_usuarios,
p.armazenamento_gb
FROM
    assinaturas AS a
    JOIN empresas AS e ON a.empresa_id = e.id
    JOIN planos AS p ON a.plano_id = p.id;

-- === DADOS INICIAIS (SEED BÁSICO) ===

-- Planos padrão
INSERT OR IGNORE INTO
    planos (
        id,
        nome,
        preco_mensal,
        limite_usuarios,
        armazenamento_gb
    )
VALUES (1, 'Basic', 99.90, 3, 50.0),
    (2, 'Pro', 199.90, 10, 500.0),
    (
        3,
        'Enterprise',
        499.90,
        50,
        2000.0
    );

-- Empresa de exemplo (opcional)
INSERT OR IGNORE INTO
    empresas (id, razao_social, cnpj, email)
VALUES (
        1,
        'Empresa Exemplo LTDA',
        '00.000.000/0001-00',
        'contato@exemplo.com.br'
    );

-- Assinatura de exemplo (opcional)
INSERT OR IGNORE INTO
    assinaturas (
        empresa_id,
        plano_id,
        status,
        data_inicio,
        proxima_cobranca
    )
VALUES (
        1,
        1,
        'Ativo',
        date('now'),
        date('now', '+30 days')
    );

-- === VERIFICAÇÃO ===

SELECT '✅ Banco de dados criado com sucesso!' as status;

SELECT 'Total de planos: ' || COUNT(*) FROM planos;

SELECT 'Total de empresas: ' || COUNT(*) FROM empresas;

SELECT 'Total de assinaturas: ' || COUNT(*) FROM assinaturas;