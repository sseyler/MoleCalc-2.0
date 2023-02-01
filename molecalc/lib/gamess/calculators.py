import copy
import logging
from multiprocessing import Pipe, Process

import ppqm

_logger = logging.getLogger("molecalc:calc")

MAX_TIME = 90  # seconds


def optimize_coordinates(molobj, gamess_options):
    theory_level = gamess_options.pop('theory_level', 'pm3')
    calculation_options = {
        "basis": {"gbasis": theory_level},
        "contrl": {"runtyp": "optimize"},
        "statpt": {"opttol": 0.00025, "nstep": 500, "projct": False},
    }

    gamess_options.get("filename", None)

    calc_obj = ppqm.gamess.GamessCalculator(**gamess_options)
    results, files = calc_obj.calculate(molobj, calculation_options)

    properties = results[0]
    gamess_io = files[0]

    return properties, gamess_io


def calculate_vibrations(molobj, gamess_options):
    theory_level = gamess_options.pop('theory_level', 'pm3')
    n_atoms = len( ppqm.chembridge.molobj_to_atoms(molobj) )
    if n_atoms == 1:
        calculation_options = {
            "contrl": {
                "runtyp": "hessian",
                "coord": "cart",
                "units": "angs",
                "scftyp": "rhf",
                "maxit": 60,
            },
            "basis": {"gbasis": "sto", "ngauss": 3},
        }
    else:
        calculation_options = {
            "basis": {"gbasis": theory_level},
            "contrl": {"runtyp": "hessian", "maxit": 60},
            "force": {"method": "seminum"},
        }

    calc_obj = ppqm.gamess.GamessCalculator(**gamess_options)
    results, files = calc_obj.calculate(molobj, calculation_options)
    properties = results[0]
    gamess_io = files[0]

    print('--- results --' + 50 * '>')
    print(results)
    print('--- files --' + 50 * '>')
    print(files)
    print('--- properties --' + 50 * '>')
    print(properties)
    print('--- gamess_io --' + 50 * '>')
    print(gamess_io)

    return properties, gamess_io


def calculate_orbitals(molobj, gamess_options):
    #TODO Fix theory_level placeholder here
    theory_level = gamess_options.pop('theory_level', 'pm3')

    calculation_options = {
        "contrl": {
            "coord": "cart",
            "units": "angs",
            "scftyp": "rhf",
            "maxit": 60,
        },
        "basis": {"gbasis": "sto", "ngauss": 3},
    }

    calc_obj = ppqm.gamess.GamessCalculator(**gamess_options)
    try:
        results, files = calc_obj.calculate(molobj, calculation_options)
        properties = results[0]
        gamess_io = files[0]
    except TypeError:
        properties = dict()
        properties["error"] = "Failed orbital calculation"
        gamess_io = {'inp': '', 'out': '', 'err': ''}

    return properties, gamess_io


def calculate_solvation(molobj, gamess_options):

    calculation_options = dict()
    calculation_options["basis"] = {"gbasis": "PM3"}
    calculation_options["system"] = {"mwords": 125}
    calculation_options["pcm"] = {
        "solvnt": "water",
        "mxts": 15000,
        "icav": 1,
        "idisp": 1,
    }
    calculation_options["tescav"] = {"mthall": 4, "ntsall": 60}

    calc_obj = ppqm.gamess.GamessCalculator(**gamess_options)
    try:
        results, files = calc_obj.calculate(molobj, calculation_options)
        properties = results[0]
        gamess_io = files[0]
    except TypeError:
        properties = dict()
        properties["error"] = "Solvation calculation failed"
        gamess_io = {'inp': '', 'out': '', 'err': ''}
    if "charges" not in properties:
        properties = dict()
        properties["error"] = "Solvation calculation failed"
        gamess_io = {'inp': '', 'out': '', 'err': ''}

    return properties, gamess_io


def calculate_all_properties(molobj, gamess_options, async_calc=False):

    funcs = [
        calculate_vibrations,
        calculate_orbitals,
        # calculate_solvation,
    ]

    filename = gamess_options.get("filename", "gamess_calc")

    if async_calc:
        def procfunc(conn, func, *args, **kwargs):
            prop = func(*args, **kwargs)
            conn.send(prop)
            conn.close()

        procs = []
        conns = []

        for func in funcs:

            # Change scr
            gamess_options = copy.deepcopy(gamess_options)
            gamess_options["filename"] = filename + "_" + func.__name__

            parent_conn, child_conn = Pipe()
            p = Process(
                target=procfunc,
                args=(child_conn, func, molobj, gamess_options),
            )
            p.start()

            procs.append(p)
            conns.append(parent_conn)

        for proc in procs:
            proc.join(timeout=MAX_TIME)

        properties_and_files = [conns[i].recv() for i in range(len(funcs))]
        properties, io_files = zip(*properties_and_files)  # unzip

    else:
        print('HELLO, YO')
        properties = []
        io_files = []
        for func in funcs:
            # Change scr
            gamess_options = copy.deepcopy(gamess_options)
            gamess_options["filename"] = filename + "_" + func.__name__
            results, files = func(molobj, gamess_options)
            properties.append(results)
            io_files.append(files)

    return properties, io_files
