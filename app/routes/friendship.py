from flask import Blueprint, request, jsonify
from ..models import db, User, Friendship
from flask_jwt_extended import jwt_required, get_jwt_identity

friendship_bp = Blueprint('friendship', __name__)

# 📌 1️⃣ Recherche des utilisateurs pour les ajoueter en amis par le nom
@friendship_bp.route('/search-find', methods=['GET'])
@jwt_required()
def search_friend_by_name():
    name = request.args.get("name")  # Récupère le nom depuis la query string

    if not name:
        return jsonify({"error": "Name is required"}), 400

    # Recherche insensible à la casse des utilisateurs correspondant au nom
    friends = User.query.filter(User.username.ilike(f"%{name}%")).all()

    if not friends:
        return jsonify({"error": "No users found"}), 404

    # Formater la réponse
    result = [
        {"id": friend.id, "username": friend.username, "email": friend.email}
        for friend in friends
    ]

    return jsonify({"users": result}), 200



# 📌 1️⃣ Envoyer une demande d’ami
@friendship_bp.route('/add-friends', methods=['POST'])
@jwt_required()
def send_friend_request():
    data = request.get_json()
    friend_id = data.get("friend_id")

    if not friend_id:
        return jsonify({"error": "friend_id is required"}), 400

    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    friend = User.query.get(friend_id)

    if not friend:
        return jsonify({"error": "User not found"}), 404

    if user.is_friend(friend):
        return jsonify({"message": "You are already friends"}), 400

    if Friendship.query.filter_by(user_id=user_id, friend_id=friend_id).first():
        return jsonify({"message": "Friend request already sent"}), 400

    friendship = Friendship(user_id=user_id, friend_id=friend_id, status="pending")
    db.session.add(friendship)
    db.session.commit()

    return jsonify({"message": "Friend request sent"}), 201

# 📌 2️⃣ Accepter une demande d’ami
@friendship_bp.route('/accept', methods=['POST'])
@jwt_required()
def accept_friend_request():
    data = request.get_json()
    friend_id = data.get("friend_id")

    if not friend_id:
        return jsonify({"error": "friend_id is required"}), 400

    user_id = get_jwt_identity()
    friendship = Friendship.query.filter_by(user_id=friend_id, friend_id=user_id, status="pending").first()

    if not friendship:
        return jsonify({"error": "No pending friend request found"}), 404

    friendship.status = "accepted"
    db.session.commit()

    return jsonify({"message": "Friend request accepted"}), 200

# 📌 3️⃣ Refuser une demande d’ami
@friendship_bp.route('/decline', methods=['POST'])
@jwt_required()
def decline_friend_request():
    data = request.get_json()
    friend_id = data.get("friend_id")

    if not friend_id:
        return jsonify({"error": "friend_id is required"}), 400

    user_id = get_jwt_identity()
    friendship = Friendship.query.filter_by(user_id=friend_id, friend_id=user_id, status="pending").first()

    if not friendship:
        return jsonify({"error": "No pending friend request found"}), 404

    db.session.delete(friendship)
    db.session.commit()

    return jsonify({"message": "Friend request declined"}), 200

# 📌 4️⃣ Supprimer un ami
@friendship_bp.route('/remove', methods=['DELETE'])
@jwt_required()
def remove_friend():
    data = request.get_json()
    friend_id = data.get("friend_id")

    if not friend_id:
        return jsonify({"error": "friend_id is required"}), 400

    user_id = get_jwt_identity()
    friendship = Friendship.query.filter(
        ((Friendship.user_id == user_id) & (Friendship.friend_id == friend_id) & (Friendship.status == "accepted")) |
        ((Friendship.user_id == friend_id) & (Friendship.friend_id == user_id) & (Friendship.status == "accepted"))
    ).first()

    if not friendship:
        return jsonify({"error": "Friend not found"}), 404

    db.session.delete(friendship)
    db.session.commit()

    return jsonify({"message": "Friend removed"}), 200

# 📌 5️⃣ Lister les amis
@friendship_bp.route('/friends', methods=['GET'])
@jwt_required()
def list_friends():
    user_id = get_jwt_identity()
    
    friends = Friendship.query.filter(
        ((Friendship.user_id == user_id) | (Friendship.friend_id == user_id)) & (Friendship.status == "accepted")
    ).all()

    friend_list = []
    for friendship in friends:
        friend_id = friendship.friend_id if friendship.user_id == user_id else friendship.user_id
        friend = User.query.get(friend_id)
        friend_list.append({"id": friend.id, "username": friend.username})

    return jsonify(friend_list), 200

# 📌 6️⃣ Lister les demandes en attente
@friendship_bp.route('/friends/pending', methods=['GET'])
@jwt_required()
def list_pending_requests():
    user_id = get_jwt_identity()

    pending_requests = Friendship.query.filter_by(friend_id=user_id, status="pending").all()
    
    pending_list = [{"id": f.user_id, "username": User.query.get(f.user_id).username} for f in pending_requests]

    return jsonify(pending_list), 200
