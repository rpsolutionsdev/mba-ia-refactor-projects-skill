const db = require('../config/database');

class EnrollmentModel {
    static async create(userId, courseId) {
        const result = await db.run(
            "INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)",
            [userId, courseId]
        );
        return result.lastID;
    }

    static async findByCourseId(courseId) {
        return await db.all("SELECT id, user_id, course_id FROM enrollments WHERE course_id = ?", [courseId]);
    }
}

module.exports = EnrollmentModel;
