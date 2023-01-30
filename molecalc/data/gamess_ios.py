import datetime
# import mongoengine as me
from app import db_me


class GamessIO(db_me.Document):
    registered_date = db_me.DateTimeField(default=datetime.datetime.now)
    hashkey = db_me.StringField(required=True)
    name = db_me.StringField(required=True)

    inp_file = db_me.StringField()
    out_file = db_me.StringField()
    err_file = db_me.StringField()

    # TODO perhaps organize calculations by molecule and have lists of both
    #   hashkeys and smiles/sdf

    meta = {
        'db_alias': 'core',
        'collection': 'gamess_ios'
    }
