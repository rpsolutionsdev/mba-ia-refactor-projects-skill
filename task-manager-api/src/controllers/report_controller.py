from flask import jsonify
from src.services.report_service import ReportService

class ReportController:
    @staticmethod
    def get_summary_report():
        report = ReportService.generate_summary()
        return jsonify(report), 200

    @staticmethod
    def get_user_report(user_id):
        report = ReportService.generate_user_report(user_id)
        if not report:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        return jsonify(report), 200
