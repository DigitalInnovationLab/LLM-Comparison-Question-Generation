#Python Imports
import time
from dataclasses import dataclass, field

#Custom Imports
from questions.evaluation_data import EvaluationData
import evaluation_api as EvaluationAPI

@dataclass
class QuestionEvaluationData:
    #Our custom metrics
    relevance: EvaluationData = field(default_factory=lambda: EvaluationData())
    reading_comprehension: EvaluationData = field(default_factory=lambda: EvaluationData())
    question_difficulty: EvaluationData = field(default_factory=lambda: EvaluationData())
    question_clarity: EvaluationData = field(default_factory=lambda: EvaluationData())
    answer_relevance: EvaluationData = field(default_factory=lambda: EvaluationData())
    answer_correctness: EvaluationData = field(default_factory=lambda: EvaluationData())

    #Ragas metrics
    context_utilisation: EvaluationData = field(default_factory=lambda: EvaluationData())

    generation_time: float = -1

    @staticmethod
    def evaluate_question(
        a_text: str,
        a_ground_truth: list[str],
        a_question: str,
        a_answer: str,
    ):
        t_evaluation_data = QuestionEvaluationData()

        t_start_time = time.time()

        #The EvaluationAPI returns a dict of EvaluationData object, not a EvaluationData object
        
        t_evaluation_data.relevance = EvaluationData.dict_to_object(EvaluationAPI.evaluate_relevance(a_question, a_text))
        t_evaluation_data.reading_comprehension = EvaluationData.dict_to_object(EvaluationAPI.evaluate_reading_comprehension(a_question))
        t_evaluation_data.question_difficulty = EvaluationData.dict_to_object(EvaluationAPI.evaluate_question_difficulty(a_question, a_text))
        t_evaluation_data.question_clarity = EvaluationData.dict_to_object(EvaluationAPI.evaluate_question_clarity(a_question))
        t_evaluation_data.answer_relevance = EvaluationData.dict_to_object(EvaluationAPI.evaluate_answer_relevancy(a_answer, a_ground_truth))
        t_evaluation_data.answer_correctness = EvaluationData.dict_to_object(EvaluationAPI.evaluate_answer_correctness(a_text, a_question, a_answer))

        t_evaluation_data.context_utilisation = EvaluationData.dict_to_object(EvaluationAPI.evaluate_context_utilisation(a_text, a_question, a_answer))
        
        t_end_time = time.time()
        t_evaluation_data.generation_time = round(t_end_time - t_start_time, 3)

        #Debug
        t_scores = [
            t_evaluation_data.relevance.score,
            t_evaluation_data.reading_comprehension.score,
            t_evaluation_data.question_difficulty.score,
            t_evaluation_data.question_clarity.score,
            t_evaluation_data.answer_relevance.score,
            t_evaluation_data.answer_correctness.score,
            t_evaluation_data.context_utilisation.score
        ]
        print(f"Generated Evaluation Score: [{', '.join(map(str, t_scores))}]")
        
        return  t_evaluation_data

    @classmethod
    def relevance_dict_key(cls) -> str:
        return "relevance"
    
    @classmethod
    def reading_comprehension_dict_key(cls) -> str:
        return "reading_comprehension"
    
    @classmethod
    def question_difficulty_dict_key(cls) -> str:
        return "question_difficulty"
    
    @classmethod
    def question_clarity_dict_key(cls) -> str:
        return "question_clarity"
    
    @classmethod
    def answer_relevance_dict_key(cls) -> str:
        return "answer_relevance"
    
    @classmethod
    def answer_correctness_dict_key(cls) -> str:
        return "answer_correctness"
    
    @classmethod
    def context_utilisation_dict_key(cls) -> str:
        return "context_utilisation"
    
    @classmethod
    def generation_time_dict_key (cls) -> str:
        return "generation_time"


        