CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  code TEXT UNIQUE,
  role TEXT,
  password TEXT
);

CREATE TABLE IF NOT EXISTS protocols (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  num INT,
  file_name TEXT,
  date TEXT,
  status TEXT,
  vote_type TEXT,
  folder TEXT,
  qcount INT,
  quorum_default TEXT
);

CREATE TABLE IF NOT EXISTS questions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  protocol_id INT,
  qnum INT,
  opt1 TEXT,
  opt2 TEXT,
  opt3 TEXT,
  default_vote TEXT,
  quorum TEXT
);

CREATE TABLE IF NOT EXISTS votes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  protocol_id INT,
  user_code TEXT,
  question_id INT,
  vote TEXT,
  voted INT
);

CREATE TABLE IF NOT EXISTS logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  participant_code TEXT,
  action TEXT,
  created_at TEXT
);