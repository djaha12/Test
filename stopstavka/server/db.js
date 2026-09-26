import { DatabaseSync } from 'node:sqlite';

// Сервер хранит только коды подписки (в виде хешей), счётчики сообщений ИИ и обезличенную
// статистику событий. Личных данных пользователей здесь нет.
export function openDb(file = ':memory:') {
  const db = new DatabaseSync(file);
  if (file !== ':memory:') db.exec('PRAGMA journal_mode = WAL;');
  db.exec(`
    CREATE TABLE IF NOT EXISTS codes (
      hash TEXT PRIMARY KEY,
      days INTEGER NOT NULL,
      note TEXT NOT NULL DEFAULT '',
      created_at INTEGER NOT NULL,
      redeemed_at INTEGER,
      device TEXT
    );
    CREATE TABLE IF NOT EXISTS ai_usage (
      subject TEXT NOT NULL,
      day TEXT NOT NULL,
      count INTEGER NOT NULL DEFAULT 0,
      PRIMARY KEY (subject, day)
    );
    CREATE TABLE IF NOT EXISTS events (
      day TEXT NOT NULL,
      name TEXT NOT NULL,
      source TEXT NOT NULL DEFAULT '',
      count INTEGER NOT NULL DEFAULT 0,
      PRIMARY KEY (day, name, source)
    );
  `);
  return db;
}

export function utcDay(now = Date.now()) {
  return new Date(now).toISOString().slice(0, 10);
}
