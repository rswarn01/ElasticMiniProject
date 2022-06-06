from datetime import datetime
from elastic.extensions import db, mm


class Ping(db.Model):
    """Model for `ping` table"""

    __tablename__ = "ping"
    id = db.Column(db.INTEGER, primary_key=True)
    value = db.Column(db.String(20), nullable=False, unique=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class PingMarshal(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = Ping
        exclude = ["id"]


ping_marshal = PingMarshal()
