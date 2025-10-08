#Python Imports
from dataclasses import dataclass
from pathlib import Path

#Custom Imports
from segment_data import SegmentData

from utilities import langchain_llm
from utilities.few_shot_request_data import FewShotRequestData


m_suffix_variables_names = ["number_of_questions", "text", "keywords"]

m_saqs_few_shot_request_data = FewShotRequestData(
    a_guidance_data_folder_path = Path("../Guidance-Data/SAQs-Generation"),
    a_files_prefix = "SAQs",
    a_suffix_variables_names = m_suffix_variables_names
)

m_gfqs_few_shot_request_data = FewShotRequestData(
    a_guidance_data_folder_path = Path("../Guidance-Data/GFQs-Generation"),
    a_files_prefix = "GFQs",
    a_suffix_variables_names = m_suffix_variables_names
)

m_blqs_few_shot_request_data = FewShotRequestData(
    a_guidance_data_folder_path = Path("../Guidance-Data/BLQs-Generation"),
    a_files_prefix = "BLQs",
    a_suffix_variables_names = m_suffix_variables_names
)

m_mcqs_few_shot_request_data = FewShotRequestData(
    a_guidance_data_folder_path = Path("../Guidance-Data/MCQs-Generation"),
    a_files_prefix = "MCQs",
    a_suffix_variables_names = m_suffix_variables_names
)


@dataclass
class QuestionsGenerationRequestData:

    def __init__(
            self,
            a_question_type: str,
            a_text: str,
            a_keywords: list[str],
            a_number_of_question: int,
            a_llm_name: str,
            a_prefix_index: int,
            a_suffix_index: int,
        ):
        
        if (SegmentData.does_question_type_exist(a_question_type) == False):
            return None
        
        self.text = a_text
        self.keywords = a_keywords
        self.number_of_question = a_number_of_question
        self.prefix_index = a_prefix_index
        self.suffix_index = a_suffix_index
        self.question_type = a_question_type

        #I REALLY do not like the if statements, but it will do for now. Too much repetition.
        t_answer_formatter = None
        t_few_shot_request_data = None
        if(a_question_type == SegmentData.saqs_dict_key()):
            print("\nCreating question generation data for SAQs")
            t_answer_formatter = QuestionsGenerationRequestData._format_saqs_answer
            t_few_shot_request_data = m_saqs_few_shot_request_data

        elif (a_question_type == SegmentData.gfqs_dict_key()):
            print("\nCreating question generation data for GFQs")
            t_answer_formatter = QuestionsGenerationRequestData._format_gfq_answer
            t_few_shot_request_data = m_gfqs_few_shot_request_data

        elif (a_question_type == SegmentData.blqs_dict_key()):
            print("\nCreating question generation data for BLQs")
            t_answer_formatter = QuestionsGenerationRequestData._format_blqs_answer
            t_few_shot_request_data = m_blqs_few_shot_request_data

        elif (a_question_type == SegmentData.mcqs_dict_key()):
            print("\nCreating question generation data for MCQs")
            t_answer_formatter = QuestionsGenerationRequestData._format_mcqs_answer
            t_few_shot_request_data = m_mcqs_few_shot_request_data

        self.llm = langchain_llm.get_generation_llm(a_llm_name, langchain_llm.LLmType.Question)
        self.answer_formatter = t_answer_formatter
        self.few_shot_request_data = t_few_shot_request_data
    
    @classmethod
    def _format_blqs_answer(cls, a_answer: str) -> bool:
        if (isinstance(a_answer, bool) == True):
            return a_answer
        
        t_answer = ""
        if (isinstance(a_answer, list) == True):
            t_answer = str(a_answer[0]).lower()
        else:
            t_answer = a_answer.strip().lower()

        if ("t" in t_answer.lower()):
            t_answer = True
        elif ("f" in t_answer.lower()):
            t_answer = False
        else: 
            #TODO consider deleting this question.
            print(f"The BLQ answer: {t_answer} could not be parsed. Setting the answer to be None")
            t_answer = None

        return t_answer
    
    @classmethod
    def _format_gfq_answer(cls, a_answer: str) -> str:
        if (isinstance(a_answer, list) == True):
            return a_answer
        
        t_answers = a_answer.split(",")
        for i, t_answer in enumerate(t_answers):
            t_answers[i] = t_answer.strip()

        return t_answers

    @classmethod
    def _format_mcqs_answer(cls, a_answer: str) -> list[str]:
        if (isinstance(a_answer, list) == True):
            return a_answer
        
        print(f"MCQ Answer Before: {a_answer}")
        t_answers = a_answer.strip().split(", ")
        for i, t_answer in enumerate(t_answers):
            t_answers[i] = t_answer.strip()

        print(f"MCQ Answer After: ")
        print(t_answers)

        if(len(t_answers) < 4):
            print("Warning, The number of answers generated for the MCQ is LESS than 4.")
            print(t_answers)
        
        if(len(t_answers) > 4):
            print("Warning, The number of answers generated for the MCQ is GREATER than 4.")
        
        return t_answers
    
    @classmethod 
    def _format_saqs_answer(cls, a_answer: str) -> str:
        if (isinstance(a_answer, str) == True):
            return a_answer
    
        if (isinstance(a_answer, list) == True):
            return ", ".join(a_answer)
        
        return str(a_answer)