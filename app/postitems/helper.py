from flask import jsonify, make_response, request, url_for
from app import app
from functools import wraps
from app.models import User, postItem


def post_required(f):
    """
    Decorator to ensure that a valid post id is sent in the url path parameters
    :param f:
    :return:
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        post_id_ = request.view_args['post_id']
        try:
            int(post_id_)
        except ValueError:
            return response('failed', 'Provide a valid post Id', 401)
        return f(*args, **kwargs)

    return decorated_function


def response(status, message, status_code):
    """
    Make an http response helper
    :param status: Status message
    :param message: Response Message
    :param status_code: Http response code
    :return:
    """
    return make_response(jsonify({
        'status': status,
        'message': message
    })), status_code


def response_with_post_item(status, item, status_code):
    """
    Http response for response with a post item.
    :param status: Status Message
    :param item: postItem
    :param status_code: Http Status Code
    :return:
    """
    return make_response(jsonify({
        'status': status,
        'item': item.json()
    })), status_code


def response_with_pagination(items, previous, nex, count):
    """
    Get the post items with the result paginated
    :param items: Items within the post
    :param previous: Url to previous page if it exists
    :param nex: Url to next page if it exists
    :param count: Pagination total
    :return: Http Json response
    """
    return make_response(jsonify({
        'status': 'success',
        'previous': previous,
        'next': nex,
        'count': count,
        'items': items
    })), 200


def get_user_post(current_user, post_id):
    """
    Query the user to find and return the post specified by the post Id
    :param post_id: post Id
    :param current_user: User
    :return:
    """
    user_post = User.get_by_id(current_user.id).posts.filter_by(id=post_id).first()
    return user_post


def get_paginated_items(post, post_id, page, q):
    """
    Get the items from the post and then paginate the results.
    Items can also be search when the query parameter is set.
    Construct the previous and next urls.
    :param q: Query parameter
    :param post: post
    :param post_id: post Id
    :param page: Page number
    :return:
    """

    if q:
        pagination = postItem.query.filter(postItem.name.like("%" + q.lower().strip() + "%")) \
            .order_by(postItem.create_at.desc()) \
            .filter_by(post_id=post_id) \
            .paginate(page=page, per_page=app.config['post_AND_ITEMS_PER_PAGE'], error_out=False)
    else:
        pagination = post.items.order_by(postItem.create_at.desc()).paginate(page=page, per_page=app.config[
            'post_AND_ITEMS_PER_PAGE'], error_out=False)

    previous = None
    if pagination.has_prev:
        if q:
            previous = url_for('items.get_items', q=q, post_id=post_id, page=page - 1, _external=True)
        else:
            previous = url_for('items.get_items', post_id=post_id, page=page - 1, _external=True)
    nex = None
    if pagination.has_next:
        if q:
            nex = url_for('items.get_items', q=q, post_id=post_id, page=page + 1, _external=True)
        else:
            nex = url_for('items.get_items', post_id=post_id, page=page + 1, _external=True)
    return pagination.items, nex, pagination, previous
