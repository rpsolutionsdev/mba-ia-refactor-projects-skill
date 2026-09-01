const ReportModel = require('../models/reportModel');

class ReportController {
    static async getFinancialReport(req, res, next) {
        try {
            const report = await ReportModel.getFinancialReport();
            return res.json(report);
        } catch (error) {
            next(error);
        }
    }
}

module.exports = ReportController;
