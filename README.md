# flask-frontend

Simple staging ground for our UX templates.

# Structure and language!

Here's the nomenclature and structure for lessons, in hopefully plain English, from top to bottom:

## Institute

* UID
* Name
* Logo
* Colour choice
* One or many *Programs*
* *Administrator* user

## Program

* UID
* One or many *Courses*
* *Program* administrator

## Course

* UID
* Name
* Slug
* Order
* Year: So we're not naming courses "My course 2020" and "my course 2021".
* ID code, for courses with school codes like `SCI2502`
* One or many `Lessons`
* Students enrolled
* One or many Teachers (admins)
* One 16:9 Cover image
* 'Who it's for' (plain text / simple markdown)
* 'Length and workload' (plain text / simple markdown)
* 'What you'll learn (plain text / simple markdown)
* Paid or free (beta = everything is free)
* Access code (optional)
* Guest access? (i.e. can anonymous users access this course?)
* Parent Institute
* Enrolled students

### Access codes:

These can be set by the admin, and control access via a code.

* 6+ characters
* Controls student access

## Lesson

* UID
* Title (short text)
* Image (16:9 ratio)
* Total time (from video segments)
* Order
* Strapline (slightly longer text)
* One or many Segments

## Segment

Segments are the chunks of video or text, which students watch / complete. Each has:

* UID
* Title
* Source
* Type
* Time (if source = video)
* Order
* Status
* ???

### Segment source

Segments can be one of the following types:

* Video (wistia)
* Video (YouTube)
* HTML (i.e. WYSIWYG page)
* Questionnaire

### Segment types

Segments are of different types to indicate to the user their utility, i.e. a "practical video" is a screengrab of someone using a spreadsheet, wheras a "bonus" video is a nice extra and not needed to complete the course.

* Video
	* Introduction
	* Standard
	* Practical
	* Story
	* Case study
	* Bonus
* Text
* Questionnaire
* Barrier
* Locked
* Hidden

**Functionality for segment types:** Type is mostly used just to set the correct icon type, however some functionality will be attached to type.

* `Locked` segments can only be watched after all previous segments are *complete*.
* `Barrier` segments are used for disclaimers, etc, and must be completed before any subsequent segments can be accessed.
* `Hidden` segments are accessible via the backend, but hidden to the student (i.e. so a teacher can hide segments without deleting them, and reveal them later)


### Segment statuses

These are changed through student interaction, and indicate progress:

* Untouched (not started or looked at in any way)
* Touched (started but not completed)
* Active (current item)
* Complete

The untouched and touched states are not shown to the student, but are used by teachers and admins.

*Completeness* is set by a % watched on a segment by segment basis.


### Questionnaires

The options for surveys / questionnaires are:

* 1-6 happiness score, plus free text
* 1-10 net promoter score with free text
* boolean "stuck" (stuck or fine), with free text on stuck
* Free text

Each questionnaire part is either "mandatory" or "optional".

---

# Users and permissions

## Users have:

* UID
* First name
* Last name
* Email (optional)
* Phone number
* Display pic

## Extra log in options:

* Attach Google account
* Attach Facebook account

We're going to encourage users to log in via Google / FB, and this will attach to whatever email we can snag from that login.

**NB:** We need to figure out some clever way of allowing users to auth without email, especially in SEA on phones. Eek.

### Anon use case:

For kids (i.e. <16), less technical users and public courses, it's likely they will never make an account with an email. At this point, we need a very simple way to auth them. Could we rember their device fingerprint perhaps?

We also want anon users to 'upgrade' to a registered user easily, and keep whatever watch / progress they've completed in a course.


## Permissions

In order, user permissions are:

1) `Super` Dev team / FA staff
2) `Institute` e.g. Melbourne University, or Tondo Foundation
3) `Program` e.g. Leave No-one Behind, or SCI2502
4) `Teacher` e.g. 2021 Summer socent course
5) `Registered` student
6) `Guest` student

Plus the weird, wonderful extra user: `Researcher`!

All admins have full view and edit access to everthing *below*.

### Use cases:

* Both `Guest` and `Registered` users can access locked courses with a `course code`, the guests appear as "anon" in admin panels
* If a course has the "guest access" flag set to 'no', only registered users can access.
* A `program` admin can create lessons, see all users activity within their program, but not other programs within that institute.
* An `institute` level user can create programs and invite program admins, as well as dive into programs, lessons, etc, with full edit permissions

### The weird and wonderful `Researcher` 

We'll implement this later. Researchers exist outside of the typical 'school' structure, and can access anonymised, aggregate data at various levels.

This will be a super careful feature, because it might expose lots of scary private data if we do it badly. 

There will probably be huge amounts of logging and tracking on who's seeing which data sets, and what they're doing with it.