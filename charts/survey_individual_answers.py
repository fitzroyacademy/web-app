from datamodels import SegmentSurveyResponse
from datamodels.enums import SurveyTypeEnum


def get_survey_individual_responses(survey):
    temp = []
    if survey.survey_type in [SurveyTypeEnum.plain_text, SurveyTypeEnum.emoji, SurveyTypeEnum.points_scale]:
        responses = SegmentSurveyResponse.objects().filter(SegmentSurveyResponse.survey == survey)
        course = survey.lesson.course
        for response in responses:
            answer = response.get_response_dict()
            temp.append({
                "free_text_response": answer.get("free_text_response", ""),
                "user_fullname": "{} {}".format(response.user.first_name, response.user.last_name),
                "avatar_url": response.user.profile_picture_url,
                "is_teacher": response.user.teaches(course),
                "chosen_answer": answer.get("chosen_answer", "").split("_")[-1]
            })

    return temp
