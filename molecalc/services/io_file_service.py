import logging

import molecalc.data.db_session as db_session
from molecalc.data.gamess_calculation import GamessCalculation


_logger = logging.getLogger("molecalc:io_file_service")


def get_calc_type(hashkey: str, calc: str):
    session = db_session.create_session()
    try:
        this_calc = session.query(GamessCalculation) \
            .filter_by(hashkey=hashkey) \
            .first()
    finally:
        session.close()

    match calc:
        case 'opt':
            return {'inp': this_calc.inptxt_opt,
                    'out': this_calc.outtxt_opt,
                    'err': this_calc.errtxt_opt}
        case 'vib':
            return {'inp': this_calc.inptxt_vib,
                    'out': this_calc.outtxt_vib,
                    'err': this_calc.errtxt_vib}
        case 'orb':
            return {'inp': this_calc.inptxt_orb,
                    'out': this_calc.outtxt_orb,
                    'err': this_calc.errtxt_orb}
        case _:
            err_msg = 'Unknown calculation type "{calc}"'
            _logger.error(err_msg)
            return {
                "error": "998",
                "message": f"Internal server error: {err_msg}",
            }


def get_calc_io_file(hashkey: str, calc: str, iofile: str):
    match iofile:
        case 'inp':
            s = get_calc_type(hashkey, calc)['inp']
        case 'out':
            s = get_calc_type(hashkey, calc)['out']
        case 'err':
            s = get_calc_type(hashkey, calc)['err']
        case _:
            _logger.error('Unknown I/O filetype "{ext}"')

    # CompressedString decompressed on cast to str, utf-8 converts from bytes
    f = str(s, 'utf-8')
    return f
