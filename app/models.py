from . import db, bcrypt
from datetime import datetime, timedelta



# Table d'association pour gérer les utilisateurs et les compétitions
class UserCompetition(db.Model):
    __tablename__ = 'user_competition'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id'), primary_key=True)
    score = db.Column(db.Integer, default=0)  # Score de l'utilisateur dans la compétition
    wins = db.Column(db.Integer, default=0)  # Victoires de l'utilisateur dans la compétition
    loses = db.Column(db.Integer, default=0)  # Défaites de l'utilisateur dans la compétition
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)  # Date d'entrée dans la compétition

    # Relations
    user = db.relationship("User", back_populates="competitions")
    competition = db.relationship("Competition", back_populates="participants")

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    score = db.Column(db.Integer, nullable=True, default=0)
    wins = db.Column(db.Integer, nullable=True, default=0)
    loses = db.Column(db.Integer, nullable=True, default=0)
    draws = db.Column(db.Integer, nullable=True, default=0)
    match_played = db.Column(db.Integer, nullable=True, default=0)
    paypal_link = db.Column(db.String, nullable=True)
    connected = db.Column(db.Boolean, default=False)  # Par défaut, l'utilisateur n'est pas connecté.
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Relation avec les compétitions via UserCompetition
    competitions = db.relationship("UserCompetition", back_populates="user")
    

    # Méthodes pour gérer les mots de passe
    def set_password(self, password):
        """Hash le mot de passe et le sauvegarde."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Vérifie si le mot de passe est correct."""
        return bcrypt.check_password_hash(self.password_hash, password)

    # Méthodes pour gérer les statistiques
    def increment_wins(self):
        """Incrémente les victoires et les matchs joués."""
        self.wins += 1
        self.match_played += 1
        db.session.commit()

    def increment_loses(self):
        """Incrémente les défaites et les matchs joués."""
        self.loses += 1
        self.match_played += 1
        db.session.commit()

    def increment_draws(self):
        """Incrémente les matchs nuls et les matchs joués."""
        self.draws += 1
        self.match_played += 1
        db.session.commit()

    def calculate_win_ratio(self):
        """Calcule le ratio de victoires."""
        if self.match_played == 0:
            return 0
        return round(self.wins / self.match_played, 2)

    # Méthodes de connexion/déconnexion
    def login_user(self):
        """Met à jour l'état connecté de l'utilisateur."""
        self.connected = True
        db.session.commit()

    def logout_user(self):
        """Met à jour l'état déconnecté de l'utilisateur."""
        self.connected = False
        db.session.commit()

    # Représentation
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, score={self.score}, connected={self.connected})>"
    


class Competition(db.Model):
    __tablename__ = 'competition'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Nom de la compétition
    max_participants = db.Column(db.Integer, nullable=False, default=10)  # Limite maximale des participants
    min_participants = db.Column(db.Integer, nullable=False)  # Limite minimale des participants
    duration_days = db.Column(db.Integer, nullable=False, default=7)  # Durée de la compétition en jours
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Date de création
    ends_at = db.Column(db.DateTime)  # Date de fin, calculée en fonction de la durée
    status = db.Column(db.String(20), nullable=False, default='en attente')  # Statut de la compétition (en attente, prêt, terminé)
    owner_id = db.Column(db.Integer, nullable=True)
    winner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Gagnant de la compétition (si terminé)


    # Relation avec les utilisateurs via UserCompetition
    participants = db.relationship("UserCompetition", back_populates="competition")


    # Méthode pour calculer la date de fin
    def set_end_date(self):
        """Calcule la date de fin de la compétition."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()  # Assurez-vous qu'une valeur existe
        self.ends_at = self.created_at + timedelta(days=self.duration_days)

    # Méthode pour mettre à jour le statut de la compétition
    def update_status(self):
        """Met à jour le statut de la compétition."""
        current_participants = len(self.participants)

        if self.status == 'En attente' and current_participants >= self.min_participants:
            self.status = 'Prêt'
        elif self.status in ['En attente', 'Prêt'] and datetime.utcnow() >= self.ends_at:
            self.status = 'Terminé'
            self.determine_winner()
        db.session.commit()

    # Méthode pour déterminer le gagnant
    def determine_winner(self):
        """Définit le gagnant de la compétition basé sur le score le plus élevé."""
        if not self.participants:
            return None

        # Trouver le participant avec le score le plus élevé
        top_participant = max(self.participants, key=lambda p: p.score)
        self.winner_id = top_participant.user_id
        db.session.commit()

    def __repr__(self):
        return (f"<Competition(id={self.id}, name={self.name}, status={self.status}, "
                f"max_participants={self.max_participants}, winner_id={self.winner_id})>")