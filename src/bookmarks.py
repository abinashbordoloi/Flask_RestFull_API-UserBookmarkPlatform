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
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)

        bookmarks = Bookmark.query.filter_by(
            user_id=current_user).paginate(page=page, per_page=per_page)

        data = []
        for bookmark in bookmarks.items:
            data.append({'id': bookmark.id, 'url': bookmark.url, 'sort_url': bookmark.short_url, 'visits': bookmark.visits,
                        'body': bookmark.body, 'created_at': bookmark.created_at, 'updated_at': bookmark.updated_at})

        meta = {
            'page': bookmarks.page,
            'pages': bookmarks.pages,
            'total_count': bookmarks.total,
            'prev_page': bookmarks.prev_num,
            'next_page': bookmarks.next_num,
            'has_next': bookmarks.has_next,
            'has_prev': bookmarks.has_prev




        }

        return jsonify({'bookmarks': data, "meta": meta})


# @bookmarks.get("/<int:id")
# @jwt_required()
# def get_bookmarks(id):
#     current_user = get_jwt_identity()
#     bookmark = Bookmark.query.filter_by(
#         id=id, user_id=current_user).first().firt()

#     if not bookmark:
#         return jsonify({'message': 'Bookmark not found'})

#     return jsonify({'id': bookmark.id, 'url': bookmark.url, 'short_url': bookmark.short_url, 'visits': bookmark.visits, 'body': bookmark.body, 'created_at': bookmark.created_at, 'updated_at': bookmark.updated_at})
