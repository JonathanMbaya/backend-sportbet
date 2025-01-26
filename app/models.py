from . import db, bcrypt

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    score = db.Column(db.Integer, nullable=True, default=0)
    # wins = db.Column(db.Integer, nullable=True, default=0)
    # loses = db.Column(db.Integer, nullable=True, default=0)
    # draws = db.Column(db.Integer, nullable=True, default=0)
    # match_played = db.Column(db.Integer, nullable=True, default=0)
    paypal_link = db.Column(db.String, nullable=True)
    connected = db.Column(db.Boolean, default=False)  # Par défaut, l'utilisateur n'est pas connecté.

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email}, score={self.score}, connected={self.connected})>"