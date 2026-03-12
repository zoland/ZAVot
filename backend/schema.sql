-- =============================================
-- ZAVot Database Schema v2
-- SQLite (совместимо с MySQL)
-- =============================================

-- USERS — пользователи
CREATE TABLE IF NOT EXISTS users (
    u_code      VARCHAR(50)     NOT NULL,
    role        VARCHAR(20)     NOT NULL,
    password    VARCHAR(100)    NOT NULL,
    casting     TINYINT         DEFAULT 0,
    PRIMARY KEY (u_code)
);

-- PROTOCOLS — протоколы
CREATE TABLE IF NOT EXISTS protocols (
    p_num       VARCHAR(20)     NOT NULL,
    description VARCHAR(255),
    date_start  VARCHAR(10),
    date_end    VARCHAR(10),
    status      VARCHAR(10)     DEFAULT 'Закрыт',
    vote_type   VARCHAR(10)     DEFAULT 'Явное',
    file_name   VARCHAR(255),
    file_hash   VARCHAR(64),
    PRIMARY KEY (p_num)
);

-- QUESTIONS — вопросы протокола
CREATE TABLE IF NOT EXISTS questions (
    p_num       VARCHAR(20)     NOT NULL,
    q_num       VARCHAR(10)     NOT NULL,
    question    VARCHAR(500)    NOT NULL,
    q_type      VARCHAR(10)     DEFAULT 'Голос',
    quorum      DECIMAL(3,2)    DEFAULT 0.50,
    default_vote INT            DEFAULT 0,
    multi       TINYINT         DEFAULT 0,
    PRIMARY KEY (p_num, q_num)
);

-- OPTIONS — варианты для Выбор / Опрос
CREATE TABLE IF NOT EXISTS options (
    p_num       VARCHAR(20)     NOT NULL,
    q_num       VARCHAR(10)     NOT NULL,
    o_num       INT             NOT NULL,
    content     VARCHAR(500)    NOT NULL,
    PRIMARY KEY (p_num, q_num, o_num),
    FOREIGN KEY (p_num, q_num) REFERENCES questions(p_num, q_num)
);

-- MATERIALS — рабочие материалы
CREATE TABLE IF NOT EXISTS materials (
    p_num       VARCHAR(20)     NOT NULL,
    q_num       VARCHAR(10)     NOT NULL,
    m_num       INT             NOT NULL,
    file_name   VARCHAR(255)    NOT NULL,
    description VARCHAR(255),
    PRIMARY KEY (p_num, q_num, m_num)
);

-- VOTES — голоса
CREATE TABLE IF NOT EXISTS votes (
    p_num       VARCHAR(20)     NOT NULL,
    q_num       VARCHAR(10)     NOT NULL,
    u_code      VARCHAR(50)     NOT NULL,
    vote        VARCHAR(50),
    vote_date   VARCHAR(10),
    PRIMARY KEY (p_num, q_num, u_code)
);

-- LOGS — журнал событий
CREATE TABLE IF NOT EXISTS logs (
    id          INTEGER         PRIMARY KEY AUTOINCREMENT,
    u_code      VARCHAR(50),
    action      VARCHAR(255),
    l_date      VARCHAR(10),
    l_time      VARCHAR(8)
);