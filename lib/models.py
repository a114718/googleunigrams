from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy import Column, Integer, Unicode, Float, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Frequency(Base):
	__tablename__ = 'frequency'
	id = Column(Integer, primary_key=True)
	year = Column(Integer)
	freq = Column(Integer)
	relfreq = Column(Float)
	wordform_id = Column(Integer, ForeignKey('wordform.id'))

	def __init__(self, wordform_id, year, freq, relfreq):
		self.wordform_id = wordform_id
		self.year = year
		self.freq = freq
		self.relfreq = relfreq


class Wordform(Base):
	__tablename__ = 'wordform'
	id = Column(Integer, primary_key=True)
	text = Column(Unicode(255))
	frequency = relationship("Frequency")

	def __init__(self, id, text):
		self.id = id
		self.text = text


def init_db(options):
	url = URL(options.drivername, host=options.host, password=options.password, port=options.port, database=options.database)
	engine = create_engine(url, echo=True)
	Session = sessionmaker(bind=engine)
	Base.metadata.create_all(engine)
	return Session()
