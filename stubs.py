import random
import models

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

segments = [];
segments.append([
    {
        "title": "Introduction",
        "duration": "1:12",
        "external_id": "4ub59urk8l",
        "url": "https://fitzroyacademy.wistia.com/medias/4ub59urk8l",
        "template": "video_wistia",
        "type": "html",
        "id": "seg_a",
        "lesson_id": 'l00',
        "course_id": "00"
    },
    {
        "title": "Lesson Resources",
        "duration": "2:36",
        "external_id": "o3lv8dulfk",
        "url": "https://fitzroyacademy.wistia.com/medias/o3lv8dulfk",
        "template": "video_wistia",
        "type": "story",
        "id": "seg_b",
        "lesson_id": 'l00',
        "course_id": "00"
    },
    {
        "title": "Drawing without words",
        "duration": "8:12",
        "external_id": "yw3rxkapqv",
        "url": "https://fitzroyacademy.wistia.com/medias/yw3rxkapqv",
        "template": "video_wistia",
        "type": "practical",
        "id": "seg_c",
        "lesson_id": 'l00',
        "course_id": "00"
    },
    {
        "title": "Guest lecture: very large boxes",
        "duration": "1:53",
        "external_id": "xdhLQCYQ-nQ",
        "url": "https://www.youtube.com/watch?v=xdhLQCYQ-nQ",
        "template": "video_youtube",
        "type": "practical",
        "id": "seg_maru",
        "lesson_id": 'l00',
        "course_id": "00"
    },   
    {
        "title": "Five designers in a box",
        "duration": "1:36",
        "external_id": "rxty4preej",
        "url": "https://fitzroyacademy.wistia.com/medias/rxty4preej",
        "template": "video_wistia",
        "type": "survey",
        "id": "seg_d",
        "lesson_id": 'l00',
        "course_id": "00"
    },
    {
        "title": "Quiet loud brainstorming",
        "duration": "7:14",
        "external_id": "1aqbgjr5ex",
        "url": "https://fitzroyacademy.wistia.com/medias/1aqbgjr5ex",
        "template": "video_wistia",
        "type": "survey",
        "id": "seg_e",
        "lesson_id": 'l00',
        "course_id": "00"
    },
    {
        "title": "Party in the woods",
        "duration": "2:47",
        "external_id": "7an2f2hf16",
        "url": "https://fitzroyacademy.wistia.com/medias/7an2f2hf16",
        "template": "video_wistia",
        "type": "case",
        "id": "seg_f",
        "lesson_id": 'l00',
        "course_id": "00"
    },
    {
        "title": "Find your Awe",
        "duration": "7:56",
        "external_id": "te5p2h5muw",
        "url": "https://fitzroyacademy.wistia.com/medias/te5p2h5muw",
        "template": "video_wistia",
        "type": "survey",
        "id": "seg_g",
        "lesson_id": 'l00',
        "course_id": "00"
    },
    {
        "title": "Mulago Fellow",
        "duration": "3:33",
        "external_id": "ja7ph4j22q",
        "url": "https://fitzroyacademy.wistia.com/medias/ja7ph4j22q",
        "template": "video_wistia",
        "type": "html",
        "id": "seg_h",
        "lesson_id": 'l00',
        "course_id": "00"
    },
    {
        "title": "Literal change of perspective",
        "duration": "4:08",
        "external_id": "ox83pgmd2l",
        "url": "https://fitzroyacademy.wistia.com/medias/ox83pgmd2l",
        "template": "video_wistia",
        "type": "story",
        "id": "seg_i",
        "lesson_id": 'l00',
        "course_id": "00"
    },
    {
        "title": "Make your own movie soundtrack",
        "duration": "4:15",
        "external_id": "trphfyidmr",
        "url": "https://fitzroyacademy.wistia.com/medias/trphfyidmr",
        "template": "video_wistia",
        "type": "video_wistia",
        "id": "seg_j",
        "lesson_id": 'l00',
        "course_id": "00"
    },
    {
        "title": "Speedriding",
        "duration": "2:46",
        "external_id": "co72ocpe4c",
        "url": "https://fitzroyacademy.wistia.com/medias/co72ocpe4c",
        "template": "video_wistia",
        "type": "case",
        "id": "seg_k",
        "lesson_id": 'l00',
        "course_id": "00"
    },
    {
        "title": "Historical Mirrors",
        "duration": "5:44",
        "external_id": "az7nj4f6sp",
        "url": "https://fitzroyacademy.wistia.com/medias/az7nj4f6sp",
        "template": "video_wistia",
        "type": "practical",
        "id": "seg_l",
        "lesson_id": 'l00',
        "course_id": "00"
    },
    {
        "title": "Sleep",
        "duration": "5:48",
        "external_id": "bv7fq9cyxx",
        "url": "https://fitzroyacademy.wistia.com/medias/bv7fq9cyxx",
        "template": "video_wistia",
        "type": "locked",
        "id": "seg_m",
        "lesson_id": 'l00',
        "course_id": "00"
    }
]);

segments.append([
  {
    "title": "Introduction",
    "duration": "1:30",
    "external_id": "xmgvld0tjy",
    "url": "https://fitzroyacademy.wistia.com/medias/xmgvld0tjy",
    "template": "video_wistia",
    "id": "seg_n",
    "lesson_id": "l01",
    "course_id": "00",
    "type": "locked"
  },
  {
    "title": "Lesson resources",
    "duration": "0:36",
    "external_id": "nrd9n1i0th",
    "url": "https://fitzroyacademy.wistia.com/medias/nrd9n1i0th",
    "template": "video_wistia",
    "id": "seg_o",
    "lesson_id": "l01",
    "course_id": "00",
    "type": "locked"
  },
  {
    "title": "Prepwork",
    "duration": "3:34",
    "external_id": "ik28rwd8xh",
    "url": "https://fitzroyacademy.wistia.com/medias/ik28rwd8xh",
    "template": "video_wistia",
    "id": "seg_p",
    "lesson_id": "l01",
    "course_id": "00",
    "type": "locked"
  },
  {
    "title": "The Pipeline",
    "duration": "7:31",
    "external_id": "5qr1imh89q",
    "url": "https://fitzroyacademy.wistia.com/medias/5qr1imh89q",
    "template": "video_wistia",
    "id": "seg_q",
    "lesson_id": "l01",
    "course_id": "00",
    "type": "locked"
  },
  {
    "title": "Making Contact",
    "duration": "10:23",
    "external_id": "i4fv1tzbke",
    "url": "https://fitzroyacademy.wistia.com/medias/i4fv1tzbke",
    "template": "video_wistia",
    "id": "seg_r",
    "lesson_id": "l01",
    "course_id": "00",
    "type": "locked"
  },
  {
    "title": "Meeting in person",
    "duration": "5:56",
    "external_id": "8r42r8wd4e",
    "url": "https://fitzroyacademy.wistia.com/medias/8r42r8wd4e",
    "template": "video_wistia",
    "id": "seg_s",
    "lesson_id": "l01",
    "course_id": "00",
    "type": "locked"
  },
  {
    "title": "Follow up and Routines",
    "duration": "5:23",
    "external_id": "kolppnbfaj",
    "url": "https://fitzroyacademy.wistia.com/medias/kolppnbfaj",
    "template": "video_wistia",
    "id": "seg_t",
    "lesson_id": "l01",
    "course_id": "00",
    "type": "locked"
  }
]);

segments.append([
  {
    "title": "Introduction",
    "duration": "1:22",
    "external_id": "nxdknxgjg4",
    "url": "https://fitzroyacademy.wistia.com/medias/nxdknxgjg4",
    "template": "video_wistia",
    "id": "598pejq0ahbmr92hdjgcx",
    "lesson_id": "l02",
    "course_id": "00",
    "type": "locked"
  },
  {
    "title": "Lesson Resources",
    "duration": "0:42",
    "external_id": "bftwqod4cr",
    "url": "https://fitzroyacademy.wistia.com/medias/bftwqod4cr",
    "template": "video_wistia",
    "id": "bpp1dfgexztukgyhdrqvk",
    "lesson_id": "l02",
    "course_id": "00",
    "type": "locked"
  },
  {
    "title": "The Big numbers",
    "duration": "6:12",
    "external_id": "tsni6veh6m",
    "url": "https://fitzroyacademy.wistia.com/medias/tsni6veh6m",
    "template": "video_wistia",
    "id": "2plze9cgsb2ifhwb0ai9da",
    "lesson_id": "l02",
    "course_id": "00",
    "type": "locked"
  },
  {
    "title": "Adding detail",
    "duration": "8:17",
    "external_id": "nleir20ny1",
    "url": "https://fitzroyacademy.wistia.com/medias/nleir20ny1",
    "template": "video_wistia",
    "id": "sj93fnzjlef0mvhaoiolb1s",
    "lesson_id": "l02",
    "course_id": "00",
    "type": "locked"
  },
  {
    "title": "Do some maths",
    "duration": "12:24",
    "external_id": "jgqhh7dogk",
    "url": "https://fitzroyacademy.wistia.com/medias/jgqhh7dogk",
    "template": "video_wistia",
    "id": "nu9dmhwz7gsr4edpsrac1",
    "lesson_id": "l02",
    "course_id": "00",
    "type": "locked"
  },
  {
    "title": "Formatting",
    "duration": "3:57",
    "external_id": "13juax70dj",
    "url": "https://fitzroyacademy.wistia.com/medias/13juax70dj",
    "template": "video_wistia",
    "id": "ouvwnfb2zz89vzag7l6jv",
    "lesson_id": "l02",
    "course_id": "00",
    "type": "locked"
  },
  {
    "title": "Benchmark the results",
    "duration": "5:21",
    "external_id": "z32ayrtmdo",
    "url": "https://fitzroyacademy.wistia.com/medias/z32ayrtmdo",
    "template": "video_wistia",
    "id": "ptrrx6iowybe0ppxwv0wmq",
    "lesson_id": "l02",
    "course_id": "00",
    "type": "locked"
  },
  {
    "title": "Growth levers",
    "duration": "5:15",
    "external_id": "ee8f50jiig",
    "url": "https://fitzroyacademy.wistia.com/medias/ee8f50jiig",
    "template": "video_wistia",
    "id": "0zg5s4y4g3ynyrk05e1qpf",
    "lesson_id": "l02",
    "course_id": "00",
    "type": "locked"
  },
  {
    "title": "Communicate",
    "duration": "6:26",
    "external_id": "2jlicc2t0e",
    "url": "https://fitzroyacademy.wistia.com/medias/2jlicc2t0e",
    "template": "video_wistia",
    "id": "i6it0ta9sf7s90p8lu3z",
    "lesson_id": "l02",
    "course_id": "00",
    "type": "locked"
  }
]);

courses = [{
    'lessons': [
        {'id': 'l00', 'title': 'How to have good ideas', 'duration': '45:15', 'segments': segments[0], 'active': False},
        {'id': 'l01', 'title': 'How to sell when you hate selling', 'duration': '45:15', 'segments': segments[1], 'active': True},
        {'id': 'l02', 'title': 'Growth forecasting', 'duration': '45:15', 'segments': segments[2], 'active': False}
    ]
}]

def get_segment(sid):
    for l in segments:
        for s in l:
            if s['id'] == sid:
                return models.Segment(sid, s)

def get_lesson(lid):
    return models.Lesson(lid, courses[0]['lessons'][int(lid)])

def get_course(cid):
    return models.Course(cid, courses[int(cid)])
