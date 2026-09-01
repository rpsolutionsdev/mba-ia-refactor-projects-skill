const db = require('../config/database');

class UserModel {
    static async findByEmail(email) {
        return await db.get("SELECT id, name, email, pass FROM users WHERE email = ?", [email]);
    }

    static async findById(id) {
        return await db.get("SELECT id, name, email FROM users WHERE id = ?", [id]);
    }

    static async create(name, email, hashedPassword) {
        const result = await db.run(
            "INSERT INTO users (name, email, pass) VALUES (?, ?, ?)",
            [name, email, hashedPassword]
        );
        return result.lastID;
    }

    static async delete(id) {
        // Remove pagamentos e matrículas associadas de forma consistente
        const enrollments = await db.all("SELECT id FROM enrollments WHERE user_id = ?", [id]);
        for (const enr of enrollments) {
            await db.run("DELETE FROM payments WHERE enrollment_id = ?", [enr.id]);
        }
        await db.run("DELETE FROM enrollments WHERE user_id = ?", [id]);
        const result = await db.run("DELETE FROM users WHERE id = ?", [id]);
        return result.changes > 0;
    }
}

module.exports = UserModel;
