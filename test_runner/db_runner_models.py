from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Enum,
    DateTime, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
import enum

Base = declarative_base()


class EstadoPruebaEnum(enum.Enum):
    PASADO = "pasado"
    FALLIDO = "fallido"
    BLOQUEADO = "bloqueado"
    EN_PROGRESO = "en_progreso"


class Result(Base):
    __tablename__ = "result"

    id = Column(Integer, primary_key=True)

    test_case_id = Column(Integer, nullable=False)
    test_cycle_id = Column(Integer)

    estado_prueba = Column(Enum(EstadoPruebaEnum), nullable=False)
    entorno = Column(String(100))
    resultado_obtenido = Column(Text)
    notas = Column(Text)
    archivo = Column(String(255))  # evidencia final

    fecha_created = Column(DateTime, default=datetime.utcnow)
    usu_created = Column(String(100))
