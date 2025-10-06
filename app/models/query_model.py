from app.config.extensions import db
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = 'demo'
    
    # id = db.Column(db.Integer, primary_key=True)
    # nombre_completo = db.Column(db.String(100), nullable=False)
    # correo_electronico = db.Column(db.String(120), unique=True, nullable=False)
    # fecha_nacimiento = db.Column(db.Date)
    # esta_activo = db.Column(db.Boolean, default=True)
    # fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    # fecha_actualizacion = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        # return f'<Usuario {self.correo_electronico}>'
        return f'Demo'