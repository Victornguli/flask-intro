import os
from flask import Flask


def create_app(test_config = None):
	"""Flask app factory function"""
	app = Flask(__name__, instance_relative_config = True)
	app.config.from_mapping(
		SECRET_KEY = 'This is my secret key',
		DATABASE = os.path.join(app.instance_path, "flaskr.sqlite3")
	)
	if test_config is None:
		app.config.from_pyfile('config.py', silent = True)
	else:
		app.config.from_mapping(test_config)

	# Make sure that the app instance folder exists
	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	# @app.route("/")
	# def hello():
	# 	return 'Hello, World!'

	from . import db
	db.init_app(app)

	# Register app Blueprints
	from . import auth
	from . import blog
	app.register_blueprint(auth.bp)
	app.register_blueprint(blog.bp)
	app.add_url_rule('/', endpoint = 'index')
	return app

