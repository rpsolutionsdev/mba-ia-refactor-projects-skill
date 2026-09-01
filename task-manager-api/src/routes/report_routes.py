from flask import Blueprint
from src.controllers.report_controller import ReportController

report_bp = Blueprint('reports', __name__)

report_bp.add_url_rule('/reports/summary', 'get_summary_report', ReportController.get_summary_report, methods=['GET'])
report_bp.add_url_rule('/reports/user/<int:user_id>', 'get_user_report', ReportController.get_user_report, methods=['GET'])
