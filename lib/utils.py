import re

from models import Wordform, Frequency, Headword, Association, Base


class BufferException(Exception):
	
	def __init__(self, message):
		self.message = message


class Buffer(object):
	
	def __init__(self, size):
		super(Buffer, self).__init__()
		self._buffer = [None] * size
		self._max_size = size
		self.reset()

	def add(self, item):
		if self._index + 1 > self._max_size:
			raise BufferException("Buffer is full (size={0}, index={1}."\
					.format(self._max_size, self._index))

		self._buffer[self._index] = item
		self._index += 1

	def reset(self):
		self._index = 0	

	def has_items(self):
		return self._index > 0

	def is_full(self):
		return self._index >= self._max_size

	def items(self):
		return self._buffer[:self._index]


class TotalcountFile(dict):

	regexp = re.compile(r'(\d+)\s+(\d+)\s+\d+\s+\d+')

	def __init__(self, filename):
		with open(filename, "rb") as f:
			for line in f:
				m = self.regexp.match(line)
				if m:
					year, freq = map(int, m.groups())
					self[year] = freq


class UnigramFile(object):

	def __init__(self, filename, buffer_size, encoding="utf-8"):
		self.filename = filename
		self.buffer_size = buffer_size
		self.encoding = encoding

	def __iter__(self):
		self._iterator = read_buffered(open(self.filename, "rb"), self.buffer_size)
		return self

	def next(self):
		items = self._iterator.next().split('\t', 3)
		type_, year, freq, _ = items 
		return type_.decode(self.encoding), int(year), int(freq)


class DatabaseConverter(object):

	def __init__(self, googlefile, totalfile, database, buffer_size=1024):
		self.googlefile = googlefile
		self.totalfile = totalfile
		self.database = database
		self.buffer_size = buffer_size
		self.wordforms = {}

	def convert(self):
		entries = Buffer(self.buffer_size)	
		for entry in self.googlefile:
			if not entries.is_full():
				entries.add(entry)
			else:
				self._process_buffer(entries)
				entries.reset()

	def _add_wordform(self, wordform):
			self.wordforms[wordform] = len(self.wordforms)
			wf = Wordform(self.wordforms.get(wordform), wordform)
			self.database.add(wf)

	def _add_frequency(self, wordform_id, year, freq, relfreq):
		fr = Frequency(wordform_id, year, freq, relfreq)
		self.database.add(fr)

	def _process_buffer(self, buf):
		for wordform, year, freq in buf.items():
			if wordform not in self.wordforms:
				self._add_wordform(wordform)
			relfreq = 1.0 * freq / self.totalfile.get(year)
			self._add_frequency(self.wordforms.get(wordform), year, freq, relfreq)


def read_buffered(fileobj, size):
	buf = Buffer(size)
	for line in fileobj:
		buf.add(line)
		if buf.is_full():
			for item in buf.items():
				yield item
			buf.reset()

	if buf.has_items():
		for item in buf.items():
			yield item
