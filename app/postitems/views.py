from flask import Blueprint, request, abort
from app.auth.helper import token_required
from app.postitems.helper import post_required, response, get_user_post, response_with_post_item, \
    response_with_pagination, get_paginated_items
from sqlalchemy import exc
from app.models import postItem

postitems = Blueprint('items', __name__)


@postitems.route('/postlists/<post_id>/items/', methods=['GET'])
@token_required
@post_required
def get_items(current_user, post_id):
    """
    A user`s items belonging to a post specified by the post_id are returned if the post Id
    is valid and belongs to the user.
    An empty item list is returned if the post has no items.
    :param current_user: User
    :param post_id: post Id
    :return: List of Items
    """
    # Get the user post
    post = get_user_post(current_user, post_id)
    if post is None:
        return response('failed', 'post not found', 404)

    # Get items in the post
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', None, type=str)
    items, nex, pagination, previous = get_paginated_items(post, post_id, page, q)

    # Make a list of items
    if items:
        result = []
        for item in items:
            result.append(item.json())
        return response_with_pagination(result, previous, nex, pagination.total)
    return response_with_pagination([], previous, nex, 0)


@postitems.route('/postlists/<post_id>/items/<item_id>/', methods=['GET'])
@token_required
@post_required
def get_item(current_user, post_id, item_id):
    """
    An item can be returned from the post if the item and post exist and below to the user.
    The post and Item Ids must be valid.
    :param current_user: User
    :param post_id: post Id
    :param item_id: Item Id
    :return:
    """
    # Check item id is an integer
    try:
        int(item_id)
    except ValueError:
        return response('failed', 'Provide a valid item Id', 202)

    # Get the user post
    post = get_user_post(current_user, post_id)
    if post is None:
        return response('failed', 'User has no post with Id ' + post_id, 404)

    # Delete the item from the post
    item = post.items.filter_by(id=item_id).first()
    if not item:
        abort(404)
    return response_with_post_item('success', item, 200)


@postitems.route('/postlists/<post_id>/items/', methods=['POST'])
@token_required
@post_required
def post(current_user, post_id):
    """
    Storing an item into a post
    :param current_user: User
    :param post_id: post Id
    :return: Http Response
    """
    if not request.content_type == 'application/json':
        return response('failed', 'Content-type must be application/json', 401)

    data = request.get_json()
    item_name = data.get('name')
    if not item_name:
        return response('failed', 'No name or value attribute found', 401)

    # Get the user post
    post = get_user_post(current_user, post_id)
    if post is None:
        return response('failed', 'User has no post with Id ' + post_id, 202)

    # Save the post Item into the Database
    item = postItem(item_name.lower(), data.get('description', None), post.id)
    item.save()
    return response_with_post_item('success', item, 200)


@postitems.route('/postlists/<post_id>/items/<item_id>/', methods=['PUT'])
@token_required
@post_required
def edit_item(current_user, post_id, item_id):
    """
    Edit an item with a valid Id. The request content-type must be json and also the post
    in which the item belongs must be among the user`s posts.
    The name of the item must be present in the payload but the description is optional.
    :param current_user: User
    :param post_id: post Id
    :param item_id: Item Id
    :return: Response of Edit Item
    """
    if not request.content_type == 'application/json':
        return response('failed', 'Content-type must be application/json', 401)

    try:
        int(item_id)
    except ValueError:
        return response('failed', 'Provide a valid item Id', 202)

    # Get the user post
    post = get_user_post(current_user, post_id)
    if post is None:
        return response('failed', 'User has no post with Id ' + post_id, 202)

    # Get the item
    item = post.items.filter_by(id=item_id).first()
    if not item:
        abort(404)

    # Check for Json data
    request_json_data = request.get_json()
    item_new_name = request_json_data.get('name')
    item_new_description = request_json_data.get('description', None)

    if not request_json_data:
        return response('failed', 'No attributes specified in the request', 401)

    if not item_new_name:
        return response('failed', 'No name or value attribute found', 401)

    # Update the item record
    item.update(item_new_name, item_new_description)
    return response_with_post_item('success', item, 200)


@postitems.route('/postlists/<post_id>/items/<item_id>/', methods=['DELETE'])
@token_required
@post_required
def delete(current_user, post_id, item_id):
    """
    Delete an item from the user's post.
    :param current_user: User
    :param post_id: post Id
    :param item_id: Item Id
    :return: Http Response
    """
    # Check item id is an integer
    try:
        int(item_id)
    except ValueError:
        return response('failed', 'Provide a valid item Id', 202)

    # Get the user post
    post = get_user_post(current_user, post_id)
    if post is None:
        return response('failed', 'User has no post with Id ' + post_id, 202)

    # Delete the item from the post
    item = post.items.filter_by(id=item_id).first()
    if not item:
        abort(404)
    item.delete()
    return response('success', 'Successfully deleted the item from post with Id ' + post_id, 200)


@postitems.errorhandler(404)
def item_not_found(e):
    """
    Custom response to 404 errors.
    :param e:
    :return:
    """
    return response('failed', 'Item not found', 404)


@postitems.errorhandler(400)
def bad_method(e):
    """
    Custom response to 400 errors.
    :param e:
    :return:
    """
    return response('failed', 'Bad request', 400)
