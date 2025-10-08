#Python Imports
from dataclasses import asdict
from pathlib import Path
import json

from segment_data import SegmentData

#Question Imports
from questions.question_data import QuestionData
from questions.questions_generation_request_data import QuestionsGenerationRequestData

#Utility Imports
from utilities import langchain_llm
from utilities.few_shot_request_data import FewShotRequestData


m_questions_format_few_shot_request = FewShotRequestData(
    a_guidance_data_folder_path = Path("../Guidance-Data/Questions-Formatting"),
    a_files_prefix = "Questions-Formatting",
    a_suffix_variables_names = ["text"]
)

def generate(
        a_generation_request_data: QuestionsGenerationRequestData
) -> list[QuestionData]:
    if (SegmentData.does_question_type_exist(a_generation_request_data.question_type) == False):
        return None
    pass

    t_generation_suffix = a_generation_request_data.few_shot_request_data.suffix_templates[a_generation_request_data.suffix_index].format(
        text = a_generation_request_data.text,
        keywords = ", ".join(a_generation_request_data.keywords),
        number_of_questions = a_generation_request_data.number_of_question
    )
    t_generation_response = a_generation_request_data.few_shot_request_data.send_request(
        a_prefix_index = a_generation_request_data.prefix_index,
        a_suffix = t_generation_suffix,
        a_llm = a_generation_request_data.llm
    ).replace("\"", "'").replace("{", "{{").replace("}", "}}")

    print("\nRaw Questions Response:")
    print(t_generation_response)

    t_formatting_suffix = m_questions_format_few_shot_request.suffix_templates[0].format(text = t_generation_response)
    t_formatting_response = m_questions_format_few_shot_request.send_request(
        a_prefix_index = 0,
        a_suffix = t_formatting_suffix,
        a_llm = langchain_llm.questions_formatting_llm
    )

    #dict to list[class]
    t_number_of_formatting_tries = 2
    for i in range(t_number_of_formatting_tries):
        try: 
            print("Converting LLM output to JSON")
            t_response_dict = json.loads(t_formatting_response)
            break #Will only break is json.loads worked.
        except Exception as e: 
            print("\n**Error converting Json into QuestionData**")

            if (i == t_number_of_formatting_tries - 1):
                return []

    
    print("Formatted Questions:")
    print(t_response_dict)
    
    t_questions_and_answers_list = []
    t_number_of_questions: int = 0


    #If empty.
    if t_response_dict == {}:
        return t_questions_and_answers_list #Empty list.
    

    for t_question_and_answer in t_response_dict["response"]:
        t_question = t_question_and_answer[QuestionData.question_dict_key()]
        t_answer = t_question_and_answer[QuestionData.answer_dict_key()]

        if (a_generation_request_data.answer_formatter != None):
            t_answer = a_generation_request_data.answer_formatter(t_answer)

        t_question_and_answer_data = QuestionData(
            question = t_question,
            answer = t_answer
        )
        t_questions_and_answers_list.append(t_question_and_answer_data)

        #Incase more than required questions are generated, end early.
        t_number_of_questions += 1
        if (t_number_of_questions >= a_generation_request_data.number_of_question):
            break

    return t_questions_and_answers_list

def get_all_questions_of_type(a_all_segments_data: list[dict], a_question_type: str) -> list[dict]:
    t_all_questions_of_type: list[dict] = []

    for a_segment_data in a_all_segments_data:
        t_current_questions_of_type: dict = a_segment_data[a_question_type]
        t_all_questions_of_type += t_current_questions_of_type

        #Debug
        print(f"\nQuestions of type {a_question_type} in {str(a_segment_data)}:")
        for i, t_question_set in enumerate(t_current_questions_of_type):
            print(f"{a_question_type.capitalize()} set {i}: {t_question_set}")

    return t_all_questions_of_type
