from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, redirect, url_for, render_template, make_response, session, current_app
from .models import db, User, Bookmark
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity, set_access_cookies, unset_jwt_cookies
from flask_jwt_extended.exceptions import NoAuthorizationError
from werkzeug.security import generate_password_hash, check_password_hash
from . import jwt, scheduler
from apscheduler.triggers.interval import IntervalTrigger
from .scraper import get_manga_info

main = Blueprint('main', __name__)

@main.after_request
def request_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        return response

@main.errorhandler(NoAuthorizationError)
def handle_auth_error(e):
    resp = make_response(redirect(url_for('main.login')))
    unset_jwt_cookies(resp)
    return resp

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    session.clear()
    return render_template('login.html')

@main.context_processor
def inject_user():
    return {'logged_in': 'username' in session, 'username': session.get('username')}

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        new_user = User(username=request.form['username'], password=hashed_password, email=request.form['email'])
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password, request.form['password']):
            token = create_access_token(identity=user.id)
            resp = make_response(redirect(url_for('main.get_bookmarks')))
            set_access_cookies(resp, token)
            session['username'] = user.username
            return resp
        else:
            error = 'Invalid login credentials'
    return render_template('login.html', error=error)

@main.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    resp = make_response(redirect(url_for('main.login')))
    unset_jwt_cookies(resp)
    session.pop('username', None)
    return resp

@main.route('/add_bookmark', methods=['GET','POST'])
@jwt_required()
def add_bookmark():
    if request.method == 'GET':
        return render_template('add_bookmark.html')
    user_id = get_jwt_identity()
    data = request.form
    manga_info = get_manga_info(data['url'])
    if len(manga_info[0]) > 15:
        manga_info[0] = manga_info[0][:15] + '...'
    new_bookmark = Bookmark(user_id=user_id, url=data['url'], title=manga_info[0], image = manga_info[1], chapters_read=data['chapters_read'], latest_chapter = manga_info[2])
    db.session.add(new_bookmark)
    db.session.commit()
    return redirect(url_for('main.get_bookmarks'))

def update_bookmarks():
    with current_app.app_context():
        for bookmark in Bookmark.query.all():
            manga_info = get_manga_info(bookmark.url)
            bookmark.latest_chapter = manga_info[2]
        db.session.commit()

scheduler.add_job(
    func=update_bookmarks,
    trigger=IntervalTrigger(days=3),
    id='update_bookmarks',
    name='Update bookmarks every 3 days',
    replace_existing=True
)

@main.route('/bookmarks', methods=['GET'])
@jwt_required()
def get_bookmarks():
    user_id = get_jwt_identity()
    bookmarks = Bookmark.query.filter_by(user_id=user_id).all()
    return render_template('bookmarks.html', bookmarks=bookmarks)

@main.route("/delete_bookmark/<int:id>", methods=['POST'])
@jwt_required()
def delete_bookmark(id):
    user_id = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(id=id, user_id=user_id).first()
    db.session.delete(bookmark)
    db.session.commit()
    return redirect(url_for('main.get_bookmarks'))

@main.route("/account_info", methods=['GET'])
@jwt_required()
def account_info():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    return render_template('account_info.html', user=user)

@main.route("/change_username", methods=['POST'])
@jwt_required()
def change_username():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    user.username = request.form['new_username']
    db.session.commit()
    session.update({'username': user.username})
    return redirect(url_for('main.account_info'))

@main.route("/delete_account", methods=['POST'])
@jwt_required()
def delete_account():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    Bookmark.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    resp = make_response(redirect(url_for('main.index')))
    session.clear()
    unset_jwt_cookies(resp)
    return resp

@main.route('/')
def index():
    return render_template('index.html')