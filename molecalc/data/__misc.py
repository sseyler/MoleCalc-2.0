import gzip
import sqlalchemy

from sqlalchemy import (
    Column,
    Integer,
    String,
    LargeBinary,
)

from molecalc.data.modelbase import SqlAlchemyBase


def compress(s):
    if type(s) == str:
        s = s.encode()
    b = gzip.compress(s)
    return b


def decompress(b):
    s = gzip.decompress(b)
    return s


class CompressedString(sqlalchemy.types.TypeDecorator):
    """
    Storage datatype for large blobs of text
    """

    impl = LargeBinary

    def process_bind_param(self, value, dialect):
        return compress(value)

    def process_result_value(self, value, dialect):
        return decompress(value)


class Counter(SqlAlchemyBase):
    __tablename__ = "molecules"
    smiles: str = Column(String, primary_key=True)
    count: int = Column(Integer)

    def __repr__(self):
        fmt = "<Molecule {:} {:} >"
        return fmt.format(self.smiles, self.count)
