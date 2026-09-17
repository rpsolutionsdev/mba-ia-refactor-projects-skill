const sqlite3 = require('sqlite3').verbose();

class Database {
    constructor() {
        this.db = new sqlite3.Database(':memory:');
    }

    init() {
        return new Promise((resolve, reject) => {
            this.db.serialize(() => {
                this.db.run("PRAGMA foreign_keys = ON;");
                this.db.run("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, pass TEXT NOT NULL)");
                this.db.run("CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, price REAL NOT NULL, active INTEGER DEFAULT 1)");
                this.db.run("CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, course_id INTEGER NOT NULL, FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE, FOREIGN KEY (course_id) REFERENCES courses(id))");
                this.db.run("CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY AUTOINCREMENT, enrollment_id INTEGER NOT NULL, amount REAL NOT NULL, status TEXT NOT NULL, FOREIGN KEY (enrollment_id) REFERENCES enrollments(id) ON DELETE CASCADE)");
                this.db.run("CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT NOT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)");

                // Seeds
                const CryptoService = require('../services/cryptoService');
                const initialSeedHash = CryptoService.hashPassword('123');
                this.db.run("INSERT INTO users (name, email, pass) VALUES ('Leonan', 'leonan@fullcycle.com.br', ?)", [initialSeedHash]);
                this.db.run("INSERT INTO courses (title, price, active) VALUES ('Clean Architecture', 997.00, 1), ('Docker', 497.00, 1)");
                this.db.run("INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)");
                this.db.run("INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997.00, 'PAID')", (err) => {
                    if (err) reject(err);
                    else resolve();
                });
            });
        });
    }

    get(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.db.get(sql, params, (err, row) => {
                if (err) reject(err);
                else resolve(row);
            });
        });
    }

    all(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.db.all(sql, params, (err, rows) => {
                if (err) reject(err);
                else resolve(rows);
            });
        });
    }

    run(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.db.run(sql, params, function (err) {
                if (err) reject(err);
                else resolve({ lastID: this.lastID, changes: this.changes });
            });
        });
    }
}

const databaseInstance = new Database();
module.exports = databaseInstance;
