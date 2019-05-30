# flask-frontend

Simple staging ground for our UX templates.

# Structure and taxonomy:

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

### Access codes

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
* Resources

## Lessons resources:

## Segment

Segments are the chunks of video or text, which students watch / complete within lessons. Each has:

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
* Survey

### Segment types

Segments are of different types to indicate to the user their utility, i.e. a "practical video" is a screengrab of someone using a spreadsheet, wheras a "bonus" video is a nice extra and not needed to complete the course.

* Video
	* Intro
	* Resource
	* Standard
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


### Questionnaires

The options for surveys / questionnaires are:

* 1-6 happiness score, plus free text
* 1-10 net promoter score with free text
* boolean "stuck" (stuck or fine), with free text on stuck
* Free text

Each questionnaire part is either "mandatory" or "optional".

---

# Users and permissions

## Users

* UID
* First name
* Last name
* Email
* Phone number
* Date of birth
* Display pic

Everything but UID is optional (woah! really? I think so! Wow.)

## Registered users

* First name
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

Let's mash this against an example lesson with it's translations:

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


In the above case, for som

---

# Lesson resources

Resources are links, text and other stuff the student uses while completing lessons. They're at the `lesson` level within courses.

## Structure:

* Resource links:
	* Title
	* Url
	* Type:
		* google_spreadsheet
		* google_doc
		* google_slide
		* google_picture
		* medium_article
		* pdf
	* Language (EN | KH | PH | etc)
	* Featured (boolean)
* WYSIWYG resource chunk (just a big slab of HTML)

Links are added by pasting a url in the `lesson editor`, the app scrapes the title, figures out the type, and guesses the language. The user can then modify from there.

The `featured` flag means that link will show up in the right hand nav for easy access, while any non-`featured` links and the HTML appear in the main resources pane.

## Uploads?

No controls for uploading file at the moment. We'll let teachers manage that via dropbox, their own hosting, etc. Just links! :)