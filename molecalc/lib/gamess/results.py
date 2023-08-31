import pathlib

import numpy as np

from ppqm import misc, units
from ase.io import read

from molecalc.services.iupac_name_service import smiles_to_iupac
from molecalc.infrastructure.settings import SETTINGS


def view_calculation(calculation):
    """

    arg:
        calculation - SQLAlchemy GamessCalculation

    return:
        data - dict of information needed for the view template

    """

    # enthalpy = Column(Float)
    # charges = Column(String)
    #
    # islinear = Column(String)
    # vibjsmol = Column(String)
    # vibfreq = Column(String)
    # vibintens = Column(String)
    #
    # thermo = Column(String)
    #
    # orbitals = Column(String)
    # orbitalstxt = Column(String)
    #
    # soltotal = Column(Float)
    # solpolar = Column(Float)
    # solnonpolar = Column(Float)
    # solsurface = Column(Float)
    # soldipole = Column(String)
    # soldipoletotal = Column(Float)

    # Get hashdir from scratch
    scratch_dir = pathlib.Path(SETTINGS['molecalc.scr'])
    hashdir = scratch_dir / calculation.hashkey

    # Convert model to dictionary
    data = calculation.__dict__

    # Molecule and calculation info (displayed at top of calculation page)
    # TODO Make service to format theorylvl (b/c may have both upper/lowercase)
    if calculation.name is None:
        data['iupac_name'] = smiles_to_iupac(calculation.smiles)
    else:
        data['iupac_name'] = calculation.name
    data['theorylvl'] = calculation.theorylvl.upper()

    fmt = "{:.2f}"

    # Thermochemistry
    #               E         H         G         CV        CP        S
    #            KJ/MOL    KJ/MOL    KJ/MOL   J/MOL-K   J/MOL-K   J/MOL-K
    #  ELEC.      0.000     0.000     0.000     0.000     0.000     0.000
    #  TRANS.     3.718     6.197   -36.542    12.472    20.786   143.348
    #  ROT.       3.718     3.718   -15.045    12.472    12.472    62.932
    #  VIB.     119.279   119.279   119.164     2.252     2.252     0.385
    #  TOTAL    126.716   129.194    67.577    27.195    35.509   206.665
    #  VIB. THERMAL CORRECTION E(T)-E(0) = H(T)-H(0) =        99.870 J/MOL

    thermotable = calculation.thermo
    thermotable = misc.load_array(thermotable)

    data["h_elect"] = fmt.format(thermotable[0, 1])
    data["h_trans"] = fmt.format(thermotable[1, 1])
    data["h_rotat"] = fmt.format(thermotable[2, 1])
    data["h_vibra"] = fmt.format(thermotable[3, 1])
    data["h_total"] = fmt.format(thermotable[4, 1])

    data["cv_elect"] = fmt.format(thermotable[0, 3])
    data["cv_trans"] = fmt.format(thermotable[1, 3])
    data["cv_rotat"] = fmt.format(thermotable[2, 3])
    data["cv_vibra"] = fmt.format(thermotable[3, 3])
    data["cv_total"] = fmt.format(thermotable[4, 3])

    data["cp_elect"] = fmt.format(thermotable[0, 4])
    data["cp_trans"] = fmt.format(thermotable[1, 4])
    data["cp_rotat"] = fmt.format(thermotable[2, 4])
    data["cp_vibra"] = fmt.format(thermotable[3, 4])
    data["cp_total"] = fmt.format(thermotable[4, 4])

    data["s_elect"] = fmt.format(thermotable[0, 5])
    data["s_trans"] = fmt.format(thermotable[1, 5])
    data["s_rotat"] = fmt.format(thermotable[2, 5])
    data["s_vibra"] = fmt.format(thermotable[3, 5])
    data["s_total"] = fmt.format(thermotable[4, 5])

    # DASGSDKLGHSDLGHSDGH
    ag = read(f'{hashdir}/{calculation.hashkey}.sdf')
    molar_mass = np.sum(ag.get_masses())
    cp_total = float(data["cp_total"])
    cv_total = float(data["cv_total"])
    adiabatic_index = cp_total/cv_total
    sound_speed = np.sqrt(adiabatic_index * 8.31446261815324 * 298.15 / (1e-3 * molar_mass))

    data["enthalpy"] = fmt.format(data["enthalpy"] * units.calories_to_joule)
    data["sound_speed"] = fmt.format(sound_speed)
    data["adiabatic_index"] = fmt.format(adiabatic_index)

    print(ag.get_masses())
    print(molar_mass)
    print(sound_speed)

    # Molecular orbitals format
    data["orbitals"] = misc.load_array(data["orbitals"])
    data["orbitals"] *= units.hartree_to_ev
    data["orbitals"] = [fmt.format(x) for x in data["orbitals"]]

    # Vibrational Frequencies format
    data["vibfreq"] = misc.load_array(data["vibfreq"])
    islinear = int(data["islinear"]) == int(1)
    offset = 5 if islinear else 6
    data["vibfreq"] = data["vibfreq"][offset:]
    data["vibfreq"] = [fmt.format(x) for x in data["vibfreq"]]
    data["viboffset"] = offset

    # Solvation calculations
    if data["charges"] is None:
        data["has_solvation"] = False

    else:
        data["has_solvation"] = True

        dipoles = misc.load_array(data["soldipole"])

        data["dipolex"] = dipoles[0]
        data["dipoley"] = dipoles[1]
        data["dipolez"] = dipoles[2]

        data["soltotal"] = fmt.format(
            data["soltotal"] * units.calories_to_joule
        )
        data["solpolar"] = fmt.format(
            data["solpolar"] * units.calories_to_joule
        )
        data["solnonpolar"] = fmt.format(
            data["solnonpolar"] * units.calories_to_joule
        )
        data["solsurface"] = fmt.format(data["solsurface"])
        data["soldipoletotal"] = fmt.format(data["soldipoletotal"])

        charges = misc.load_array(data["charges"])
        charges = np.array(charges)
        charge = np.sum(charges)
        charge = np.round(charge, decimals=0)

        data["charge"] = int(charge)

    return data
