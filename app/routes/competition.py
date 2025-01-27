from flask import Blueprint, request, jsonify
from app.models import db, Competition, User
import logging
from flask_jwt_extended import jwt_required, get_jwt_identity

# Blueprint pour les compétitions
competition_bp = Blueprint('competition', __name__)

# Route pour créer une compétition
@competition_bp.route('/create', methods=['POST'])
@jwt_required()
def create_competition():
    """
    Route pour créer une nouvelle compétition.
    """
    data = request.get_json()

    # Récupérer l'utilisateur connecté à partir du JWT
    user_id = get_jwt_identity()

    # Log des données reçues
    logging.info(f"Données reçues : {data}")

    # Vérification des champs obligatoires
    required_fields = ['name', 'min_participants', 'duration_days']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({'error': f"Champs manquants : {', '.join(missing_fields)}"}), 400

    # Validation des valeurs
    try:
        min_participants = int(data['min_participants'])
        duration_days = int(data['duration_days'])

        if min_participants <= 0:
            return jsonify({'error': "Le nombre minimum de participants doit être supérieur à 0."}), 400
        if duration_days <= 0:
            return jsonify({'error': "La durée de la compétition doit être supérieure à 0 jour."}), 400
        if min_participants > 10 or min_participants < 2:
            return jsonify({'error': "Le nombre de participants doit être entre 2 et 10."}), 400
    except ValueError:
        return jsonify({'error': "Les champs min_participants et duration_days doivent contenir des nombres entiers."}), 400

    # Création de la compétition
    try:
        competition = Competition(
            name=data['name'],
            min_participants=min_participants,
            duration_days=duration_days,
            owner_id=user_id
        )
        competition.set_end_date()
        db.session.add(competition)
        db.session.commit()

        return jsonify({
            'message': 'Compétition créée avec succès.',
            'competition': {
                'id': competition.id,
                'name': competition.name,
                'min_participants': competition.min_participants,
                'duration_days': competition.duration_days,
                'ends_at': competition.ends_at.strftime('%Y-%m-%d %H:%M:%S'),
                'status': competition.status,
                'owner_id': competition.owner_id
            }
        }), 201

    except Exception as e:
        logging.error(f"Erreur lors de la création : {str(e)}")
        return jsonify({'error': "Erreur lors de la création de la compétition. Veuillez réessayer."}), 500
    

# Récupérer les compétitions auxquelles un utilisateur participe et qu'il a créées
@competition_bp.route('/mycompetition-user', methods=['GET'])
@jwt_required()  # Protéger la route avec le token JWT
def get_user_competitions():
    try:
        # Récupérer l'ID de l'utilisateur à partir du token JWT
        user_id = get_jwt_identity()

        # Charger l'utilisateur depuis la base de données
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404

        # Récupérer les compétitions auxquelles l'utilisateur participe via UserCompetition
        user_competitions = [uc.competition for uc in user.competitions]

        # Récupérer les compétitions créées par l'utilisateur
        created_competitions = Competition.query.filter_by(owner_id=user_id).all()

        # Combiner les deux listes de compétitions
        all_competitions = user_competitions + created_competitions

        # Retourner la liste des compétitions sous format JSON
        return jsonify({
            'competitions': [
                {
                    'id': competition.id,
                    'name': competition.name,
                    'max_participants': competition.max_participants,
                    'min_participants': competition.min_participants,
                    'duration_days': competition.duration_days,
                    'status': competition.status,
                    'ends_at': competition.ends_at.strftime('%Y-%m-%d %H:%M:%S') if competition.ends_at else None
                }
                for competition in all_competitions
            ]
        }), 200

    except Exception as e:
        print(str(e))  # Optionnel : pour déboguer
        return jsonify({'error': 'Une erreur est survenue lors de la récupération des compétitions.'}), 500





# Route pour supprimer une compétition
@competition_bp.route('/delete/<int:competition_id>', methods=['DELETE'])
def delete_competition(competition_id):
    """
    Route pour supprimer une compétition.
    - competition_id: ID de la compétition à supprimer (dans l'URL)
    """
    try:
        # Récupérer la compétition par ID
        competition = Competition.query.get(competition_id)
        if not competition:
            return jsonify({'error': 'Compétition introuvable.'}), 404

        # Supprimer la compétition
        db.session.delete(competition)
        db.session.commit()

        return jsonify({'message': f'Compétition avec ID {competition_id} supprimée avec succès.'}), 200

    except Exception as e:
        return jsonify({'error': f"Erreur lors de la suppression de la compétition : {str(e)}"}), 500
