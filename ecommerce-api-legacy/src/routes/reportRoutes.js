const express = require('express');
const router = express.Router();
const ReportController = require('../controllers/reportController');

router.get('/admin/financial-report', ReportController.getFinancialReport);

module.exports = router;
