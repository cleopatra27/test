from flask import make_response, jsonify, url_for
from app import app
from app.models import post


def response_for_user_post(user_post):
    """
    Return the response for when a single post when requested by the user.
    :param user_post:
    :return:
    """
    return make_response(jsonify({
        'status': 'success',
        'post': user_post
    }))


def response_for_created_post(user_post, status_code):
    """
    Method returning the response when a post has been successfully created.
    :param status_code:
    :param user_post: post
    :return: Http Response
    """
    return make_response(jsonify({
        'status': 'success',
        'id': user_post.id,
        'name': user_post.name,
        'createdAt': user_post.create_at,
        'modifiedAt': user_post.modified_at
    })), status_code


def response(status, message, code):
    """
    Helper method to make a http response
    :param status: Status message
    :param message: Response message
    :param code: Response status code
    :return: Http Response
    """
    return make_response(jsonify({
        'status': status,
        'message': message
    })), code


def get_user_post_json_list(user_posts):
    """
    Make json objects of the user posts and add them to a list.
    :param user_posts: post
    :return:
    """
    posts = []
    for user_post in user_posts:
        posts.append(user_post.json())
    return posts


def response_with_pagination(posts, previous, nex, count):
    """
    Make a http response for postList get requests.
    :param count: Pagination Total
    :param nex: Next page Url if it exists
    :param previous: Previous page Url if it exists
    :param posts: post
    :return: Http Json response
    """
    return make_response(jsonify({
        'status': 'success',
        'previous': previous,
        'next': nex,
        'count': count,
        'posts': posts
    })), 200


def paginate_posts(user_id, page, q, user):
    """
    Get a user by Id, then get hold of their posts and also paginate the results.
    There is also an option to search for a post name if the query param is set.
    Generate previous and next pagination urls
    :param q: Query parameter
    :param user_id: User Id
    :param user: Current User
    :param page: Page number
    :return: Pagination next url, previous url and the user posts.
    """
    if q:
        pagination = post.query.filter(post.name.like("%" + q.lower().strip() + "%")).filter_by(user_id=user_id) \
            .paginate(page=page, per_page=app.config['post_AND_ITEMS_PER_PAGE'], error_out=False)
    else:
        pagination = user.posts.paginate(page=page, per_page=app.config['post_AND_ITEMS_PER_PAGE'],
                                           error_out=False)
    previous = None
    if pagination.has_prev:
        if q:
            previous = url_for('post.postlist', q=q, page=page - 1, _external=True)
        else:
            previous = url_for('post.postlist', page=page - 1, _external=True)
    nex = None
    if pagination.has_next:
        if q:
            nex = url_for('post.postlist', q=q, page=page + 1, _external=True)
        else:
            nex = url_for('post.postlist', page=page + 1, _external=True)
    items = pagination.items
    return items, nex, pagination, previous
