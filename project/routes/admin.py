from flask import Blueprint, jsonify
from project.models.attack_log import AttackLog

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/logs', methods=['GET'])
def get_logs():
    logs = AttackLog.query.order_by(AttackLog.id.desc()).all()
    return jsonify([
        {
            "timestamp": log.timestamp,
            "username": log.username,
            "ip": log.ip,
            "attack_type": log.attack_type,
            "original": log.original,
            "cleaned": log.cleaned
        } for log in logs
    ])
