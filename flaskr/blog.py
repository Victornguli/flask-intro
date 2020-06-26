from flask import (
	Blueprint, g, url_for, request, redirect, render_template, flash, Response
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
	db = get_db()
	posts = db.execute(
		"""
		SELECT p.id, title, body, created, author_id, username
		FROM post p JOIN user u WHERE p.author_id = u.id
		ORDER BY created DESC 
		"""
	).fetchall()
	return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
	if request.method == 'POST':
		title = request.form['title']
		body = request.form['body']
		error = None

		if not title:
			error = 'Title cannot be empty'
		if error is None:
			db = get_db()
			db.execute(
				"""
				INSERT INTO post (title, body, author_id)
				VALUES(?, ?, ?)
				""", (title, body, g.user['id'])
			)
			db.commit()
			return redirect(url_for('blog.index'))
		flash(error)

	return render_template('blog/create.html')


def get_post(post_id, check_author=True):
	post = get_db().execute(
		"""
		SELECT p.id, title, body, created, author_id, username
		FROM post p JOIN user u ON p.author_id = u.id
		WHERE p.id = ?
		""", (post_id,)
	).fetchone()
	if post is None:
		abort(404, "Post id {0} doesn't exist.".format(post_id))

	if check_author and post['author_id'] != g.user['id']:
		abort(403)

	return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
	post = get_post(id)
	if request.method == 'POST':
		title = request.form['title']
		body = request.form['body']
		error = None

		if not title:
			error = 'Title is required.'

		if error is not None:
			flash(error)
		else:
			db = get_db()
			db.execute(
				'UPDATE post SET title = ?, body = ?'
				'WHERE id = ?',
				(title, body, id)
			)
			db.commit()
			return redirect(url_for('blog.index'))
	return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
	get_post(id)
	db = get_db()
	db.execute(
		'DELETE FROM post WHERE id = ?', (id,)
	)
	db.commit()
	return redirect(url_for('blog.index'))


@bp.errorhandler(404)
def custom_404(error):
	return render_template('errors/404.html'), 404


@bp.errorhandler(403)
def custom_403(error):
	return render_template('errors/403.html'), 403
