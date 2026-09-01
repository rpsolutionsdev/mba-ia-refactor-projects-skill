const db = require('../config/database');

class ReportModel {
    static async getFinancialReport() {
        const courses = await db.all("SELECT id, title, price FROM courses");
        const report = [];

        for (const course of courses) {
            const rows = await db.all(`
                SELECT 
                    u.name as student_name,
                    p.amount as paid_amount,
                    p.status as payment_status
                FROM enrollments e
                LEFT JOIN users u ON e.user_id = u.id
                LEFT JOIN payments p ON p.enrollment_id = e.id
                WHERE e.course_id = ?
            `, [course.id]);

            let totalRevenue = 0;
            const students = [];

            for (const row of rows) {
                if (row.payment_status === 'PAID') {
                    totalRevenue += (row.paid_amount || 0);
                }
                students.push({
                    student: row.student_name || 'Unknown',
                    paid: row.paid_amount || 0
                });
            }

            report.push({
                course: course.title,
                revenue: totalRevenue,
                students: students
            });
        }

        return report;
    }
}

module.exports = ReportModel;
