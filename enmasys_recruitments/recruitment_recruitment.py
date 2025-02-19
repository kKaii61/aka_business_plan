MALE_GENDER = 'male'
FEMALE_GENDER = 'female'
OTHER_GENDER = 'other'
GENDERS = [(MALE_GENDER, "Male"), (FEMALE_GENDER, "Female"), (OTHER_GENDER, "Other")]
IN_REQUEST_STATUS = 'in_request'
IN_RECRUIT_STATUS = 'in_recruit'
DONE_STATUS = 'done'
CANCELLED_STATUS = 'cancelled'
RECRUITMENT_STATUSES = [
    (IN_REQUEST_STATUS, "Requested"), (IN_RECRUIT_STATUS, "In Recruit"),
    (DONE_STATUS, "Done"), (CANCELLED_STATUS, "Cancelled")
]


class RecruitmentRecruitment:
    def __init__(self):
        pass
