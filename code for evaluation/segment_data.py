#Python Imports
from dataclasses import dataclass, field

#Custom Imports
from questions.question_data import QuestionData

@dataclass
class SegmentData:
    transcript: str
    summary: str = ""

    generated_transcript_keywords: dict = field(default_factory = dict)
    generated_summary_keywords: dict = field(default_factory = dict)
    
    saqs: list[QuestionData] = field(default_factory = list)
    saqs_keywords: dict = field(default_factory = dict)

    mcqs: list[QuestionData] = field(default_factory = list)
    mcqs_keywords: dict = field(default_factory = dict)

    gfqs: list[QuestionData] = field(default_factory = list)
    gfqs_keywords: dict = field(default_factory = dict)

    blqs: list[QuestionData] = field(default_factory = list)
    blqs_keywords: dict = field(default_factory = dict)


    @classmethod
    def question_types(cls) -> list[str]:
        return [cls.saqs_dict_key(), cls.gfqs_dict_key(), cls.blqs_dict_key(), cls.mcqs_dict_key()]
    
    @classmethod
    def does_question_type_exist(cls, a_question_type: str) -> bool:
        if (a_question_type not in cls.question_types()):
            print(f"Provide a valid question type. All Question types: {', '.join(SegmentData.question_types())}")
            return False
        
        return True
    
    @classmethod
    def question_keyword_types(cls) -> list[str]:
        return [cls.saqs_keywords_dict_key(), cls.mcqs_keywords_dict_key(), cls.blqs_keywords_dict_key(), cls.gfqs_keywords_dict_key()]
    
    @classmethod
    def does_question_keyword_type_exist(cls, a_question_keyword_type: str) -> bool:
        if (a_question_keyword_type not in cls.question_keyword_types()):
            print(f"Provide a valid question keyword type. All Question keyword types: {', '.join(SegmentData.question_keyword_types())}")
            return False
        
        return True
    
    
    #Ideally should have used constants
    @classmethod
    def transcript_dict_key(cls) -> str:
        return "transcript"
    
    @classmethod
    def summary_dict_key(cls) -> str:
        return "summary"
    
    @classmethod
    def transcript_keywords_dict_key(cls) -> str:
        return "transcript_keywords"

    @classmethod
    def generated_transcript_keywords_dict_key(cls) -> str:
        return "generated_transcript_keywords"
    
    @classmethod
    def summary_keywords_dict_key(cls) -> str:
        return "summary_keywords"

    @classmethod
    def generated_summary_keywords_dict_key(cls) -> str:
        return "generated_summary_keywords"
    
    @classmethod
    def saqs_dict_key(cls) -> str:
        return "saqs"
    
    @classmethod
    def saqs_keywords_dict_key(cls) -> str:
        return "saqs_keywords"
    
    @classmethod
    def gfqs_dict_key(cls) -> str:
        return "gfqs"
    
    @classmethod
    def gfqs_keywords_dict_key(cls) -> str:
        return "gfqs_keywords"
    
    @classmethod
    def blqs_dict_key(cls) -> str:
        return "blqs"
    
    @classmethod
    def blqs_keywords_dict_key(cls) -> str:
        return "blqs_keywords"
    
    @classmethod
    def mcqs_dict_key(cls) -> str:
        return "mcqs"
    
    @classmethod
    def mcqs_keywords_dict_key(cls) -> str:
        return "mcqs_keywords"