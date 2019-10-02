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
