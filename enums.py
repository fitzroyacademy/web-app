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
    normal = "normal"
    barrier = "barrier"
    hidden = "hidden"


class ResourceTypeEnum(enum.Enum):
    google_doc = "Google doc"
    google_sheet = "Google spreadsheet"
    google_slide = "Google slide"
    google_drawing = "Google drawing"
    youtube = "YouTube"
    video = "Video"
    pdf = "PDF file"
    file_generic = "File (generic)"
    image = "Image"
