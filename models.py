import copy
import stubs

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
		return "/course/{}/{}/{}".format(self.course_id, self.lesson_id, self.id)


class Lesson(DataModel):
	
	def get_segments(self):
		return DataCollection(Segment, self._data['segments'])

	def get_resources(self):
		return DataCollection(Resource, self._data['resources'])

	def get_course(self):
		return Course(self.course_id, {'lessons': []})

	def get_permalink(self):
		return "/course/{}/{}".format(self.course_id, self.id)


class Course(DataModel):

	def get_lessons(self):
		return DataCollection(Lesson, self._data['lessons'])


class Resource(DataModel):

	def get_icon(self):
		stubs = {
			'google_doc': 'fa-file-alt',
			'google_sheet': 'fa-file-spreadsheet',
			'google_slides': 'fa-file-image'
		}
		if self.type in stubs:
			return stubs[self.type]
		return 'fa-file'

	def get_description(self):
		stubs = {
			'google_doc': 'Google document',
			'google_sheet': 'Google spreadsheet',
			'google_slides': 'Google slides'
		}
		if self.type in stubs:
			return stubs[self.type]
		return 'External file'


def get_segment(sid):
    for l in stubs.segments:
        for s in l:
            if s['id'] == sid:
                return Segment(sid, s)

def get_lesson(lid):
    return Lesson(int(lid), stubs.courses[0]['lessons'][int(lid)])

def get_course(cid):
    return Course(cid, stubs.courses[int(cid)])
