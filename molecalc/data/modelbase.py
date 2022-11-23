# TODO: combine this with data/extensions.py, which sets up the sqlalchemy
# naming convention and a CRUDMixin class. Note that infrastructure/config.py
# also has configuration for sqlite database.

import sqlalchemy.ext.declarative as dec

SqlAlchemyBase = dec.declarative_base()
