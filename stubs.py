import random

student_completion =  [
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

students = [
    {
        'first_name': 'Homer',
        'last_name': 'Simpson',
        'password': 'homer',
        'username': 'homer',
        'super_admin': True,
        'email': 'homer@simpsons.com',
        'profile_picture': '/static/assets/stub/homer.png',
        'bio': 'Homer is the Chief Safety Inspector and former power plant operator at the Springfield Nuclear Power Plant',
    },
    {
        'first_name': 'Marge',
        'last_name': 'Simpson',
        'password': 'marge',
        'username': 'marge',
        'email': 'marge@simpsons.com',
        'bio': 'Marge is a homemaker with previous experience as a buisnesswoman and police officer',
        'profile_picture': '/static/assets/stub/marge.png'
    },
    {
        'first_name': 'Bart',
        'last_name': 'Simpson',
        'password': 'bart',
        'username': 'bart',
        'email': 'bart@simpsons.com',
        'profile_picture': '/static/assets/stub/bart.png'
    },
    {
        'first_name': 'Lisa',
        'last_name': 'Simpson',
        'password': 'lisa',
        'username': 'lisa',
        'email': 'lisa@simpsons.com',
        'profile_picture': '/static/assets/stub/lisa.png'
    },
    {
        'first_name': 'Maggie',
        'last_name': 'Simpson',
        'password': 'maggie',
        'username': 'maggie',
        'email': 'maggie@simpsons.com',
        'profile_picture': '/static/assets/stub/maggie.png'
    },
]

segments = [];
segments.append([
    {
        "type": "video",
        "title": "Introduction",
        "duration": "1:12",  # -> duration seconds
        "external_id": "4ub59urk8l",
        "url": "https://fitzroyacademy.wistia.com/medias/4ub59urk8l",
        # language = en
        "id": "seg_a",
        # "order", add
        "template": "video_wistia", # pop
        "lesson_id": '00',  # ignore (matches segment index)
        "course_id": "00"  # ignore (matches segment index)
    },
    {
        "title": "Lesson Resources",
        "duration": "2:36",
        "external_id": "o3lv8dulfk",
        "url": "https://fitzroyacademy.wistia.com/medias/o3lv8dulfk",
        "template": "video_wistia",
        "type": "video",
        "id": "seg_b",
        "lesson_id": '00',
        "course_id": "00"
    },
    {
        "title": "Drawing without words",
        "duration": "8:12",
        "external_id": "yw3rxkapqv",
        "url": "https://fitzroyacademy.wistia.com/medias/yw3rxkapqv",
        "template": "video_wistia",
        "type": "video",
        "id": "seg_c",
        "lesson_id": '00',
        "course_id": "00"
    },  
    {
        "title": "Five designers in a box",
        "duration": "1:36",
        "external_id": "rxty4preej",
        "url": "https://fitzroyacademy.wistia.com/medias/rxty4preej",
        "template": "video_wistia",
        "type": "video",
        "id": "seg_d",
        "lesson_id": '00',
        "course_id": "00"
    },
    {
        "title": "Quiet loud brainstorming",
        "duration": "7:14",
        "external_id": "1aqbgjr5ex",
        "url": "https://fitzroyacademy.wistia.com/medias/1aqbgjr5ex",
        "template": "video_wistia",
        "type": "video",
        "id": "seg_e",
        "lesson_id": '00',
        "course_id": "00"
    },
    {
        "title": "Party in the woods",
        "duration": "2:47",
        "external_id": "7an2f2hf16",
        "url": "https://fitzroyacademy.wistia.com/medias/7an2f2hf16",
        "template": "video_wistia",
        "type": "video",
        "id": "seg_f",
        "lesson_id": '00',
        "course_id": "00"
    },
    {
        "title": "Find your Awe",
        "duration": "7:56",
        "external_id": "te5p2h5muw",
        "url": "https://fitzroyacademy.wistia.com/medias/te5p2h5muw",
        "template": "video_wistia",
        "type": "video",
        "id": "seg_g",
        "lesson_id": '00',
        "course_id": "00"
    },
    {
        "title": "Mulago Fellow",
        "duration": "3:33",
        "external_id": "ja7ph4j22q",
        "url": "https://fitzroyacademy.wistia.com/medias/ja7ph4j22q",
        "template": "video_wistia",
        "type": "video",
        "id": "seg_h",
        "lesson_id": '00',
        "course_id": "00"
    },
    {
        "title": "Literal change of perspective",
        "duration": "4:08",
        "external_id": "ox83pgmd2l",
        "url": "https://fitzroyacademy.wistia.com/medias/ox83pgmd2l",
        "template": "video_wistia",
        "type": "video",
        "id": "seg_i",
        "lesson_id": '00',
        "course_id": "00"
    },
    {
        "title": "Make your own movie soundtrack",
        "duration": "4:15",
        "external_id": "trphfyidmr",
        "url": "https://fitzroyacademy.wistia.com/medias/trphfyidmr",
        "template": "video_wistia",
        "type": "video",
        "id": "seg_j",
        "lesson_id": '00',
        "course_id": "00"
    },
    {
        "title": "Speedriding",
        "duration": "2:46",
        "external_id": "co72ocpe4c",
        "url": "https://fitzroyacademy.wistia.com/medias/co72ocpe4c",
        "template": "video_wistia",
        "type": "video",
        "id": "seg_k",
        "lesson_id": '00',
        "course_id": "00"
    },
    {
        "title": "Historical Mirrors",
        "duration": "5:44",
        "external_id": "az7nj4f6sp",
        "url": "https://fitzroyacademy.wistia.com/medias/az7nj4f6sp",
        "template": "video_wistia",
        "type": "video",
        "id": "seg_l",
        "lesson_id": '00',
        "course_id": "00"
    },
    {
        "title": "Sleep",
        "duration": "5:48",
        "external_id": "bv7fq9cyxx",
        "url": "https://fitzroyacademy.wistia.com/medias/bv7fq9cyxx",
        "template": "video_wistia",
        "type": "video",
        "id": "seg_m",
        "lesson_id": '00',
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
    "lesson_id": "01",
    "course_id": "00",
    "type": "video"
  },
  {
    "title": "Lesson resources",
    "duration": "0:36",
    "external_id": "nrd9n1i0th",
    "url": "https://fitzroyacademy.wistia.com/medias/nrd9n1i0th",
    "template": "video_wistia",
    "id": "seg_o",
    "lesson_id": "01",
    "course_id": "00",
    "type": "video"
  },
  {
    "title": "Prepwork",
    "duration": "3:34",
    "external_id": "ik28rwd8xh",
    "url": "https://fitzroyacademy.wistia.com/medias/ik28rwd8xh",
    "template": "video_wistia",
    "id": "seg_p",
    "lesson_id": "01",
    "course_id": "00",
    "type": "video"
  },
  {
    "title": "The Pipeline",
    "duration": "7:31",
    "external_id": "5qr1imh89q",
    "url": "https://fitzroyacademy.wistia.com/medias/5qr1imh89q",
    "template": "video_wistia",
    "id": "seg_q",
    "lesson_id": "01",
    "course_id": "00",
    "type": "video"
  },
  {
    "title": "Making Contact",
    "duration": "10:23",
    "external_id": "i4fv1tzbke",
    "url": "https://fitzroyacademy.wistia.com/medias/i4fv1tzbke",
    "template": "video_wistia",
    "id": "seg_r",
    "lesson_id": "01",
    "course_id": "00",
    "type": "video"
  },
  {
    "title": "Meeting in person",
    "duration": "5:56",
    "external_id": "8r42r8wd4e",
    "url": "https://fitzroyacademy.wistia.com/medias/8r42r8wd4e",
    "template": "video_wistia",
    "id": "seg_s",
    "lesson_id": "01",
    "course_id": "00",
    "type": "video"
  },
  {
    "title": "Follow up and Routines",
    "duration": "5:23",
    "external_id": "kolppnbfaj",
    "url": "https://fitzroyacademy.wistia.com/medias/kolppnbfaj",
    "template": "video_wistia",
    "id": "seg_t",
    "lesson_id": "01",
    "course_id": "00",
    "type": "video"
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
    "lesson_id": "02",
    "course_id": "00",
    "type": "vide"
  },
  {
    "title": "Lesson Resources",
    "duration": "0:42",
    "external_id": "bftwqod4cr",
    "url": "https://fitzroyacademy.wistia.com/medias/bftwqod4cr",
    "template": "video_wistia",
    "id": "bpp1dfgexztukgyhdrqvk",
    "lesson_id": "02",
    "course_id": "00",
    "type": "vide"
  },
  {
    "title": "The Big numbers",
    "duration": "6:12",
    "external_id": "tsni6veh6m",
    "url": "https://fitzroyacademy.wistia.com/medias/tsni6veh6m",
    "template": "video_wistia",
    "id": "2plze9cgsb2ifhwb0ai9da",
    "lesson_id": "02",
    "course_id": "00",
    "type": "video"
  },
  {
    "title": "Adding detail",
    "duration": "8:17",
    "external_id": "nleir20ny1",
    "url": "https://fitzroyacademy.wistia.com/medias/nleir20ny1",
    "template": "video_wistia",
    "id": "sj93fnzjlef0mvhaoiolb1s",
    "lesson_id": "02",
    "course_id": "00",
    "type": "video"
  },
  {
    "title": "Do some maths",
    "duration": "12:24",
    "external_id": "jgqhh7dogk",
    "url": "https://fitzroyacademy.wistia.com/medias/jgqhh7dogk",
    "template": "video_wistia",
    "id": "nu9dmhwz7gsr4edpsrac1",
    "lesson_id": "02",
    "course_id": "00",
    "type": "video"
  },
  {
    "title": "Formatting",
    "duration": "3:57",
    "external_id": "13juax70dj",
    "url": "https://fitzroyacademy.wistia.com/medias/13juax70dj",
    "template": "video_wistia",
    "id": "ouvwnfb2zz89vzag7l6jv",
    "lesson_id": "02",
    "course_id": "00",
    "type": "video"
  },
  {
    "title": "Benchmark the results",
    "duration": "5:21",
    "external_id": "z32ayrtmdo",
    "url": "https://fitzroyacademy.wistia.com/medias/z32ayrtmdo",
    "template": "video_wistia",
    "id": "ptrrx6iowybe0ppxwv0wmq",
    "lesson_id": "02",
    "course_id": "00",
    "type": "video"
  },
  {
    "title": "Growth levers",
    "duration": "5:15",
    "external_id": "ee8f50jiig",
    "url": "https://fitzroyacademy.wistia.com/medias/ee8f50jiig",
    "template": "video_wistia",
    "id": "0zg5s4y4g3ynyrk05e1qpf",
    "lesson_id": "02",
    "course_id": "00",
    "type": "video"
  },
  {
    "title": "Communicate",
    "duration": "6:26",
    "external_id": "2jlicc2t0e",
    "url": "https://fitzroyacademy.wistia.com/medias/2jlicc2t0e",
    "template": "video_wistia",
    "id": "i6it0ta9sf7s90p8lu3z",
    "lesson_id": "02",
    "course_id": "00",
    "type": "video"
  }
]);

lessons = [
    {
        'id': '00', # pop
        'course_id': '00', # pop
        'slug': 'how-to-have-good-ideas',
        'title': 'How to have good ideas',
        'segments': segments[0],
        'active': True,
        'resources': [
            {
                'id': 'res_a', # -> slug
                'title': 'Good ideas reference sheet',
                'type': 'google_doc',
                'lang': 'en', # -> language
                'featured': True,
                'url':'https://docs.google.com/document/d/1rQkOtFhmFFHzEizFJXpdvU4M1YGez5jIsXUHWpKyif4/edit#heading=h.i32sbgppwg0k'
            }
        ]
    },
    {
        'id': '01',
        'slug': 'how-to-sell-when-you-hate-selling',
        'course_id': '00',
        'title': 'How to sell when you hate selling',
        'segments': segments[1],
        'active': True,
        'resources': [
            {
                'id': 'res_b',
                'title': 'Sales template',
                'type': 'google_doc',
                'lang': 'en',
                'featured': True,
                'url':'https://docs.google.com/document/d/1damO0yDb7nOR9QpGf1a9l1jkukPVwrS7I6LvQgUQI-c/edit#'
            },
            {
                'id': 'res_c',
                'title': 'Pipeline template',
                'type': 'google_sheet',
                'lang': 'en',
                'featured': True,
                'url':'https://docs.google.com/spreadsheets/d/17SPW-Cicm8bA5-646HgRGLBUJ0yYX_pZO9l3UrY2imA/edit#gid=0'
            }
        ]
    },
    {
        'id': '02',
        'slug': 'growth-forecasting',
        'course_id': '00',
        'title': 'Growth forecasting',
        'segments': segments[2],
        'active': True,
        'resources': [
            {
                'id': 'res_d',
                'title': 'Profit share example',
                'type': 'google_sheet',
                'lang': 'en',
                'featured': True,
                'url':'https://docs.google.com/spreadsheets/d/1Bi0XAfmM8bJqAamdEPqqtuwLDPDbKYsCDrG9GCnlU2w/copy'
            },
            {
                'id': 'res_e',
                'title': 'Profit share with scenarios',
                'type': 'google_sheet',
                'lang': 'en',
                'featured': True,
                'url':'https://docs.google.com/spreadsheets/d/1N1qUDM1jprc1nAol1AYyQd67QZMurkrCeDn7S7uc9PU/copy'
            },
            {
                'id': 'res_f',
                'title': 'Service business model',
                'type': 'google_sheet',
                'lang': 'en',
                'featured': True,
                'url': 'https://docs.google.com/spreadsheets/d/1-UVn_wYQVMvFFMOuy0Rnq63DKVrLwn3Y7gnhlui48-M/copy'
            },
            {
                'id': 'res_g',
                'title': 'SaaS business model',
                'type': 'google_sheet',
                'lang': 'en',
                'featured': True,
                'url': 'https://docs.google.com/spreadsheets/d/1jrVQ32p_Qq3zG_Phg6MLysIbqotmxefto92zgz_RdgE/copy'
            }
        ]
    }
]



courses = [{
    'lessons': [
        lessons[0],
        lessons[1],
        lessons[2]
    ]
}]
