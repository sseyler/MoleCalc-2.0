
# TODO
#   Think about where else this can go; maybe a config file somewhere.
HOME = '/home/cloudlab'

SETTINGS = {
    'gamess.rungms': f'{HOME}/Library/gamess/rungms',
    'gamess.scr': f'{HOME}/scratch/gamess/restart/',
    'gamess.userscr': f'{HOME}/scratch/gamess/restart/',
    'molecalc.scr': f'{HOME}/scratch/molecalc_data/',
    'db.dir': 'db',
    'db.name': 'molecalc'
}

MONGODB_SETTINGS = {
    'db': SETTINGS['db.name'],
    'host': 'localhost',
    'port': 27017,
    'alias': 'core',
}
