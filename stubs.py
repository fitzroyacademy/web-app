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

segments = [
    {
        "title": "Introduction",
        "duration": "1:12",
        "external_id": "4ub59urk8l",
        "url": "https://fitzroyacademy.wistia.com/medias/4ub59urk8l",
        "template": "video_wistia",
        "type": "html",
        "id": "seg_a"
    },
    {
        "title": "Lesson Resources",
        "duration": "2:36",
        "external_id": "o3lv8dulfk",
        "url": "https://fitzroyacademy.wistia.com/medias/o3lv8dulfk",
        "template": "video_wistia",
        "type": "story",
        "id": "seg_b"
    },
    {
        "title": "Drawing without words",
        "duration": "8:12",
        "external_id": "yw3rxkapqv",
        "url": "https://fitzroyacademy.wistia.com/medias/yw3rxkapqv",
        "template": "video_wistia",
        "type": "practical",
        "id": "seg_c"
    },
    {
        "title": "Five designers in a box",
        "duration": "1:36",
        "external_id": "rxty4preej",
        "url": "https://fitzroyacademy.wistia.com/medias/rxty4preej",
        "template": "video_wistia",
        "type": "survey",
        "id": "seg_d"
    },
    {
        "title": "Quiet loud brainstorming",
        "duration": "7:14",
        "external_id": "1aqbgjr5ex",
        "url": "https://fitzroyacademy.wistia.com/medias/1aqbgjr5ex",
        "template": "video_wistia",
        "type": "survey",
        "id": "seg_e"
    },
    {
        "title": "Party in the woods",
        "duration": "2:47",
        "external_id": "7an2f2hf16",
        "url": "https://fitzroyacademy.wistia.com/medias/7an2f2hf16",
        "template": "video_wistia",
        "type": "case",
        "id": "seg_f"
    },
    {
        "title": "Find your Awe",
        "duration": "7:56",
        "external_id": "te5p2h5muw",
        "url": "https://fitzroyacademy.wistia.com/medias/te5p2h5muw",
        "template": "video_wistia",
        "type": "survey",
        "id": "seg_g"
    },
    {
        "title": "Mulago Fellow",
        "duration": "3:33",
        "external_id": "ja7ph4j22q",
        "url": "https://fitzroyacademy.wistia.com/medias/ja7ph4j22q",
        "template": "video_wistia",
        "type": "html",
        "id": "seg_h"
    },
    {
        "title": "Literal change of perspective",
        "duration": "4:08",
        "external_id": "ox83pgmd2l",
        "url": "https://fitzroyacademy.wistia.com/medias/ox83pgmd2l",
        "template": "video_wistia",
        "type": "story",
        "id": "seg_i"
    },
    {
        "title": "Make your own movie soundtrack",
        "duration": "4:15",
        "external_id": "trphfyidmr",
        "url": "https://fitzroyacademy.wistia.com/medias/trphfyidmr",
        "template": "video_wistia",
        "type": "video_wistia",
        "id": "seg_j"
    },
    {
        "title": "Speedriding",
        "duration": "2:46",
        "external_id": "co72ocpe4c",
        "url": "https://fitzroyacademy.wistia.com/medias/co72ocpe4c",
        "template": "video_wistia",
        "type": "case",
        "id": "seg_k"
    },
    {
        "title": "Historical Mirrors",
        "duration": "5:44",
        "external_id": "az7nj4f6sp",
        "url": "https://fitzroyacademy.wistia.com/medias/az7nj4f6sp",
        "template": "video_wistia",
        "type": "practical",
        "id": "seg_l"
    },
    {
        "title": "Sleep",
        "duration": "5:48",
        "external_id": "bv7fq9cyxx",
        "url": "https://fitzroyacademy.wistia.com/medias/bv7fq9cyxx",
        "template": "video_wistia",
        "type": "locked",
        "id": "seg_m"
    }
];

course = {
	'lessons': [
		{'id': 'les_a', 'title': 'Lesson 1', 'duration': '45:15', 'segments': segments, 'active': False},
		{'id': 'les_b', 'title': 'Lesson 2', 'duration': '45:15', 'segments': segments, 'active': True},
		{'id': 'les_c', 'title': 'Lesson 3', 'duration': '45:15', 'segments': segments, 'active': False}
	]
}