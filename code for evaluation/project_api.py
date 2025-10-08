#External imports
from dataclasses import asdict
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware

#Custom Imports
from project import Project
from project_settings import ProjectSettings


api = FastAPI(
    title = "i45 AQG API",
    summary = "Takes text input to generate keywords and text summary from which it generates \
short-answer-questions, multiple-choice questions, boolean questions and gap-fil questions."
)
api.add_middleware(
    CORSMiddleware,
    allow_origins = '*',
    allow_credentials = True,
    allow_headers = ["*"],
)



#Project*
@api.get("/does-valid-project-exists/{a_project_name}")
def does_valid_project_exist(a_project_name: str) -> dict:

    if (_does_valid_project_exist(a_project_name) == False):
        print(f"{a_project_name} is NOT a valid project!")
        return _output_false()
    
    print(f"{a_project_name} is a valid project!")
    return _output_true()


@api.post("/create-project/")
def create_project(
    a_project_name: str = Form(...), 
    a_project_transcript: str = Form(...),
    a_transcript_chunk_size: int = Form(...),
    a_summary_size: int = Form(...),
    a_number_of_transcript_keywords: int = Form(...),
    a_number_of_summary_keywords: int = Form(...),
    a_number_of_questions: int = Form(...),
    a_llm_name: str = Form(...)
):
    print("Creating Project...")
    print(f"Project name: {a_project_name}")
    print(f"Transcript: {a_project_transcript}")
    print(f"Transcript Chunk Size: {a_transcript_chunk_size}")
    print(f"Summary Size: {a_summary_size}")
    print(f"Number of Transcript Keywords: {a_number_of_transcript_keywords}")
    print(f"Number of Summary Keywords: {a_number_of_summary_keywords}")
    print(f"Number of questions: {a_number_of_questions}")
    print(f"LLM: {a_llm_name}")

    t_project_settings: ProjectSettings = ProjectSettings(
        summaries_word_limit = a_summary_size,
        transcript_segment_size = a_transcript_chunk_size,

        number_of_questions = a_number_of_questions,
        number_of_summary_keywords = a_number_of_summary_keywords,
        number_of_transcript_keywords = a_number_of_transcript_keywords,

        llm_name = a_llm_name,

        #Just default
        saq_prefix_index = 0,
        saq_suffix_index = 0,
        gfq_prefix_index = 0,
        gfq_suffix_index = 0,
        blq_prefix_index = 0,
        blq_suffix_index = 0,
        mcq_prefix_index = 0,
        mcq_suffix_index = 0
    )

    t_project = Project (
            a_name = a_project_name,
            a_transcript = a_project_transcript,
            a_settings = t_project_settings
        )
    
    if (t_project == None):
        return _output_false()

    t_project.initialise() 
    print(f"Created project with the name {t_project.name}")

    return _output_true()


@api.get("/get-full-transcript/{a_project_name}/{a_segment_index}")
def get_full_transcript(a_project_name: str):

    #Check if project exists and is valid.
    if (_does_valid_project_exist(a_project_name) == False):
        return _output_custom("Project does not exist. Cannot retrieve segment data!")
    
    t_project: Project = _open_project(a_project_name)
    return _output_custom(asdict(t_project.get_full_transcript()))



#Segment*
@api.get("/get-segment-data/{a_project_name}/{a_segment_index}")
def get_segment_data(a_project_name: str, a_segment_index: int):

    #Check if project exists and is valid.
    if (_does_valid_project_exist(a_project_name) == False):
        return _output_custom("Project does not exist. Cannot retrieve segment data!")
    
    t_project = _open_project(a_project_name)
    t_outcome = t_project.get_segment_data(int(a_segment_index))
    
    #print(f"Fetching segment: {t_outcome}")
    return _output_custom(t_outcome)

@api.get("/get-number-of-segments/{a_project_name}")
def get_number_of_segments(a_project_name: str) -> dict:

    #Check if project exists and is valid.
    if (_does_valid_project_exist(a_project_name) == False):
        return _output_custom("Project does not exist. Cannot retrieve segment data!")
    
    t_project: Project = _open_project(a_project_name)
    t_number_of_segments = t_project.get_number_of_segments()

    print(f"Returning number of segments: {t_number_of_segments}")
    return _output_custom(t_number_of_segments)


#Transcript*
@api.post("/generate-segment-summaries/{a_project_name}")
def generate_segment_summaries(a_project_name: str):

    #Check if project exists and is valid.
    if (_does_valid_project_exist(a_project_name) == False):
        return _output_custom("Project does not exist. Cannot retrieve segment data!")
    
    t_project = _open_project(a_project_name)

    print("Generating Summaries...")
    t_project.generate_segments_summaries()
    return _output_true()



#Keywords*
@api.post("/generate-transcript-keywords/{a_project_name}")
def generate_transcript_keywords(a_project_name: str):

    #Check if project exists and is valid.
    if (_does_valid_project_exist(a_project_name) == False):
        return _output_custom("Project does not exist. Cannot retrieve segment data!")
    
    t_project = _open_project(a_project_name)

    print("Generating Transcript Keywords...")
    t_project.generate_transcript_keywords()
    return _output_true()


@api.post("/generate-summary-keywords/{a_project_name}")
def generate_summary_keywords(a_project_name: str):
    
    #Check if project exists and is valid.
    if (_does_valid_project_exist(a_project_name) == False):
        return _output_custom("Project does not exist. Cannot retrieve segment data!")
    
    t_project = _open_project(a_project_name)

    print("Generating Summary Keywords...")
    t_project.generate_summary_keywords()
    return _output_true()


@api.post("/remove-keyword-from-segment/{a_project_name}/{a_segment_index}/{a_user_keywords_type}/{a_keyword}")
def remove_keyword_from_segment(a_project_name: str, a_segment_index: int, a_user_keywords_type: str, a_keyword: str):
    
    #Check if project exists and is valid.
    if (_does_valid_project_exist(a_project_name) == False):
        return _output_custom("Project does not exist. Cannot retrieve segment data!")

    t_project = _open_project(a_project_name)
    t_outcome = t_project.remove_keyword_from_segment(
        a_segment_index = a_segment_index,
        a_user_keywords_type = a_user_keywords_type,
        a_keyword = a_keyword
    )

    print(f"The outcome for removing the keyword <{a_keyword}> from the project <{a_project_name}> in segment index <{a_segment_index}>, of type <{a_user_keywords_type}> was {t_outcome}")
    return _output_custom(t_outcome)


@api.post("/add-keyword-to-segment/{a_project_name}/{a_segment_index}/{a_user_keywords_type}/{a_keyword}")
def add_keyword_to_segment(a_project_name: str, a_segment_index: int, a_user_keywords_type: str, a_keyword: str):
    
    #Check if project exists and is valid.
    if (_does_valid_project_exist(a_project_name) == False):
        return _output_custom("Project does not exist. Cannot retrieve segment data!")

    t_project = _open_project(a_project_name)
    
    t_outcome = t_project.add_keyword_to_segment(
        a_segment_index = a_segment_index,
        a_user_keywords_type = a_user_keywords_type,
        a_keyword = a_keyword
    )
    
    print(f"The outcome for adding the keyword <{a_keyword}> to the project <{a_project_name}> in segment index <{a_segment_index}>, of type <{a_user_keywords_type}> was {t_outcome}")
    return _output_custom(t_outcome)



#Questions*
@api.post("/generate-questions-of-type/{a_project_name}/{a_question_type}")
def generate_questions_of_type(a_project_name: str, a_question_type: str):
    
    #Check if project exists and is valid.
    if (_does_valid_project_exist(a_project_name) == False):
        return _output_custom("Project does not exist. Cannot retrieve segment data!")

    t_project = _open_project(a_project_name)
    t_outcome = t_project.generate_questions_of_type(a_question_type)
    return _output_custom(t_outcome)


@api.get("/generate-segment-questions-of-type/{a_project_name}/{a_segment_id}/{a_question_type}")
def generate_segment_questions_of_type(a_project_name: str, a_segment_id: int, a_question_type: str):
    
    #Check if project exists and is valid.
    if (_does_valid_project_exist(a_project_name) == False):
        return _output_custom("Project does not exist. Cannot retrieve segment data!")

    t_project = _open_project(a_project_name)
    t_outcome = t_project.generate_segment_questions_of_type(a_segment_id, a_question_type)
    print(f"{a_question_type} questions generated for segment {a_segment_id}:\n{t_outcome}")
    return _output_custom(t_outcome)


@api.get("/get-all-questions-of-type/{a_project_name}/{a_question_type}")
def get_all_questions_of_type(a_project_name: str, a_question_type: str):
    
    #Check if project exists and is valid.
    if (_does_valid_project_exist(a_project_name) == False):
        return _output_custom("Project does not exist. Cannot retrieve segment data!")

    t_project = _open_project(a_project_name)
    t_outcome = t_project.get_all_questions_of_type(a_question_type)
    return _output_custom(t_outcome)



#Evaluation*
@api.get("/evaluate-all_segments/{a_project_name}")
def evaluate_all_segments(a_project_name: str) -> dict:

    #Check if project exists and is valid.
    if (_does_valid_project_exist(a_project_name) == False):
        return _output_custom("Project does not exist. Cannot retrieve segment data!")
    
    t_project: Project = _open_project(a_project_name)
    t_project.evaluate_all_segments()
    return _output_true()


@api.get("/evaluate-segment/{a_project_name}/{a_segment_index}")
def evaluate_segment(a_project_name: str, a_segment_index: int) -> dict:
    
    #Check if project exists and is valid.
    if (_does_valid_project_exist(a_project_name) == False):
        return _output_custom("Project does not exist. Cannot retrieve segment data!")
    
    t_project: Project = _open_project(a_project_name)
    t_project.evaluate_segment(a_segment_index)
    return _output_true()



#Project CSV Data
@api.get("/get-csv/{a_project_name}")
def get_csv(a_project_name: str):

    #Check if project exists and is valid.
    if (_does_valid_project_exist(a_project_name) == False):
        return _output_custom("Project does not exist. Cannot retrieve segment data!")
    
    t_project: Project = _open_project(a_project_name)
    t_project.get_project_data_as_csv()

    return _output_true()



#Project Settings Data
@api.get("/get-project-settings/{a_project_name}")
def get_project_settings(a_project_name: str):

    #Check if project exists and is valid.
    if (_does_valid_project_exist(a_project_name) == False):
        return _output_custom("Project does not exist. Cannot retrieve segment data!")
    
    t_project: Project = _open_project(a_project_name)
    return _output_custom(asdict(t_project.get_saved_settings()))



@api.get("/hi/")
def hi():
    return f"Hello!"


#Utility*
def _output_custom(a_msg) -> dict:
    return {"output" : a_msg}

def _output_true() -> dict:
    return _output_custom(True)

def _output_false() -> dict:
    return _output_custom(False)

def _open_project(a_project_name: str) -> Project:
    return Project(a_name = a_project_name, a_transcript = "")

def _does_valid_project_exist(a_project_name: str) -> bool:
    t_project = _open_project(a_project_name)

    if (t_project == None):
        return False
    
    if (t_project.is_project_file_system_valid() == False):
        return False
    
    return True