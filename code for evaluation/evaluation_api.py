#Python Imports
from pathlib import Path
from dataclasses import asdict

#External Imports
from fastapi import FastAPI
import json

from langchain_openai import ChatOpenAI

from datasets import Dataset 
from ragas.metrics import context_utilization
from ragas import evaluate

from dotenv import load_dotenv

#Custom Imports
from utilities.few_shot_request_data import FewShotRequestData
from questions.evaluation_data import EvaluationData


#Setup
load_dotenv()
api = FastAPI(
    title = "i45 Evaluation API",
    summary = "Takes a text and question input to evaluate how good the question is in regards to the text."
)


#Evaluation Variables
m_chatGPT_model_name = "gpt-4o-mini"
m_evaluation_generation_llm = ChatOpenAI(model = m_chatGPT_model_name, max_tokens = "1024", temperature = 0.45)


#Criteria Based Evaluation with FewShot
m_relevance_evaluation_few_shot = FewShotRequestData(
    a_guidance_data_folder_path = Path("../Guidance-Data/Relevance-Evaluation"),
    a_files_prefix = "Relevance",
    a_suffix_variables_names = ["text", "question"]
)
@api.post("/evaluate-relevance")
def evaluate_relevance(
    a_question: str,
    a_text: str
) -> dict: 
    t_suffix = m_relevance_evaluation_few_shot.suffix_templates[0].format(question = a_question, text = a_text)
    t_result: dict = _generate_evaluation(m_relevance_evaluation_few_shot, t_suffix)

    return t_result


m_reading_comprehension_few_shot = FewShotRequestData(
    a_guidance_data_folder_path = Path("../Guidance-Data/Reading-Comprehension"),
    a_files_prefix = "Reading-Comprehension",
    a_suffix_variables_names = ["question"]
)
@api.post("/evaluate-reading-comprehension")
def evaluate_reading_comprehension(
    a_question: str
) -> dict: 
    t_suffix = m_reading_comprehension_few_shot.suffix_templates[0].format(question = a_question)
    t_result: dict = _generate_evaluation(m_reading_comprehension_few_shot, t_suffix)

    return t_result


m_question_difficulty_few_shot = FewShotRequestData(
    a_guidance_data_folder_path = Path("../Guidance-Data/Question-Difficulty-Evaluation"),
    a_files_prefix = "Question-Difficulty",
    a_suffix_variables_names = ["text", "question"]
)
@api.post("/evaluate-question-difficulty")
def evaluate_question_difficulty(
    a_question: str,
    a_text: str
) -> dict: 
    t_suffix = m_question_difficulty_few_shot.suffix_templates[0].format(question = a_question, text = a_text)
    t_result: dict = _generate_evaluation(m_question_difficulty_few_shot, t_suffix)

    return t_result


m_question_clarity_few_shot = FewShotRequestData(
    a_guidance_data_folder_path = Path("../Guidance-Data/Question-Clarity-Evaluation"),
    a_files_prefix = "Question-Clarity",
    a_suffix_variables_names = ["question"]
)
@api.post("/evaluate-question-clarity")
def evaluate_question_clarity(
    a_question: str,
) -> dict: 
    t_suffix = m_question_clarity_few_shot.suffix_templates[0].format(question = a_question)
    t_result: dict = _generate_evaluation(m_question_clarity_few_shot, t_suffix)

    return t_result


m_answer_relevancy_few_shot = FewShotRequestData(
    a_guidance_data_folder_path = Path("../Guidance-Data/Answer-Relevancy-Evaluation"),
    a_files_prefix = "Answer-Relevancy",
    a_suffix_variables_names = ["answer", "ground_truth"]
)
@api.post("/evaluate-answer-relevancy")
def evaluate_answer_relevancy(
    a_answer: str,
    a_ground_truth: str
) -> dict: 
    t_suffix = m_answer_relevancy_few_shot.suffix_templates[0].format(answer = a_answer, ground_truth = a_ground_truth)
    t_result: dict = _generate_evaluation(m_answer_relevancy_few_shot, t_suffix)

    return t_result


m_answer_correctness_few_shot = FewShotRequestData(
    a_guidance_data_folder_path = Path("../Guidance-Data/Answer-Correctness-Evaluation"),
    a_files_prefix = "Answer-Correctness",
    a_suffix_variables_names = ["text", "question", "answer"]
)
@api.post("/evaluate-answer-correctness")
def evaluate_answer_correctness(
    a_text: str,
    a_question: str, 
    a_answer: str,
) -> dict:
    t_suffix = m_answer_correctness_few_shot.suffix_templates[0].format(answer = a_answer, question = a_question, text = a_text)
    t_result: dict = _generate_evaluation(m_answer_correctness_few_shot, t_suffix)
    
    return t_result


@api.post("/evaluate-context-utilisation")
def evaluate_context_utilisation(
    a_text: str,
    a_question: str,
    a_answer: str
) -> dict:
    if (isinstance(a_answer, list) == True):
        a_answer = ", ".join(a_answer)
    elif (isinstance(a_answer, bool) == True):
        a_answer = str(a_answer)

    t_evaluation_data = {
        "question" : [a_question],
        "answer" : [a_answer],
        "contexts" : [[a_text]]
    }

    t_evaluation_dataset = Dataset.from_dict(t_evaluation_data)
    t_evaluation_score = evaluate(t_evaluation_dataset, metrics = [context_utilization])

    t_evaluation = EvaluationData(score = round(t_evaluation_score["context_utilization"], 2), reasoning = "")
    return asdict(t_evaluation)


def _generate_evaluation(
        a_few_shot_request: FewShotRequestData,
        a_suffix: str, 
        a_generation_llm = m_evaluation_generation_llm, 
    ) -> dict | EvaluationData:

    t_number_of_tries: int = int(2)
    for i in range(t_number_of_tries):
        t_generation_result: str = a_few_shot_request.send_request(
            a_prefix_index = 0,
            a_suffix = a_suffix,
            a_llm = a_generation_llm
        ).replace("```json", "").replace("```", "")

        try:
            t_generation_result = json.loads(t_generation_result)
            break
        except:
            print("The evaluation text generation did not return a valid json format!")
            print(f"The generated evaluation text:\n{t_generation_result}")

            if (i < t_number_of_tries):
                print("Retrying...")
            else:
                print("Returning an empty EvaluationData dict!")
                return asdict(EvaluationData())

    t_evaluation_data = EvaluationData(score = t_generation_result["response"]["score"], reasoning = t_generation_result["response"]["reasoning"])

    if (isinstance(t_evaluation_data.score, str) == True):
        if t_evaluation_data.score.startswith("T"):
            t_evaluation_data.score = 1
        elif t_evaluation_data.score.startswith("F"):
            t_evaluation_data.score = 0

    #Normalize between 0 and 5 if valid score.
    if (float(t_evaluation_data.score) > 0):
        t_evaluation_data.score = round(float(t_evaluation_data.score) / 5, 3)

    return asdict(t_evaluation_data)


#Testing

t_transcript = "The term machine learning was coined in 1959 by Arthur Samuel, an IBM employee and pioneer in the field of computer gaming and artificial intelligence.The synonym self-teaching computers was also used in this time period. Although the earliest machine learning model was introduced in the 1950s when Arthur Samuel invented a program that calculated the winning chance in checkers for each side"
t_summary = "Arthur Samuel, an IBM employee, coined the term 'machine learning' in 1959, also referring to it as 'self-teaching computers.' He pioneered this field by creating a program in the 1950s that assessed winning probabilities in checkers."
t_saqs_keywords = "1959, machine learning, Arthur Samuel, IBM employee, artificial intelligence, self-teaching computers, 1950s"
t_gfqs_keywords = "1959, Arthur Samuel, IBM employee, machine learning, Red roses"

"""
evaluate_context_utilisation(
    "this program is designed for everyone who works in the horticultural industry . watch carefully . it shows you what to look out for and how to behave whilst you 're at work . over 50 people a year are killed because of activities at work in agriculture and horticulture . many more are seriously injured . that 's why it is important to take notice of the rules and guidelines that are designed to help people in the horticultural industry stay safe and healthy . you have a duty to look after your own safety and that of others . you must report any health and safety concerns you may have to your manager or supervisor . also , there is a need to report ill health for food safety and hygiene reasons . the rules are there to protect you . listen , learn and obey them to stay safe and healthy at work .", 
    "What industry is the program designed for?", 
    "The program is designed for everyone who works in the horticultural industry."
)
"""

"""
print("Relevance")
#3
print(evaluate_relevance("What term is synonymous with 'machine learning' as used during its early development?", t_transcript))
#print(evaluate_relevance("Who coined the term 'machine learning' and when?", t_transcript))
#print(evaluate_relevance("Arthur Samuel coined the term 'machine learning' in 1959.", t_summary))

#1,2
#print(evaluate_relevance("What is the name of the astronaut's favorite food?", "The story follows an astronaut's journey as he explores new planets and makes contact with alien civilizations."))
#print(evaluate_relevance("What is the name of the author's pet dog?", "The book describes the author's childhood experiences growing up in a small village and how these experiences shaped their later life."))
#print(evaluate_relevance("How does the author's pet change his life?", "The book describes the author's childhood experiences growing up in a small village full of pets and how these experiences shaped their later life."))
#print(evaluate_relevance("How many characters were introduced in the first chapter of the novel?", "The novel details the economic impact of industrialization on rural communities and the subsequent societal changes."))
print("")

print("Reading Comp")
#3
#print(evaluate_reading_comprehension("Who coined the term machine learning and when?"))
print(evaluate_reading_comprehension("The term 'machine learning' was coined in _____."))
#print(evaluate_reading_comprehension("In what year did Donald Hebb publish his influential work on theoretical neural structures?"))

#2
#print(evaluate_reading_comprehension("Do you know what are the causes of deforestation?"))
#print(evaluate_reading_comprehension("How does the changing of seasons affect on human activities?"))
#print(evaluate_reading_comprehension("how many types of animals that live in the ocean does the article mention?"))
print("")

print("Question Difficulty")
#1
#print(evaluate_question_difficulty("What term is synonymous with 'machine learning' as used during its early development?", t_transcript))
#print(evaluate_question_difficulty("Arthur Samuel coined the term 'machine learning' in 1959.", t_summary))

#3
print(evaluate_question_difficulty("How does Gatsby’s pursuit of Daisy symbolize the broader themes of the American Dream and social class in 'The Great Gatsby'?", "In the novel “The Great Gatsby,” Jay Gatsby is depicted as a wealthy and enigmatic figure who throws lavish parties in hopes of rekindling a past romance with Daisy Buchanan. Gatsby's ambition and mysterious background are central to the story, which explores themes of the American Dream, social class, and the moral decay of society in the 1920s. Gatsby’s relationship with Daisy is complex and reflects both his personal desires and the broader social commentary of the time."))

#2
#print(evaluate_question_difficulty("What is the main motivation for Ahab hunting the white whale in ‘Moby Dick’?", "Moby Dick is a novel written in 1851 by the American author Herman Melville. This novel features the experiences of the sailor Ishmael’s narrative of the maniacal quest of Ahab, captain of the whaling ship Pequod. The whale that Ahab is hunting, nicknamed ‘Moby Dick,’ bit off the his leg on a previous voyage."))
print("")

print("Question Clarity")
#3
#print(evaluate_question_clarity("Who coined the term machine learning and when?"))

print(evaluate_question_clarity("The term 'machine learning' was coined in _____."))
#print(evaluate_question_clarity("In what year did Donald Hebb publish his influential work on theoretical neural structures?"))

#2
#print(evaluate_question_clarity("Do you know what are the causes of deforestation?"))
#print(evaluate_question_clarity("How does the changing of seasons affect on human activities?"))
#print(evaluate_question_clarity("how many types of animals that live in the ocean does the article mention?"))
print("")

print("Answer Relevance")
#3
print(evaluate_answer_relevancy("The term machine learning was coined in 1959 by Arthur Samuel.", t_saqs_keywords))
#print(evaluate_answer_relevancy("Arthur Samuel, 1959", t_gfqs_keywords))
print("")

print("Answer Correctness")
print(evaluate_answer_correctness(
    "this program is designed for everyone who works in the horticultural industry . watch carefully . it shows you what to look out for and how to behave whilst you 're at work . over 50 people a year are killed because of activities at work in agriculture and horticulture . many more are seriously injured . that 's why it is important to take notice of the rules and guidelines that are designed to help people in the horticultural industry stay safe and healthy . you have a duty to look after your own safety and that of others . you must report any health and safety concerns you may have to your manager or supervisor . also , there is a need to report ill health for food safety and hygiene reasons . the rules are there to protect you . listen , learn and obey them to stay safe and healthy at work .", 
    "What industry is the program designed for?", 
    "The program is designed for everyone who works in the horticultural industry."
))
print("")
"""