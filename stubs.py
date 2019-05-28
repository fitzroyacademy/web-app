import random

students =  [
	{
		'id':'1',
		'name':'Alice',
		'completion': ';'.join(str(v) for v in random.sample(range(100), 5)),
		'progress': random.randrange(50, 100),
		'color': '#e809db',
		'admin': False
	},
	{
		'id':'2',
		'name':'Bob',
		'completion': ';'.join(str(v) for v in random.sample(range(100), 5)),
		'progress': random.randrange(10, 50),
		'color': '#0f7ff4',
		'admin': False
	},
	{
		'id':'3',
		'name':'Eve',
		'completion': ';'.join(str(v) for v in random.sample(range(100), 5)),
		'progress': random.randrange(50, 100),
		'color': '#666',
		'admin': True
	}
];