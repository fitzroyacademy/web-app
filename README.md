# Fitzroy Academy [![CircleCI](https://circleci.com/gh/fitzroyacademy/web-app.svg?style=svg&circle-token=675ba8fe3f8f5e094cbeafdf5b054724851864a0)](https://circleci.com/gh/fitzroyacademy/web-app)

The new LMS for Fitzroy Academy!

Bugs and issues go here: [https://github.com/fitzroyacademy/web-app/issues](https://github.com/fitzroyacademy/web-app/issues)

# When setting up the site on a new mac:

First up, clone the repo into a directory somewhere, e.g. `~/dev/web-app`

Then, install a bunch of basic stuff:

```
xcode-select --install
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"

brew install node
brew upgrade openssl
brew install postgresql
npm install sass -g

export LIBRARY_PATH=$LIBRARY_PATH:/usr/local/opt/openssl/lib/

python3 -m venv env
```

Add this to `~/.bash_profile`

```
# this stuff is for the Fitzroy python app
export LIBRARY_PATH=$LIBRARY_PATH:/usr/local/opt/openssl/lib/
export PATH="~/.composer/vendor/bin/:$PATH"export FLASK_ENV=development
source /Users/willdayble/dev/web-app/env/bin/activate
```

# Local Installation

This application requires Python 3 to work as well as the libraries listed in requirements.txt.

## Manual Installation

Assuming a Python 3 installation, typing this should work.

```
pip3 install -r ./requirements.txt 
export FLASK_ENV=development
python3 app.py
```

## Restarting the app, assuming everything is installed:

```
source ./env/bin/activate
python3 app.py
```

To reseed the DB - this takes everything from `stubs.py` and puts it in the database `dev_db.sqlite`, which is our local databse:

* To change the database, edit `stubs.py`, and rm `dev_db.sqlite`
* Ensure your virtualenv is active and packages are installed, then `flask utils reseed-database` to reseed from stubs
* Then reset the app via `python3 app.py`
* Then hit [localhost:5000](http://localhost:5000).
* For an example lesson: [http://localhost:5000/course/fitzroy-academy/how-to-have-good-ideas/seg_a](http://localhost:5000/course/fitzroy-academy/how-to-have-good-ideas/seg_a)

Here's the reseed code on all one line for copy/pasting:

```
rm dev_db.sqlite; flask utils reseed-database; python3 app.py
```

### To make the SCSS work:

```
sass --watch static/assets/scss/fit.scss static/css/fit.css
```

### To make the subdomains work:

In your `/etc/hosts` file add the following lines:
```
127.0.0.1 fitz-dev.com
127.0.0.1 jeditemple.fitz-dev.com
127.0.0.1 some_fancy_subdomain.fitz-dev.com
...
```

Having such entries in `hosts` file, the following urls are valid:
```
fitz-dev.com
jeditemple.fitz-dev.com
some_fancy_subdomain.fitz-dev.com
```

Note that for local development two domains are obligatory in `hosts` file, namely `fitz-dev.com` and `jeditemple.fitz-dev.com`

### To add issues to Github:

[https://github.com/fitzroyacademy/web-app/issues](https://github.com/fitzroyacademy/web-app/issues)

## Docker Installation

There's also a Dockerfile for your convenience which can be used instead. All of the application code, including Sass, will be live-reloaded if you edit any files locally with the Docker container running.

From the root repository directory, type:

```
docker build -t fitzroy-academy .
docker run -p 5000:5000 -e FLASK_ENV=development fitzroy-academy
```

Server will then be available here: [localhost:5000](http://localhost:5000)
Example lesson will be available here: [localhost:5000/course_intro/01](localhost:5000/course_intro/01)

## Docker-compose

There is also a docker-compose.yml file which launches an instance of the app and a Postgres database.

### Building and running docker-compose
When you change requirements.txt, you will need to rebuild the containers before running like so:
```
docker-compose build
docker-compose up # add -d to detach
```

### Stopping docker-compose
```
docker-compose down
```

### Seeding the DB while using docker-compose
While docker-compose is running:
```
docker exec -it $(docker ps -f name="fitzroy-academy-app" -q) flask utils reseed-database
```

### Connecting to the docker-compose DB locally
You can open a [psql](https://www.postgresql.org/docs/8.3/tutorial-accessdb.html) shell like the following:
```
docker exec -it $$(docker ps -f name="postgres" -q) psql -U postgres
```
If docker-compose is running, it will also be available via localhost on port 5001.

## Reseeding the DB in docker-compose

The previous method will work for both Docker and non-Docker local development with sqlite. If you're using docker-compose, you will need to run the script on the application container:
```
docker exec -it $(docker ps -f name="fitzroy-academy" -q) flask utils reseed-database
```

## Cleaning out the docker-compose Postgres db (to start fresh):
1. Ensure the containers aren't running (`docker-compose down` and `docker ps`)
1. Run `docker volume list`, and find the postgres-container volume (should be like `web_app_dbdata`)
2. Run `docker volume rm [volume name]`

## Database migrations

We use [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/) (Alembic) for database migrations. There are instructions on their page on how to use it properly, but here are the important ones when making DB changes:
```
flask db migrate [--message MESSAGE] [--sql] [--head HEAD] [--splice] [--branch-label BRANCH_LABEL] [--version-path VERSION_PATH] [--rev-id REV_ID]
```
> Equivalent to revision --autogenerate. The migration script is populated with changes detected automatically. The generated script should to be reviewed and edited as not all types of changes can be detected automatically. This command does not make any changes to the database, just creates the revision script.

Check in your changes and migrations as usual in a PR.

---

# Testing, debugging and profiling

You can run tests with `make check` before you might want to run `make format` which will run `black` formatting.

For profiling just run `python3.7 profiler` and you will get 30 most time consuming methods for each request.

# Structure and taxonomy:

Here's the nomenclature and structure for lessons, in hopefully plain English, from top to bottom:

## Institute

E.g. "Monash University", or "SHE Investments"

* UID
* Name
* Subdomain (unique, i.e. schoolname.fitzroyacademy.com)
* Wide logo (image upload, for horizontal logos)
* Square logo (image upload, for links + header)
* Colour choice (hex code)
* One or many *Programs*
* One or many users
	* Institute admins
	* Program managers
	* Teachers (inhereted from programs)

## Program

E.g. "Global Challenges" or "Leave No-one Behind"

* UID
* Banner picture
* One or many *Courses*
* Program managers
* Teachers


## Course

E.g. "Accelerator", or "Global Challenges"

* UID
* Name
* Picture (forced to 16:9, user-uploadable)
* Slug
* Order
* Year: So we're not naming courses "My course 2020" and "my course 2021".
* ID code, for courses with school codes like `SCI2502`
* One or many `Lessons`
* One 16:9 Cover image
* 'Who it's for' (plain text / simple markdown) w/ translations?
* 'Length and workload' (plain text / simple markdown) w/ translations?
* 'What you'll learn (plain text / simple markdown) w/ translations?
* Paid or free (beta = everything is free)
* Access code (optional)
* Guest access? (i.e. can anonymous users access this course?)
* On the home page (i.e. does this show up on the home page?) **NB: This option is only for super admins**
* Parent Institute
* Whitelabel (removes FA branding from course)
* One or many affiliated users with access levels including:
	* Enrolled students
	* Teachers (admins)

### Access codes

These can be set by the admin, and control access via a short code.

* 4+ characters, letters and numbers
* Controls student access
* Most be unique


### Conditional logic for codes:

* Public listed: Shows up on public listings
* Public: Anonymous access allowed
* Public + login --> log in form --> play first lesson
* Public + code --> type in the code --> access
* Public + code + needs login --> type in the code --> check login --> enter course
* Public to certain domain: Needs login with certain domain(s), e.g. @harvard.edu
* Private: Doesn't show up on the site unless you type in the course code.
* Private + Needs login: Doesn't show up on the site unless you type in the course code, AND needs login

This means we have these options in course edit page:

* Listed | Public | Private
* Code (optional)
* Secure by domain(s)
* Featured or not (shows up on home page, only set by superadmin)


#### Domain acccess:

* When teacher is editing a course, can set one or many domains (or subdomains) for access
* Course shows "log in with your @domain email"
* This will require users to confirm their email address - how the hell do we deal with this?


#### Later on: Whitelist

This will require some sort of fancy "invite all these email addresses" thing? Do it later.

Codes are central to user login: They are UIDs for courses. If a teacher wishes to constrain access to a course, they can add a code AND demand that only logged in users can access.

## Lesson

* UID
* Title (short text) w/ translations?
* Image (16:9 ratio)
* Total time (from video segments)
* Order
* Strapline (slightly longer text) w/ translations?
* One or many Segments
* Resources

## Lessons resources:

Resources are links, text and other stuff the student uses while completing lessons. They're at the `lesson` level within courses.

### Resource Translations

A secondary table for translations of default resources is available to provide localized override of all applicable resource data fields.

### Resources structure:

* Resource links:
	* Title
	* Url
	* Type:
		* google_doc
		* google_spreadsheet
		* google_slide
		* google_drawing
		* youtube_video
		* file_pdf
		* file_image (for jpg/gif/etc)
		* file_doc (.doc and .docx etc)		
		* medium_article
		* url
	* Language (EN | KH | PH | etc) - can be blank for unset.
	* Featured (boolean)
* WYSIWYG resource chunk (just a big slab of HTML)

Links are added by pasting a url in the `lesson editor`, the app scrapes the title, figures out the type, and guesses the language. The user can then modify from there.

The `featured` flag means that link will show up in the right hand nav for easy access, while any non-`featured` links and the HTML appear in the main resources pane.

### Uploads?

No controls for uploading file at the moment. We'll let teachers manage that via dropbox, their own hosting, etc. Just links! :)

## Segment

Segments are the chunks of video or text, which students watch / complete within lessons. Each has:

* UID
* Title w/ translations?
* Source
* Type
* Time (if source = video)
* Order
* Status
* Language (EN | KH | PH | etc)
* Subtitle languages availabile (EN | KH | PH | etc) (if source = video)
* ???

### Segment Translations

A secondary table for translations of default segments is available to provide localized override of all applicable segment data fields.

### Segment source

Segments can be one of the following types:

* Video (wistia)
* Video (YouTube)
* HTML (i.e. WYSIWYG page)
* Survey

### Segment types

Segments are of different types to indicate to the user their utility, i.e. a "practical video" is a screengrab of someone using a spreadsheet, wheras a "bonus" video is a nice extra and not needed to complete the course.

* Video
	* Intro
	* Standard
	* Resource
	* Practical
	* Story
	* Interview
	* Case
	* Bonus
* HTML
* Survey

**Functionality for segment types:** Type is mostly used just to set the correct icon type, however some functionality will be attached to type.

* `Locked` segments can only be watched after all previous segments are *complete*.
* `Barrier` segments are used for disclaimers, etc, and must be completed before any subsequent segments can be accessed.
* `Hidden` segments are accessible via the backend, but completely hidden to the student (i.e. so a teacher can hide segments without deleting them, and reveal them later)


### Segment statuses

These are changed through student interaction, and indicate progress:

* Untouched (not started or looked at in any way)
* Touched (started but not completed)
* Active (current item)
* Complete

The untouched and touched states are not shown to the student, but are used by teachers and admins.

*Completeness* is set by a % watched on a segment by segment basis.

### Segment languages

#### Video

Lesson creators will have to upload separate videos if they want differently-languaged audio. Each video within a segment may have one or more subtitle languages.

#### Subtitles

For YouTube, the subtitle language can be set in the embed, which should integrate with our preferred `subtitle` language preference; for Wistia, it's based upon the user's browser, with a fallback to the [first availabile language](https://wistia.com/support/player/captions) for the video.

#### HTML/Survey

The text and their translations will be stored in the database.

### Surveys

The options for surveys / questionnaires are:

* 1-6 happiness score, plus free text
* 1-10 net promoter score with free text
* boolean "stuck" (stuck or fine), with free text on stuck
* Free text

Each questionnaire part is either "mandatory" or "optional".

---

# Course permissions

### Managed through escalating "security" levels:

* Publicly accessible
* Locked with `course code`
* Locked with `registered user`
* Locked with `course code` AND `registered user`

And in the future, we will implement:

* Locked to `registered user whitelist` (requires invite codes, argh)
* Locked to `domain` (i.e. only @institute.edu emails, or only @company.com emails)

This is expressed in the course edit with:

* Requires `course code` Y/N
* Requires `registered user` Y/N

---

# Users and permissions

## Users

* UID
* Phone number
* First name
* Last name
* Primary email
* More emails
* Date of birth
* Display pic
* Color (randomly chosen from a list)

Everything but UID is optional (woah! really? I think so! Wow.)

## Registered users

* First name
* Last ssname
* Email
* Password

## Extra log in options

* Attach Google account
* Attach Facebook account

We're going to encourage users to log in via Google / FB, and this will attach to whatever email we can snag from that login.

This creates a weird flow: If a user does a Google auth, then later tries to sign in via that email *without* Google, they'll have to a) sign in via Google, or b) do a password reset, as they don't have a password yet.

**NB:** We need to figure out some clever way of allowing users to auth without email, especially in SEA on phones. Eek.

### Anon use case:

For kids (i.e. <16), less technical users, and public courses, it's likely users will *never* make an account with an email. At this point, we need a very simple way to auth them. Could we rember their device fingerprint perhaps? Or let them log back in with their first name and date of birth? Super simple?

We also want anon users to be able to very easily 'upgrade' to a registered user, and keep whatever watch / progress they've completed in a course.


## Permissions

In order, user permissions are:

1) `Super` Dev team / FA staff
2) `Institute` e.g. Melbourne University, or Tondo Foundation
3) `Program` e.g. Leave No-one Behind, or SCI2502
4) `Teacher` e.g. 2021 Summer socent course
5) `Registered` student
6) `Guest` student

Plus the weird, wonderful extra user: `Researcher`!

All admins have full view and edit access to everthing *below* their perm level.

### Use cases

* Both `Guest` and `Registered` users can access locked courses with a `course code`, and the guests appear as "anon" in admin panels
* If a course has the "guest access" flag set to 'no', only registered users can access.
* A `program` admin can create lessons, see all users activity within their program, but not other programs within that institute.
* An `institute` level user can create programs and invite program admins, as well as dive into programs, lessons, etc, with full edit permissions

### The weird and wonderful `Researcher` (TBC)

**We'll implement this later coz is tricksy.** Researchers exist outside of the typical 'school' structure, and can access anonymised, aggregate data at various levels.

This will be a delicately released feature, because it might expose lots of scary private data if we do it badly. There will probably be huge amounts of logging and tracking on who's seeing which data sets, and what they're doing with it.


---

# Things to remember

For each user, the app should remember certain variables:

### Last viewed/watched:

* Course level (left side menu):
	* Overall hiding
	* Which segments are completed or not
	* Current, active segment
	* Last segment viewed, within a lesson
	* Last MM:SS viewed of the last viewed lesson
	* Last course viewed (inherited by the lesson, above)
* Main viewing pane (segment level):
	* Resources
	* FAQs
	* Transcript
	* Teacher
	* Analytics (admins only)
* Lesson level (sidebar on the right):
	* Overall hiding
	* Resources
	* FAQs
	* Transcript
	* Teacher
	* Analytics (admins only)

Other user preferences:

* Selected `app` language (buttons etc)
* Display subtitles or not
* Preferred `video` language
* Preferred `subtitle` language
* Preferred `transcript` language

The above means that the app will attempt to find the preferred video and transcript language, and display that, or fall back to English.

This means a Cambodia user could choose an `app language` of `KH`, while watching videos in `EN`, with subtitles displayed in `KH`, and just for fun, `transcripts` in `EN`.

The above example has Khmer buttons, English spoken in the videos with Khmer subtitles, while reading transcripts happens in English. ARGH!

---

# Translation

We translate the app at these levels:

* Overall chrome, i.e. app buttons / labels / etc
* Lesson level
	* Resources
	* FAQs
	* Teacher
	* Segment
		* Video
		* Transcript
		* Survey

English is our fallback language. If a 'preferred' language is unvailable, fall back to English. This means some parts of a lesson may _or may not_ be transcribed.

## Example: Partially translated lesson.

**KH** means Khmer, **EN** means English, **PH** means Tagolog:


### Example user preferences:

* Selected `app` language: **KH**
* Display subtitles or not **Yes**
* Preferred `video` language **KH**
* Preferred `subtitle` language **EN**
* Preferred `transcript` language **EN**

The above might read as _"I speak Khmer as a first language, but want to see subtitles and read transcripts in English, to improve my English."_

Let's mash this against an example lesson with its translations:

### Example translations available:

* Overall chrome: KH / EN / PH
* Lesson level
	* Resources: EN
	* FAQs: EN / KH
	* Teacher: EN / KH
	* Segment 1
		* Video: EN
		* Transcript
	* Segment 2
		* Video: EN
		* Transcript: EN
	* Segment 3
		* Video: EN
		* Transcript: EN / KH

---


## Will's foolish notes and design ideas:

### Domains:

* fitzroy.tech
* fitzroy.space
* fitzroy.design
* fitzroy.academy
* fitzroy.io


# How to define future features

* Brainstorm feature with everyone
* Wireframe all the bits
* Wireframe all the bits

1. Do a blog post with screen shots
2. Show it to `dev` to see how hard it is
3. Change blog post until people are happy
4. Do wireframes in XD or paper
5. ???


### Add Youtube as a video type

* As a course editor I want to add youtube link as a video segment type
* As a course viewer I want to watch a youtube video
* As a analytics viewer I want to watch a youtube video

Bits:

* Biz logic
* User stories
* Brainstorm
* Wireframe
* Time budget


### Day 1: Retro

* What happened last sprint?
* Check error bars for last months retro
* Reprioritising existing features
* Change processes?
* Stakeholder update

### Day 1.5: Ideas + snacks (together)

* Debate this months work
* Write / update blog posts for next months

### Day 3: Research + rethink (small group)

* Figure out hourly estimates for defined features
* Any curly problems noted down
* Backlog grooming
* Tech debt
* Cheap wireframing

### Day 4: Refine the scope

* Present ideas and problems (what we learned)
* Match stories with hourly budget
* Prioritise tasks
* Put all the tickets in
* Make tickets + assignemnt make sense

### More stuff

* Updates from the boss on what else is going on


### Will, think about:

* What stuff do I want the app to do before this month?
* Testing: Do one day, or 2x .5 days
* Role based testing for a few days?
* See how much is left to burnt?
* Tech debt?








