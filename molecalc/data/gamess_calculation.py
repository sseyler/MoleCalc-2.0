import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
)

from molecalc.data.modelbase import SqlAlchemyBase
from molecalc.data.__misc import CompressedString


class GamessCalculation(SqlAlchemyBase):
    __tablename__ = "gamesscalculations"
    id: int = Column(Integer, primary_key=True, autoincrement=True)

    # Basic descriptors
    hashkey: str = Column(String, unique=True)
    created: datetime.datetime = Column(DateTime, default=datetime.datetime.now, index=True)
    name: str = Column(String)
    smiles: str = Column(String)
    sdf: str = Column(String)
    mol2: str = Column(String)
    svg: str = Column(String)
    coordinates: str = Column(String)
    theorylvl: str = Column(String)

    # GAMESS optimization input and output files
    inptxt_opt: CompressedString = Column(CompressedString)
    outtxt_opt: CompressedString = Column(CompressedString)
    errtxt_opt: CompressedString = Column(CompressedString)
    # GAMESS vibrational calculation input and output files
    inptxt_vib: CompressedString = Column(CompressedString)
    outtxt_vib: CompressedString = Column(CompressedString)
    errtxt_vib: CompressedString = Column(CompressedString)
    # GAMESS orbitals calculation input and output files
    inptxt_orb: CompressedString = Column(CompressedString)
    outtxt_orb: CompressedString = Column(CompressedString)
    errtxt_orb: CompressedString = Column(CompressedString)

    # GAMESS Results
    enthalpy: float = Column(Float)
    charges: str = Column(String)

    islinear: str = Column(String)
    vibjsmol: CompressedString = Column(CompressedString)
    vibfreq: str = Column(String)
    vibintens: str = Column(String)
    thermo: str = Column(String)

    orbitals: str = Column(String)
    orbitalstxt: CompressedString = Column(CompressedString)

    soltotal: float = Column(Float)
    solpolar: float = Column(Float)
    solnonpolar: float = Column(Float)
    solsurface: float = Column(Float)
    soldipole: str = Column(String)
    soldipoletotal: float = Column(Float)

    def __repr__(self):
        fmt = "<GamessCalculation {:} {:} >"
        return fmt.format(self.smiles, self.hashkey)
