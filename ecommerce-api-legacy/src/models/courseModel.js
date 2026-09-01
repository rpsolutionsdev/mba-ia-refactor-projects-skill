const db = require('../config/database');

class CourseModel {
    static async findActiveById(id) {
        return await db.get("SELECT id, title, price, active FROM courses WHERE id = ? AND active = 1", [id]);
    }

    static async findAll() {
        return await db.all("SELECT id, title, price, active FROM courses");
    }
}

module.exports = CourseModel;
