const db = require('../config/database');

class PaymentModel {
    static async create(enrollmentId, amount, status) {
        const result = await db.run(
            "INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)",
            [enrollmentId, amount, status]
        );
        return result.lastID;
    }

    static async logAudit(action) {
        return await db.run(
            "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
            [action]
        );
    }
}

module.exports = PaymentModel;
