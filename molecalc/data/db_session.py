import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session

from molecalc.data.modelbase import SqlAlchemyBase

__factory = None


def global_init(db_file: str):
    global __factory

    if __factory:
        return

    # --- SQLAlchemy ---
    if not db_file or not db_file.strip():
        raise Exception("You must specify a database filename.")

    conn_str = 'sqlite:///' + db_file.strip() + '.sqlite'
    print("Connecting to DB with {}".format(conn_str))

    engine = sa.create_engine(conn_str, echo=False, connect_args={"check_same_thread": False})
    __factory = orm.sessionmaker(bind=engine)

    # noinspection PyUnresolvedReferences
    import molecalc.data.__all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory

    session: Session = __factory()

    session.expire_on_commit = False

    return session
