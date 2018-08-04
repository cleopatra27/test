from flask import Blueprint, request, abort
from app.auth.helper import token_required
from app.post.helper import response, response_for_created_post, response_for_user_post, response_with_pagination, \
    get_user_post_json_list, paginate_posts
from app.models import User, post

# Initialize blueprint
post = Blueprint('post', __name__)


@post.route('/postlists/', methods=['GET'])
@token_required
def postlist(current_user):
    """
    Return all the posts owned by the user or limit them to 10.
    Return an empty posts object if user has no posts
    :param current_user:
    :return:
    """
    user = User.get_by_id(current_user.id)
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', None, type=str)

    items, nex, pagination, previous = paginate_posts(current_user.id, page, q, user)

    if items:
        return response_with_pagination(get_user_post_json_list(items), previous, nex, pagination.total)
    return response_with_pagination([], previous, nex, 0)


@post.route('/postlists/', methods=['POST'])
@token_required
def create_postlist(current_user):
    """
    Create a post from the sent json data.
    :param current_user: Current User
    :return:
    """
    if request.content_type == 'application/json':
        data = request.get_json()
        name = data.get('name')
        if name:
            user_post = post(name.lower(), current_user.id)
            user_post.save()
            return response_for_created_post(user_post, 201)
        return response('failed', 'Missing name attribute', 400)
    return response('failed', 'Content-type must be json', 202)


@post.route('/postlists/<post_id>', methods=['GET'])
@token_required
def get_post(current_user, post_id):
    """
    Return a user post with the supplied user Id.
    :param current_user: User
    :param post_id: post Id
    :return:
    """
    try:
        int(post_id)
    except ValueError:
        return response('failed', 'Please provide a valid post Id', 400)
    else:
        user_post = User.get_by_id(current_user.id).posts.filter_by(id=post_id).first()
        if user_post:
            return response_for_user_post(user_post.json())
        return response('failed', "post not found", 404)


@post.route('/postlists/<post_id>', methods=['PUT'])
@token_required
def edit_post(current_user, post_id):
    """
    Validate the post Id. Also check for the name attribute in the json payload.
    If the name exists update the post with the new name.
    :param current_user: Current User
    :param post_id: post Id
    :return: Http Json response
    """
    if request.content_type == 'application/json':
        data = request.get_json()
        name = data.get('name')
        if name:
            try:
                int(post_id)
            except ValueError:
                return response('failed', 'Please provide a valid post Id', 400)
            user_post = User.get_by_id(current_user.id).posts.filter_by(id=post_id).first()
            if user_post:
                user_post.update(name)
                return response_for_created_post(user_post, 201)
            return response('failed', 'The post with Id ' + post_id + ' does not exist', 404)
        return response('failed', 'No attribute or value was specified, nothing was changed', 400)
    return response('failed', 'Content-type must be json', 202)


@post.route('/postlists/<post_id>', methods=['DELETE'])
@token_required
def delete_post(current_user, post_id):
    """
    Deleting a User post from the database if it exists.
    :param current_user:
    :param post_id:
    :return:
    """
    try:
        int(post_id)
    except ValueError:
        return response('failed', 'Please provide a valid post Id', 400)
    user_post = User.get_by_id(current_user.id).posts.filter_by(id=post_id).first()
    if not user_post:
        abort(404)
    user_post.delete()
    return response('success', 'post Deleted successfully', 200)


@post.errorhandler(404)
def handle_404_error(e):
    """
    Return a custom message for 404 errors.
    :param e:
    :return:
    """
    return response('failed', 'post resource cannot be found', 404)


@post.errorhandler(400)
def handle_400_errors(e):
    """
    Return a custom response for 400 errors.
    :param e:
    :return:
    """
    return response('failed', 'Bad Request', 400)
