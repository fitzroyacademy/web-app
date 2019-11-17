import enum


class VideoTypeEnum(enum.Enum):
    standard = "standard"
    resources = "resources"
    practical = "practical_example"
    interview = "interview"
    case = "case_study"
    story = "story"
    bonus = "bonus"


class SegmentPermissionEnum(enum.Enum):
    normal = "normal"  # Normal Can be skipped
    barrier = "barrier"  # Soft barrier Only this segment must be completed to continue (but not previous)
    hard_barrier = "hard barrier"  # Hard barrier This and every prior segment must be completed to continue
    hidden = "hidden"  # Hidden Not shown to students, visible only to teachers


class ResourceTypeEnum(enum.Enum):
    google_doc = "Google doc"
    google_sheet = "Google spreadsheet"
    google_slide = "Google slide"
    google_drawing = "Google drawing"
    youtube = "YouTube Video"
    pdf = "PDF file"
    file_generic = "File (generic)"
    image = "Image"


RESOURCE_CONTENT_IMG = {
    "google_doc": "fal fa-file-alt",
    "google_sheet": "fal fa-file-spreadsheet",
    "google_slide": "fal fa-presentation",
    "google_drawing": "fal fa-image",
    "youtube": "fab fa-youtube",
    "pdf": "fal fa-file-pdf",
    "file_generic": "fal fa-file",
    "image": "fal fa-camera",
}


class InstitutePermissionEnum(enum.Enum):
    admin = "Administrator"
    manager = "Program manager"
    teacher = "Teacher"
