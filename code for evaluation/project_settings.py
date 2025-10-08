#Python Imports
from dataclasses import dataclass

@dataclass
class ProjectSettings:
    summaries_word_limit: int
    number_of_transcript_keywords: int
    number_of_summary_keywords: int
    number_of_questions: int
    transcript_segment_size: int

    llm_name: str

    saq_prefix_index: int
    saq_suffix_index: int
    gfq_prefix_index: int
    gfq_suffix_index: int
    blq_prefix_index: int
    blq_suffix_index: int
    mcq_prefix_index: int
    mcq_suffix_index: int

    def dict_to_object(a_dict: dict):
        try: 
            return ProjectSettings (
                summaries_word_limit = a_dict["summaries_word_limit"],
                number_of_transcript_keywords = a_dict["number_of_transcript_keywords"],
                number_of_summary_keywords = a_dict["number_of_summary_keywords"],
                number_of_questions = a_dict["number_of_questions"],
                transcript_segment_size = a_dict["transcript_segment_size"],

                llm_name = a_dict["llm_name"],

                saq_prefix_index = a_dict["saq_prefix_index"],
                saq_suffix_index = a_dict["saq_suffix_index"],
                gfq_prefix_index = a_dict["gfq_prefix_index"],
                gfq_suffix_index = a_dict["gfq_suffix_index"],
                blq_prefix_index = a_dict["blq_prefix_index"],
                blq_suffix_index = a_dict["blq_suffix_index"],
                mcq_prefix_index = a_dict["mcq_prefix_index"],
                mcq_suffix_index = a_dict["mcq_suffix_index"]
            )
        
        except:
            print("Not a valid project settings dict provided. Returning default settings.")
            return default

        

#Default project settings
default: ProjectSettings = ProjectSettings(
    summaries_word_limit = 50,
    number_of_transcript_keywords = 3,
    number_of_summary_keywords = 3,
    number_of_questions = 3,
    transcript_segment_size = 500,

    llm_name = "chatgpt",

    saq_prefix_index = 0,
    saq_suffix_index = 0,
    gfq_prefix_index = 0,
    gfq_suffix_index = 0,
    blq_prefix_index = 0,
    blq_suffix_index = 0,
    mcq_prefix_index = 0,
    mcq_suffix_index = 0
)