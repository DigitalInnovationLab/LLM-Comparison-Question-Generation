#Python Imports
from dataclasses import dataclass, field

#Custom Imports
from .question_evaluation_data import QuestionEvaluationData

@dataclass
class QuestionData:
    question: str = ""
    answer: str | list[str] | bool | dict = ""
    question_evaluation: QuestionEvaluationData = field(default_factory=lambda: QuestionEvaluationData())

    @classmethod
    def question_dict_key(cls) -> str:
        return "question"
    
    @classmethod
    def answer_dict_key(cls) -> str:
        return "answer"

    @classmethod
    def question_evaluation_dict_key(cls) -> str:
        return "question_evaluation"
