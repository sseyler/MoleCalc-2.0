import datetime
import mongoengine as me


class GamessIO(me.Document):
    registered_date = me.DateTimeField(default=datetime.datetime.now)
    hashkey = me.StringField(required=True)
    name = me.StringField(required=True)

    inp_file = me.StringField()
    out_file = me.StringField()

    # TODO perhaps organize calculations by molecule and have lists of both
    #   hashkeys and smiles/sdf

    meta = {
        'db_alias': 'core',
        'collection': 'gamess_ios'
    }
