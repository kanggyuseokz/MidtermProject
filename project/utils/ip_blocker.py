from project.extensions import db
from project.models.blocked_ip import BlockedIP
from datetime import datetime

BLOCK_THRESHOLD = 5

def is_ip_blocked(ip: str) -> bool:
    return BlockedIP.query.filter_by(ip=ip).first() is not None

def record_attack_and_check_block(ip: str, reason: str):
    record = BlockedIP.query.filter_by(ip=ip).first()
    if record:
        record.count += 1
    else:
        record = BlockedIP(ip=ip, blocked_at=datetime.now(), reason=reason, count=1)
        db.session.add(record)
    db.session.commit()

    return record.count >= BLOCK_THRESHOLD