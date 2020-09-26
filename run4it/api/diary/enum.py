from enum import Enum, unique

@unique
class DiaryEntryType(Enum):
    # Used in DB and in front-end, so DO NOT change the order/values
    Goal = 1
    Workout = 2
    RecordWeek = 3
    RecordMonth = 4
    RecordYear = 5
    RecordDistance = 6
    RecordWorkout = 7

@unique
class DiaryEntryState(Enum):   
    # Used in DB and in front-end, so DO NOT change the order/values
    New = 1
    Updated = 2
    Deleted = 3
    Started = 4
    Progress50 = 5
    Progress100 = 6
    Ended = 7
