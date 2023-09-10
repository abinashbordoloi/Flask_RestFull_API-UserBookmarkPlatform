from flask import Blueprint, request
from flask.json import jsonify
import validators
from src.database import Bookmark, db
from flask_jwt_extended import get_jwt_identity, jwt_required


bookmarks = Blueprint("bookmarks", __name__, url_prefix="/api/v1/bookmarks")



# for creating a new bookmark and getting all bookmarks of a user that is logged in
@bookmarks.route('/', methods=['POST', 'GET'])
@jwt_required()
def handle_bookmarks():
    current_user = get_jwt_identity()
    if request.method == 'POST':
        body = request.get_json().get('body', '')
        url = request.get_json().get('url', '')

        if not validators.url(url):
            return jsonify({'error': 'Invalid URL'})

        if Bookmark.query.filter_by(url=url).first():
            return jsonify({'error': 'URL already exists!'})

        bookmark = Bookmark(url=url, body=body, user_id=current_user)
        db.session.add(bookmark)
        db.session.commit()
        return jsonify({'Message': 'bookmark created',
                        'Details': {'id': bookmark.id, 'url': bookmark.url, 'short_url': bookmark.short_url,
                                    'visits': bookmark.visits, 'body': bookmark.body, 'created_at': bookmark.created_at, 'updated_at': bookmark.updated_at}})

    else:
        bookmarks = Bookmark.query.filter_by(user_id=current_user)

        data = []
        for bookmark in bookmarks:
            data.append({'id': bookmark.id, 'url': bookmark.url, 'sort_url': bookmark.short_url, 'visits': bookmark.visits,
                        'body': bookmark.body, 'created_at': bookmark.created_at, 'updated_at': bookmark.updated_at})


        return jsonify({'bookmarks': data})