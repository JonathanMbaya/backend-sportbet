from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config  # Assurez-vous que le fichier config.py est au bon endroit

# Initialisation des extensions
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)

    # Charger la configuration
    app.config.from_object(Config)

    # Configuration de CORS (autorise React sur le port 3000)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Initialisation des extensions
    db.init_app(app)
    migrate.init_app(app, db)  # Initialiser Migrate avec app et db
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Importation et enregistrement des blueprints
    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Importation et enregistrement des blueprints
    from .routes.competition import competition_bp
    app.register_blueprint(competition_bp, url_prefix='/competition')

    from .routes.friendship import friendship_bp
    app.register_blueprint(friendship_bp, url_prefix='/friendship')


    # Route racine pour vérifier que l'API fonctionne
    @app.route('/')
    def index():
        return "Bienvenue sur l'API Flask, tout fonctionne correctement !", 200

    # Crée les tables dans la base de données si elles n'existent pas
    with app.app_context():
        db.create_all()

    return app
