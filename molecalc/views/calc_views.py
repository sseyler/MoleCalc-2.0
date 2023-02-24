import flask
from flask import request, send_file

import io
import datetime
import hashlib
import logging
import re
import numpy as np

from rdkit import Chem
from rdkit.Chem import AllChem

from molecalc.infrastructure.view_modifiers import response
from molecalc.infrastructure.settings import SETTINGS
import molecalc.data.db_session as db_session
from molecalc.data.gamess_calculation import GamessCalculation
from molecalc.services.io_file_service import get_calc_io_file
from molecalc.services.iupac_name_service import smiles_to_iupac
from molecalc.lib import gamess

from ppqm import chembridge


_logger = logging.getLogger("molecalc:calc_views")

bp = flask.Blueprint('calc', __name__, template_folder='../templates')


@bp.route('/calculations_download/<string:hashkey>/<string:calc>/<string:iofile>',
          methods=['GET', 'POST'])
# @response(template_file='calculation/calculation.html')
def download_gamess_io(hashkey: str, calc: str, iofile: str):
    match calc:
        case 'opt':
            filename = f'optimization_{hashkey}.{iofile}'
        case 'vib':
            filename = f'vibrations_{hashkey}.{iofile}'
        case 'orb':
            filename = f'orbitals_{hashkey}.{iofile}'
        case _:
            err_msg = 'Unknown calculation type "{calc}"'
            _logger.error(err_msg)
            return {
                "error": "999",
                "message": f"Internal server error: {err_msg}",
            }

    f = get_calc_io_file(hashkey, calc, iofile)

    # return flask.Response(f,
    #     mimetype='text/plain',
    #     direct_passthrough=True,
    #     headers={'Content-disposition': f'attachment; filename={filename}'})

    return send_file(f,
                     mimetype='text/plain',
                     as_attachment=True,
                     download_name=filename)


@bp.route('/calculations')
@bp.route('/calculations/<string:hashkey>')
@response(template_file='calculation/calculation.html')
def calculation(hashkey: str):

    # Look up the key
    session = db_session.create_session()
    try:
        this_calculation = session.query(GamessCalculation) \
            .filter_by(hashkey=hashkey) \
            .first()
    finally:
        session.close()

    print(20 * '>')
    print('calculation: ', this_calculation)
    print('hashkey: ', hashkey)
    print(20 * '>')

    if this_calculation is None:
        raise flask.abort(404)
    if hashkey == "404":
        raise flask.abort(404)

    results = gamess.results.view_calculation(this_calculation)
    iupac_name = smiles_to_iupac(this_calculation.smiles).lower()

    data = dict({'iupac_name': iupac_name}, **results)
    return data


@bp.post('/ajax/_submit_quantum')
def ajax_submit_quantum():

    # print(20*'>')
    # print('request.method: ', request.method)
    # print('request.get_data(): ', request.get_data())
    # print('request.form: ', request.form)
    # print('request.values: ', request.values)
    # print(20 * '>')

    if 'sdf' not in request.form:
        return {
                "error": "Error 132 - sdf key error",
                "message": "Error. Missing information.",
            }

    if 'theory_level' not in request.form:
        return {
                "error": "Error XXX - theory level key error",
                "message": "Error. Missing information.",
            }

    # settings = request.registry.settings
    # TODO: Need replacement statement for obtaining (app?) settings for Flask

    # Check if user is someone who is a known misuser
    # user_ip = request.remote_addr
    # if (
    #     constants.COLUMN_BLOCK_IP in settings
    #     and user_ip in settings[constants.COLUMN_BLOCK_IP]
    # ):
    #     return {
    #         "error": "Error 194 - blocked ip",
    #         "message": "IP address has been blocked for misuse",
    #     }

    # if not request.POST:
    #     return {
    #         "error": "Error 128 - empty post",
    #         "message": "Error. Empty post.",
    #     }

    # Get coordinates from request
    sdfstr = request.form["sdf"].encode("utf-8")

    # Is this 2D or 3D?
    add_hydrogens = request.form.get("add_hydrogens", "1")
    add_hydrogens = add_hydrogens == "1"

    # Get theory level
    theory_level = request.form.get('theory_level', 'pm3')
    _logger.info(f'Selected theory level: "{theory_level}"')

    # TODO Use ChemSpider and RDKit/MolVS for chemical name things
    # Get IUPAC name (if available)
    iupac_name = request.form.get('iupac_name', 'N/A')
    _logger.info(f'IUPAC Name: "{iupac_name}"')

    # # Get SMILES name (if available)
    # smiles_name = request.form.get('smiles_name', 'N/A')
    # _logger.info(f'SMILES Name: "{smiles_name}"')

    # Get "trivial" name (if available)
    trivial_name = request.form.get('trivial_name', 'N/A')
    _logger.info(f'Trivial Name: "{trivial_name}"')

    # Get rdkit
    molobj, status = chembridge.sdfstr_to_molobj(sdfstr, return_status=True)

    if molobj is None:
        status = status.split("]")
        status = status[-1]
        status = re.sub(r"\# [0-9]+", "", status)
        return {"error": "Error 141 - rdkit error", "message": status}

    try:
        molobj.GetConformer()
    except ValueError:
        # Error
        return {
            "error": "Error 141 - rdkit error",
            "message": (
                "Error. Server was unable to generate "
                "conformations for this molecule"
            ),
        }

    # If hydrogens not added, assume graph and optimize with forcefield
    atoms = chembridge.molobj_to_atoms(molobj)

    if 1 not in atoms and add_hydrogens:
        molobj = Chem.AddHs(molobj)
        AllChem.EmbedMultipleConfs(molobj, numConfs=1)
        chembridge.molobj_optimize(molobj)

    atoms = chembridge.molobj_to_atoms(molobj)

    # TODO Check lengths of atoms
    # TODO Define max in settings
    max_atoms = 50
    (heavy_atoms,) = np.where(atoms != 1)
    if len(heavy_atoms) > max_atoms:
        return {
            "error": "Error 194 - max atoms error",
            "message": f"Stop Casper. Max {max_atoms} heavy atoms.",
        }

    # Fix sdfstr
    sdfstr = sdfstr.decode("utf8")
    for _ in range(3):
        i = sdfstr.index("\n")
        sdfstr = sdfstr[i+1:]
    sdfstr = "\n" * 3 + sdfstr

    # Inject numerical calculation parameters (e.g., "theory_level") in
    # the generated hashkey so the existence of a calculation depends not only
    # only on the input structure but also the selected numerical inputs
    # TODO CHECK THIS, SEAN --- this is probably causing that error with N#N
    calc_str = f'{sdfstr}\n{theory_level}'

    # hash on sdf (conformer)
    hshobj = hashlib.md5(calc_str.encode())
    hashkey = hshobj.hexdigest()

    # Check if hash/calculation already exists in data
    session = db_session.create_session()
    try:
        this_calculation = session.query(GamessCalculation) \
            .filter_by(hashkey=hashkey) \
            .first()
    finally:
        session.close()

    # If calculation already exists, return
    if this_calculation is not None:
        msg = {"hashkey": hashkey}
        this_calculation.created = datetime.datetime.now()
        _logger.info(f"{hashkey} exists")
        return msg

    # The calculation is valid and does not exist, pass to pipeline
    _logger.info(f"{hashkey} create")

    molecule_info = {"sdfstr": sdfstr, "molobj": molobj, "hashkey": hashkey}
    calc_settings = {'theory_level': theory_level}

    try:
        msg, new_calculation = gamess.pipelines.calculation_pipeline(
            molecule_info, calc_settings)
    except Exception:

        sdfstr = chembridge.molobj_to_sdfstr(molobj)
        _logger.error(f"{hashkey} PipelineError", exc_info=True)
        _logger.error(sdfstr)

        return {
            "error": "293",
            "message": "Internal server error. Uncaught exception",
        }

    print(20 * '>')
    print(new_calculation)
    print(20 * '>')

    # Add calculation to the database
    if new_calculation is not None:
        session = db_session.create_session()
        session.add(new_calculation)
        session.commit()
        session.close()

    return msg
