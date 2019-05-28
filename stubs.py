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

lessons = [
	{
		"title": "Introduction",
		"duration": 1,
		"external_id": "4ub59urk8l",
		"url": "https://fitzroyacademy.wistia.com/medias/4ub59urk8l",
		"type": "video_wistia"
	},
	{
		"title": "Lesson Resources",
		"duration": 2,
		"external_id": "o3lv8dulfk",
		"url": "https://fitzroyacademy.wistia.com/medias/o3lv8dulfk",
		"type": "video_wistia"
	},
	{
		"title": "Drawing without words",
		"duration": 8,
		"external_id": "yw3rxkapqv",
		"url": "https://fitzroyacademy.wistia.com/medias/yw3rxkapqv",
		"type": "video_wistia"
	},
	{
		"title": "Five designers in a box",
		"duration": 1,
		"external_id": "rxty4preej",
		"url": "https://fitzroyacademy.wistia.com/medias/rxty4preej",
		"type": "video_wistia"
	},
	{
		"title": "Quiet loud brainstorming",
		"duration": 7,
		"external_id": "1aqbgjr5ex",
		"url": "https://fitzroyacademy.wistia.com/medias/1aqbgjr5ex",
		"type": "video_wistia"
	},
	{
		"title": "Party in the woods",
		"duration": 2,
		"external_id": "7an2f2hf16",
		"url": "https://fitzroyacademy.wistia.com/medias/7an2f2hf16",
		"type": "video_wistia"
	},
	{
		"title": "Find your Awe",
		"duration": 7,
		"external_id": "te5p2h5muw",
		"url": "https://fitzroyacademy.wistia.com/medias/te5p2h5muw",
		"type": "video_wistia"
	},
	{
		"title": "Mulago Fellow",
		"duration": 3,
		"external_id": "ja7ph4j22q",
		"url": "https://fitzroyacademy.wistia.com/medias/ja7ph4j22q",
		"type": "video_wistia"
	},
	{
		"title": "Literal change of perspective",
		"duration": 4,
		"external_id": "ox83pgmd2l",
		"url": "https://fitzroyacademy.wistia.com/medias/ox83pgmd2l",
		"type": "video_wistia"
	},
	{
		"title": "Make your own movie soundtrack",
		"duration": 4,
		"external_id": "trphfyidmr",
		"url": "https://fitzroyacademy.wistia.com/medias/trphfyidmr",
		"type": "video_wistia"
	},
	{
		"title": "Speedriding",
		"duration": 2,
		"external_id": "co72ocpe4c",
		"url": "https://fitzroyacademy.wistia.com/medias/co72ocpe4c",
		"type": "video_wistia"
	},
	{
		"title": "Historical Mirrors",
		"duration": 5,
		"external_id": "az7nj4f6sp",
		"url": "https://fitzroyacademy.wistia.com/medias/az7nj4f6sp",
		"type": "video_wistia"
	},
	{
		"title": "Sleep",
		"duration": 5,
		"external_id": "bv7fq9cyxx",
		"url": "https://fitzroyacademy.wistia.com/medias/bv7fq9cyxx",
		"type": "video_wistia"
	}
];