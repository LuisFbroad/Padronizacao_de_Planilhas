from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Pessoa(Base):
    __tablename__ = "pessoa"

    id = Column(Integer, primary_key=True)
    nome = Column(String(150), nullable=False, unique=True)

    indicacoes = relationship("Indicacao", back_populates="pessoa")


class Indicacao(Base):
    __tablename__ = "indicacoes"

    id = Column(Integer, primary_key=True)
    pessoa_id = Column(Integer, ForeignKey("pessoa_id"), nullable=False)
    data_indicacao = Column(Date, nullable=True)

    pessoa = relationship("Pessoa", back_populates="indicacoes")
