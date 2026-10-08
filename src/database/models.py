from datetime import datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.database.connection import Base


class Pessoa(Base):
    __tablename__ = "pessoas"

    id = Column(Integer, primary_key=True)

    nome = Column(String(255), nullable=False, unique=True)

    indicacoes = relationship("Indicacao", back_populates="pessoa")


class Area(Base):
    __tablename__ = "areas"

    id = Column(Integer, primary_key=True)

    nome = Column(String(100), nullable=False, unique=True)

    indicacoes = relationship("Indicacao", back_populates="area")


class Indicacao(Base):

    __tablename__ = "indicacoes"

    id = Column(Integer, primary_key=True)

    pessoa_id = Column(Integer, ForeignKey("pessoas.id"), nullable=False)

    area_id = Column(Integer, ForeignKey("areas.id"), nullable=False)

    processo = Column(String(255), nullable=True)

    tipo_indicacao = Column(String(50), nullable=True)

    data_indicacao = Column(Date, nullable=True)

    arquivo_origem = Column(String(255), nullable=True)

    data_importacao = Column(DateTime, default=datetime.now)

    pessoa = relationship("Pessoa", back_populates="indicacoes")

    area = relationship("Area", back_populates="indicacoes")
