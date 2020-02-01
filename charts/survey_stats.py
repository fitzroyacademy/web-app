from collections import Counter
from datamodels import SegmentSurveyResponse
from datamodels.enums import SurveyTypeEnum


def get_survey_statistics(survey):
    responses = SegmentSurveyResponse.objects().filter(SegmentSurveyResponse.survey == survey)
    course = survey.lesson.course
    number_of_students = len(course.students)
    base_stats = {"number_of_responses": responses.count(),
                  "number_of_students": number_of_students,
                  "responses": {}
                  }
    survey_id = survey.get_questions_template().get("survey_id", "")
    survey_template = survey.get_base_template_by_id(survey_id)

    if survey.survey_type == SurveyTypeEnum.plain_text:
        return base_stats
    elif survey.survey_type in [SurveyTypeEnum.emoji, SurveyTypeEnum.points_scale]:
        cnt = Counter()
        for response in responses:
            try:
                cnt[response.get_response_dict()["chosen_answer"]] += 1
            except KeyError:
                pass

        if survey.survey_type == SurveyTypeEnum.emoji:
            for question in survey_template["choice_questions"]:
                base_stats["responses"][question["id"]] = cnt.get(question["id"], 0)
        else:
            for i in range(survey_template["scale_start"], survey_template["scale_stop"]):
                base_stats["responses"][str(i)] = cnt.get(str(i), 0)
        return base_stats
