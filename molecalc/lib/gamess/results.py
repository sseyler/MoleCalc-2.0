import pathlib

import numpy as np

from ppqm import misc, units
from ase.io import read

from molecalc.services.iupac_name_service import smiles_to_iupac
from molecalc.infrastructure.settings import SETTINGS

import pandas as pd
import json
import plotly
import plotly.express as px


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

    # ---------------------------------
    # Thermochemistry
    # ---------------------------------
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

    ag = read(f'{hashdir}/{calculation.hashkey}.sdf')
    molar_mass = np.sum(ag.get_masses())
    cp_total = float(data["cp_total"])
    cv_total = float(data["cv_total"])
    adiabatic_index = cp_total/cv_total
    sound_speed = np.sqrt(adiabatic_index * 8.31446261815324 * 298.15 / (1e-3 * molar_mass))

    data["enthalpy"] = fmt.format(data["enthalpy"] * units.calories_to_joule)
    data["sound_speed"] = fmt.format(sound_speed)
    data["adiabatic_index"] = fmt.format(adiabatic_index)
    # print(ag.get_masses())
    # print(molar_mass)
    # print(sound_speed)

    # ---------------------------------
    # Vibrational Frequencies format
    # ---------------------------------
    data["vibintens"] = misc.load_array(data["vibintens"])
    data["vibfreq"] = misc.load_array(data["vibfreq"])
    islinear = int(data["islinear"]) == int(1)
    offset = 5 if islinear else 6
    data["vibfreq"] = data["vibfreq"][offset:]
    data["vibfreq"] = [fmt.format(x) for x in data["vibfreq"]]
    data["viboffset"] = offset

    # IR Spectrum Plot
    #  MODE FREQ(CM**-1)  SYMMETRY  RED. MASS  IR INTENS.
    # 1       0.288    A       14.665479    0.000000
    # 2       0.253    A       14.665052    0.000000
    # 3       0.016    A       14.663251    0.000000
    # 4      16.066    A       15.994910    0.000000
    # 5      16.319    A       15.994910    0.000000
    # 6     520.849    A       12.875666    1.239695
    # 7     520.956    A       12.875989    1.239759
    # 8    1407.763    A       15.994910    0.000000
    # 9    2386.390    A       12.877391    1.468959

    def molabscoef(nu, nu0=1, A=1, w=1):
        return (2*A*w/np.pi) / (4*(nu - nu0)**2 + w**2)

    # Generate IR spectrum with Lorentzian broadening as a function of
    # frequency, *nu*, from a (discrete) set of spectral lines as input.
    #   * Note, this implementation uses numpy.ufunc.reduce, specifically
    #     numpy.add.reduce, in lieu of np.sum, which allows it to accept
    #     both scalar and array values for nu and so that intensity is a
    #     properly vectorized function (i.e., a numpy ufunc). Note that
    #     using np.sum instead does not make intensity vectorized.
    #   * The input *nu* should be an iterable of frequencies that covers
    #     the range of the IR spectrum. A dense spacing may be necessary
    #     if the spectral lines are very narrow but spread apart and the
    #     values of nu are spaced linearly (e.g., using np.linspace).
    #     However, one may use a nonlinear spacing that is densest in the
    #     vicinity of the peaks to reduce the number of plot points.
    def intensity(nu, lines, areas=1, widths=1):
        lines = np.atleast_1d(lines)
        areas = np.atleast_1d(areas)
        widths = np.atleast_1d(widths)

        n_lines = len(lines)
        if n_lines > 1:
            areas = np.repeat(areas, n_lines) if len(areas) == 1 else areas
            widths = np.repeat(widths, n_lines) if len(widths) == 1 else widths
            if n_lines != len(areas):
                raise ValueError('Number of area parameters does not match number of spectral lines!')
            if n_lines != len(widths):
                raise ValueError('Number of width parameters does not match number of spectral lines!')
        gen = [molabscoef(nu, nu0, A, w) for nu0, A, w in zip(lines, areas, widths)]
        return np.add.reduce(gen)

    # ((6.02200e23 * pi) / (3 * ((2.99800e8 (m / s))^2))) * (1.46900 * ((3.33600e-30 coulomb * m)^2) * (m^(-2)) * (Da^(-1)))
    # CO2_spectral_lines = np.array([520.849, 520.849, 2386.390])  # CO2
    # CO2_line_areas = 43.42945 * np.array([1.240, 1.240, 1.469])  # (wrong vals from PM3 GAMESS + Vojta et al. 2017)
    # CO2_line_widths = 1  # cm^-1  (arbitrarily taken from Vojta et al. 2017)
    # min_line = np.min(CO2_spectral_lines)
    # max_line = np.max(CO2_spectral_lines)
    # spectrum_min = 0  # min_line - np.log10(min_line)*10*CO2_line_widths
    # spectrum_max = max_line + np.log10(max_line)*10*CO2_line_widths

    ir_line_freqs = data['vibfreq']
    ir_line_areas = 43.42945 * data['vibintens']
    ir_line_width = 1  # cm^-1
    min_line = np.min(ir_line_freqs)
    max_line = np.max(ir_line_freqs)

    n_plot_points = 1000
    min_freq = 0
    max_freq = max_line + np.log10(max_line)*10*ir_line_freqs

    freq_data = np.linspace(min_freq, max_freq, n_plot_points)
    intens_data = intensity(freq_data, ir_line_freqs, ir_line_areas, ir_line_width)
    # intens_data = intensity(freq_data, CO2_spectral_lines, CO2_line_areas, CO2_line_widths)

    df = pd.DataFrame({
        'Frequency': freq_data,
        'Intensity': intens_data
    })
    fig = px.line(
        df,
        x=r'Frequency cm$^{-1}$',
        y='Intensity',
        title='IR Spectrum',
        template='simple_white'
    )
    fig.update_layout(
        margin=dict(l=20, r=20, t=25, b=20),
    )

    data['irPlotJSON'] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    data['irPlotTitle'] = 'IR Spectrum'
    data['irPlotDesc'] = f"""
    Predicted infrared spectrum of {data['iupac_name']} using {data['theorylvl']}.
    """

    # ---------------------------------
    # Molecular orbitals format
    # ---------------------------------
    data["orbitals"] = misc.load_array(data["orbitals"])
    data["orbitals"] *= units.hartree_to_ev
    data["orbitals"] = [fmt.format(x) for x in data["orbitals"]]

    # ---------------------------------
    # Solvation calculations
    # ---------------------------------
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
