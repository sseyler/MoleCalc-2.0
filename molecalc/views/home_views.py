import flask

from molecalc.infrastructure.view_modifiers import response

bp = flask.Blueprint('editor', __name__, template_folder='../templates')


@bp.route('/')
@bp.route('/home')
@bp.route('/editor')
@response(template_file='home/editor.html')
def editor():
    return {}


@bp.route('/about')
@response(template_file="home/about.html")
def about():
    return {}


@bp.route('/help')
@response(template_file="home/help_page.html")
def help_page():
    return {}


@bp.route('/dark', methods=['POST'])
def dark():
    dark = flask.request.form['dark']
    flask.session['dark'] = dark
    
    # return 
    return flask.make_response(flask.jsonify({'dark': dark}, 200))
