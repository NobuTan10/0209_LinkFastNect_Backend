# db_control/create_tables.py
from .mymodels import Base
from .connect import engine

def init_db() -> None:
    """FastAPIのstartupで呼ぶ。import時には実行しない。"""
    Base.metadata.create_all(engine)
