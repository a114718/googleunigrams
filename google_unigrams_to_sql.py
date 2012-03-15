from argparse import ArgumentParser

from utils import UnigramFile, TotalcountFile, DatabaseConverter, Buffer
from models import init_db


def main():

	parser = ArgumentParser(description="Convert google books unigram list to database.")

	parser.add_argument("--drivername", choices=["mysql", "postgresql", "sqlite", "access", "mssql", "oracle", "sybase", "drizzle", "firebird", "informix", "maxdb"], default="sqlite",
			help="select database backend")
	parser.add_argument("--database", type=unicode, default=None,
			help="name of database")
	parser.add_argument("--host", type=unicode, default=None)
	parser.add_argument("--user", type=unicode, default=None)
	parser.add_argument("--password", type=unicode, default=None)
	parser.add_argument("--frequency", type=unicode, default=None, required=True,
			help="googlebooks 1-gram file")
	parser.add_argument("--total", type=unicode, default=None, required=True,
			help="googlebooks totalcounts")
	parser.add_argument("--port", type=int, default=0)
	parser.add_argument("--buffer", type=int, default=1024,
			help="number of lines processed at once")
	options = parser.parse_args()

	fname = options.frequency
	tname = options.total
	
	database = init_db(options)

	google_buffer_size = options.buffer

	cc = DatabaseConverter(
		UnigramFile(fname, google_buffer_size),
		TotalcountFile(tname),
		database
	)

	cc.convert()	

if __name__ == '__main__':
	main()
