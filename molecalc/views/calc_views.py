import flask

from molecalc.infrastructure.view_modifiers import response
# from molecalc_lib import gamess_results
# import models

bp = flask.Blueprint('calc', __name__, template_folder='../templates')


# TODO: This view function *appears* to be used to access calculations through
#   a URL that looks like "https://molecalc.cloud/calculations/<hashkey>", so
#   Flask can be used to add a *variable* section to the URL with
#   "/the/base/url/<variable_name>".
@bp.route('/calculation/<string:hashkey>')
@response(template_file='calculation/calculation.html')
def calculation(hashkey: str):
    # hashkey = request.matchdict["one"]  # Get the hashkey
    #
    # print(request.matchdict)
    #
    # # Look up the key
    # calculation = (
    #     request.dbsession.query(models.GamessCalculation)
    #     .filter_by(hashkey=hashkey)
    #     .first()
    # )
    #
    # if calculation is None:
    #     raise httpexceptions.exception_response(404)
    #
    # if hashkey == "404":
    #     raise httpexceptions.exception_response(404)
    #
    # return gamess_results.view_gamess_calculation(calculation)

    return {}
