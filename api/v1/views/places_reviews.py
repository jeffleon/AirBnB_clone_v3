#!/usr/bin/python3
""" Script to route the request """
from api.v1.views import app_views
from models.review import Review
from models import storage
from flask import jsonify, abort, request


@app_views.errorhandler(400)
def resource_bad_request(e):
    return jsonify({'error': str(e).replace('400 Bad Request: ', '')}), 400


@app_views.route('/places/<place_id>/reviews',
                 methods=['GET', 'POST'], strict_slashes=False)
def reviews(place_id):
    """ Count the whole information in the database
        with the newly added count()"""
    if request.method == 'GET':
        dictionary = storage.all(Review)
        result = []
        for key, value in dictionary.items():
            if value.to_dict()['place_id'] == place_id:
                result.append(value.to_dict())
        return jsonify(result), 201
    elif request.method == 'POST':
        print("entre al post")
        content = request.get_json(silent=True)
        if type(content) == dict:
            # is for valid if the pass is a json
            if 'text' not in content.keys():
                abort(400, "Missing text")
            if 'user_id' not in content.keys():
                abort(400, "Missing user_id")
            verify = storage.all(Review)
            checkplace = False
            checkuser = False
            for value in verify.values():
                if value.to_dict()['user_id'] == content['user_id']:
                    checkuser = True
                if value.to_dict()['place_id'] == place_id:
                    checkplace = True
                if checkplace and checkuser:
                    break
            print(checkuser, checkplace)
            if not checkuser or not checkplace:
                abort(404)
            dictionary = Review(**content)
            dictionary.save()
            # dictionary.save()
            return jsonify(dictionary.to_dict()), 201
        else:
            abort(400, "Not a JSON")
            # abort(400, description="fails cause yes")


@app_views.route('/reviews/<review_id>',
                 methods=['GET', 'DELETE', 'PUT'], strict_slashes=False)
def reviews_by_id(review_id):
    """ Count the whole information in the database
    with the newly added count()"""
    result = storage.get(Review, review_id)
    if not result:
        abort(404)

    if request.method == 'GET':
        return jsonify(result.to_dict())

    if request.method == 'DELETE':
        if result:
            result.delete()
            storage.save()
            return jsonify({})

    if request.method == 'PUT':
        contents = request.get_json(silent=True)
        if not request.json:
            abort(400, "Not a JSON")

        for key, value in contents.items():
            if key not in ('id', 'user_id',
                           'place_id', 'created_at', 'updated_at'):
                setattr(result, key, value)

        storage.save()
        return jsonify(result.to_dict()), 200
