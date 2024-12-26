from flask import Blueprint, request, jsonify, make_response

bp = Blueprint('webfinger', __name__, url_prefix='/user/<username>/inbox')

@bp.route('', methods=['GET', 'POST'])
def inbox(username):
    return jsonify({'message': 'Hello, World!'})