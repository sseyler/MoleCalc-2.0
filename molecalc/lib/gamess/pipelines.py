import datetime
import logging
import pathlib

import numpy as np

from molecalc.data.gamess_calculation import GamessCalculation
from molecalc.data.__misc import Counter
from molecalc.lib import gamess
from ppqm import chembridge, misc
from ppqm.constants import COLUMN_COORDINATES, COLUMN_ENERGY

_logger = logging.getLogger("molecalc:pipe")


def calculation_pipeline(molinfo, calc_settings, settings):
    """

    Assumed that rdkit understands the molecule

    args:
        molinfo - dict
        settings -

    """

    # Read input
    molobj = molinfo["molobj"]
    sdfstr = molinfo["sdfstr"]
    hashkey = molinfo["hashkey"]
    theory_level = calc_settings['theory_level']

    scratch_dir = settings["scr.scr"]
    scratch_dir = pathlib.Path(scratch_dir)

    # TODO Get molecule names

    # Get that smile on your face
    try:
        smiles = chembridge.molobj_to_smiles(molobj, remove_hs=True)
    except Exception:
        smiles = chembridge.molobj_to_smiles(molobj)

    # Start respond message
    msg = {"smiles": smiles, "hashkey": hashkey}

    atoms = chembridge.molobj_to_atoms(molobj)
    _logger.info(f"{hashkey} '{smiles}' {atoms}")

    # Create new calculation
    calculation = GamessCalculation()

    # Switch to scrdir / hashkey
    hashdir = scratch_dir / hashkey
    hashdir.mkdir(parents=True, exist_ok=True)

    gamess_options = {
        "cmd": settings["gamess.rungms"],
        "gamess_scr": settings["gamess.scr"],
        "gamess_userscr": settings["gamess.userscr"],
        "scr": hashdir,
        "filename": hashkey,
        'theory_level': theory_level
    }

    # TODO Add error messages when gamess fails
    # TODO add timeouts for all gamess calls

    # Optimize molecule
    n_atoms = len(atoms)
    if n_atoms >= 2:
        try:
            properties = gamess.calculators.optimize_coordinates(
                molobj, gamess_options
            )
        except Exception:
            # TODO Logger + rich should store these exceptions somewhere. One file
            # per exception for easy debugging.
            # TODO Should store SDF of the molecule if exception
            sdfstr = chembridge.molobj_to_sdfstr(molobj)
            _logger.error(f"{hashkey} OptimizationError", exc_info=True)
            _logger.error(sdfstr)
            properties = None
    elif n_atoms == 1:
        properties = {
            COLUMN_COORDINATES: chembridge.molobj_to_coordinates(molobj),
            COLUMN_ENERGY: 0.0
        }
    else:
        return {
            "error": "Error - misc atom count error",
            "message": "Error. There is not at least one atom.",
        }, None

    if properties is None:
        return {
            "error": "Error g-80 - gamess optimization error",
            "message": "Optimization Error: properties is None",
        }, None

    if "error" in properties:
        return {
            "error": "Error g-93 - gamess optimization error known",
            "message": properties["error"],
        }, None

    if (
        COLUMN_COORDINATES not in properties
        or properties[COLUMN_COORDINATES] is None
    ):
        return {
            "error": "Error g-104 - gamess optimization error",
            "message": "Optimization Error: no coordinates found in properties",
        }, None

    _logger.info(f"{hashkey} OptimizationSuccess")

    # Save and set coordinates
    coord = properties[COLUMN_COORDINATES]
    calculation.coordinates = misc.save_array(coord)
    calculation.enthalpy = properties[COLUMN_ENERGY]
    chembridge.molobj_set_coordinates(molobj, coord)

    # Optimization is finished, do other calculation async-like
    (
        properties_vib,
        properties_orb,
        # properties_sol,
    ) = gamess.calculators.calculate_all_properties(molobj, gamess_options)


    # Check results

    # Vibrational Modes
    # print(80*'=')
    # print(properties_vib)
    # print(80*'=')
    # if n_atoms == 1:
    #     properties_vib["linear"] = True
    #     properties_vib["jsmol"] = ''
    #     properties_vib["freq"] = np.zeros(6)
    #     properties_vib["intens"] = np.zeros(6)
    #     properties_vib["thermo"] = np.zeros((5, 6))
    #     properties_vib["thermo"][0,:] = -1.0
    #     properties_vib["thermo"][1,:] = -1.0
    #     properties_vib["thermo"][4,:] = -1.0

    if properties_vib is None or "error" in properties_vib:
        return {
            "error": "Error g-104 - gamess vibration error",
            "message": "Error. Unable to vibrate molecule",
        }, None

    _logger.info(f"{hashkey} VibrationSuccess")

    # TODO Make a custom reader and move this out of ppqm
    calculation.islinear = properties_vib["linear"]
    calculation.vibjsmol = properties_vib["jsmol"]
    calculation.vibfreq = misc.save_array(properties_vib["freq"])
    calculation.vibintens = misc.save_array(properties_vib["intens"])
    calculation.thermo = misc.save_array(properties_vib["thermo"])

    # Molecular Orbitals
    if properties_orb is None or "error" in properties_orb:
        return {
            "error": "Error g-128 - gamess orbital error",
            "message": "Error. Unable to calculate molecular orbitals",
        }, None

    _logger.info(f"{hashkey} OrbitalsSuccess")
    calculation.orbitals = misc.save_array(properties_orb["orbitals"])
    calculation.orbitalstxt = properties_orb["stdout"]

    # Solvation and Polarity
    # if properties_sol is None or "error" in properties_sol:
    #
    #     # Is okay solvation didn't converge, just warn.
    #     _logger.warning(f"{hashkey} SolvationError")
    #
    # else:
    #     # 'charges', 'solvation_total', 'solvation_polar',
    #     # 'solvation_nonpolar', 'surface', 'total_charge', 'dipole',
    #     # 'dipole_total'
    #     _logger.info(f"{hashkey} SolvationSuccess")
    #
    #     charges = properties_sol["charges"]
    #     calculation.charges = misc.save_array(charges)
    #     calculation.soltotal = properties_sol["solvation_total"]
    #     calculation.solpolar = properties_sol["solvation_polar"]
    #     calculation.solnonpolar = properties_sol["solvation_nonpolar"]
    #     calculation.solsurface = properties_sol["surface"]
    #     calculation.soldipole = misc.save_array(properties_sol["dipole"])
    #     calculation.soldipoletotal = properties_sol["dipole_total"]
    #
    #     # Save mol2 fmt
    #     mol2 = chembridge.molobj_to_mol2(molobj, charges=charges)
    #     calculation.mol2 = mol2

    # Saveable sdf and reset title
    sdfstr = chembridge.molobj_to_sdfstr(molobj)
    sdfstr = chembridge.clean_sdf_header(sdfstr)

    # Get a 2D Picture
    svgstr = chembridge.molobj_to_svgstr(molobj, removeHs=True, use_2d=True)

    # Success, store results database
    calculation.smiles = smiles
    calculation.hashkey = hashkey
    calculation.sdf = sdfstr
    calculation.svg = svgstr
    calculation.theorylvl = theory_level
    calculation.created = datetime.datetime.now()

    return msg, calculation


def update_smiles_counter(request, smiles):

    # Add smiles to counter
    countobj = (
        request.dbsession.query(Counter)
        .filter_by(smiles=smiles)
        .first()
    )

    if countobj is None:
        counter = Counter()
        counter.smiles = smiles
        counter.count = 1
        request.dbsession.add(counter)
    else:
        countobj.count += 1

    return
