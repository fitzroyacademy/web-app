import copy

class DataModel:
	def __init__(self, sid, data):
		self._id = sid
		self._data = data
		self._data['id'] = sid

	def __getattr__(self, key="WTF"):
		get_meth = "get_{}".format(key)
		try:
			meth = object.__getattribute__(self, get_meth)
		except:
			return self._data[key]
		return meth()

	def dump(self):
		data = copy.copy(self._data)
		for f in dir(self):
			if f.startswith('get_') and callable(getattr(self, f)):
				data[f.split('_')[1]] = getattr(self, f)()
		for k, v in data.items():
			dump = None
			try:
				dump = getattr(v, 'dump')
			except:
				pass
			if dump is not None:
				data[k] = dump()
		return data


class DataCollection:
	def __init__(self, base, items):
		self._items = items
		self._base = base
		self._i = 0

	def find(self, **kwargs):
		for i in self._items:
			match = True
			for k,v in kwargs.items():
				if i[k] != v:
					match = False
					break
			if match:
				return self._base(i['id'], i)

	def __getitem__(self, i):
		item = self._items[i]
		return self._base(item['id'], self._items[i])

	def __iter__(self):
		self._i = 0
		return self

	def __next__(self):
		max_index = len(self._items) - 1
		if self._i <= max_index:
			n = self.__getitem__(self._i)
			self._i += 1
			return n
		else:
			self._i = 0
			raise StopIteration

	def dump(self):
		o = []
		for i in range(len(self._items)):
			o.append(self.__getitem__(i).dump())
		return o


class Segment(DataModel):

	def get_permalink(self):
		return "/c123/{}/{}".format(self.lesson.id, self.id)

	def get_lesson(self):
		return Lesson('01', {'segments': []})


class Lesson(DataModel):
	
	def get_segments(self):
		return DataCollection(Segment, self._data['segments'])


class Course(DataModel):

	def get_lessons(self):
		return DataCollection(Lesson, self._data['lessons'])
