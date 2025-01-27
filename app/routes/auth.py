from flask import Blueprint, request, jsonify
from .. import db
from ..models import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Vérifier que les champs nécessaires sont dans la requête
    if not data.get('username') or not data.get('password'):
        raise BadRequest('Missing fields')

    # Vérifier si l'username ou l'email existent déjà
    existing_user = User.query.filter_by(username=data['username']).first()
    if existing_user:
        raise BadRequest('Username already taken')

    # Créer un nouvel utilisateur
    user = User(username=data['username'])
    user.set_password(data['password'])  # Hachage du mot de passe

    db.session.add(user)
    db.session.commit()


    return jsonify({"message": "User created successfully", "user": {

        "id": user.id,
        "username": user.username

    }}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    # Récupérer les données envoyées dans la requête
    username = request.json.get('username')
    password = request.json.get('password')

    # Valider les entrées
    if not username or not password:
        return jsonify({"error": "Username or password missing"}), 400

    # Rechercher l'utilisateur dans la base de données
    user = User.query.filter_by(username=username).first()
    # user.connected = True

    # Vérifier si l'utilisateur existe et si le mot de passe est correct
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    # Si tout va bien, créez un jeton ou gérez la connexion
    access_token = create_access_token(identity=user.id)

    # Préparer les données utilisateur pour la réponse
    user = {
        "id": user.id,
        "username": user.username,
        "score": user.score,
        "wins": user.wins,
        "loses": user.loses,
        "draws": user.draws,
        "match_played": user.match_played,
        "paypal_link": user.paypal_link,
        "connected": user.connected,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }

    return jsonify({"user": user, "access_token": access_token}), 200 

@auth_bp.route('/me', methods=['GET'])
@jwt_required()  # Nécessite un token valide
def get_current_user():
    # Récupère l'identifiant de l'utilisateur à partir du token JWT
    user_id = get_jwt_identity()

    # Recherche l'utilisateur dans la base de données
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "Utilisateur non trouvé"}), 404

    # Retourne les informations de l'utilisateur
    return jsonify({
        "user": {
            "id": user.id,
            "username": user.username,
            "score": user.score,
            "wins": user.wins,
            "loses": user.loses,
            "draws": user.draws,
            "match_played": user.match_played,
            "paypal_link": user.paypal_link,
            "connected": user.connected,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
    }), 200