#Python Imports
from pathlib import Path

#External imports
from langchain.output_parsers import CommaSeparatedListOutputParser

#Custom Imports
from segment_data import SegmentData
from utilities.few_shot_request_data import FewShotRequestData
from utilities import langchain_llm


m_few_shot_generation_guidance_data_folder_path = Path("../Guidance-Data/Keywords-Generation")
m_few_shot_generation_request = FewShotRequestData(
    a_guidance_data_folder_path = m_few_shot_generation_guidance_data_folder_path,
    a_files_prefix = "Keywords",
    a_suffix_variables_names = ["number_of_keywords", "text"]
)

m_few_shot_formatting_guidance_data_folder_path = Path("../Guidance-Data/Keywords-Formatting")
m_few_shot_formatting_request = FewShotRequestData(
    a_guidance_data_folder_path = m_few_shot_formatting_guidance_data_folder_path,
    a_files_prefix = "Keywords-Formatting",
    a_suffix_variables_names = ["text"]
)

m_output_parser = CommaSeparatedListOutputParser()


def generate( 
        a_text: str,
        a_number_of_keywords: int,
        a_llm_name: str,
        a_prefix_index: int = 0,
        a_suffix_index: int = 0,
    ) -> list[str]:
    
    #Generating
    t_generation_suffix_template = m_few_shot_generation_request.suffix_templates[a_suffix_index]
    t_generation_suffix = t_generation_suffix_template.format(
        text = a_text, 
        number_of_keywords = a_number_of_keywords
    )
    t_generation_response = m_few_shot_generation_request.send_request (
        a_prefix_index = a_prefix_index,
        a_suffix = t_generation_suffix,
        a_llm = langchain_llm.get_generation_llm(a_llm_name, langchain_llm.LLmType.Transcript)
    )

    #print(f"\nRaw Keywords Response: {t_generation_response}")

    #Formatting
    t_formatting_suffix_template = m_few_shot_formatting_request.suffix_templates[a_suffix_index]
    t_formatting_suffix = t_formatting_suffix_template.format(
        text = t_generation_response, 
    )
    t_formatted_response = m_few_shot_formatting_request.send_request (
        a_prefix_index = a_prefix_index,
        a_suffix = t_formatting_suffix,
        a_llm = langchain_llm.keywords_formatting_llm
    )

    #print(f"\nFormatted Keywords: {t_formatted_response}")
    return  get_words_frequency_from_text(m_output_parser.parse(t_formatted_response), a_text, a_number_of_keywords)


#TODO Check for count using similarity and not exact match
def get_words_frequency_from_text(a_keywords: list[str], a_text: str, a_max_number_of_keywords: int)-> dict:

    if (isinstance(a_text, str) == False):
        a_text = str(a_text)
    
    t_keywords_with_frequency: dict = {}
    t_number_of_keywords: int = 0
    for a_keyword in a_keywords:
        a_keyword = a_keyword.strip()
        t_keyword_frequency = a_text.lower().count(a_keyword.lower())
        t_keywords_with_frequency.update({a_keyword: t_keyword_frequency})

        #Incase more than required keywords are generated, end early.
        t_number_of_keywords += 1
        if (t_number_of_keywords >= a_max_number_of_keywords):
            break

    t_sorted_keywords = dict(sorted(t_keywords_with_frequency.items(), key = lambda item: item[1], reverse = True))
    return t_sorted_keywords


def remove_keyword_from_segment(a_segment_data: dict, a_keywords_dict_key: str, a_word: str) -> dict:
    if ((a_word in a_segment_data[a_keywords_dict_key]) == False):
        print("The keyword given does not exist in the keywords list for this segment version file.")
        return a_segment_data

    a_segment_data[a_keywords_dict_key].pop(a_word)
    print(f"Removed the keyword {a_word} from {a_segment_data[a_keywords_dict_key]}")
    return a_segment_data


def add_keyword_to_segment(a_segment_data: dict, a_keywords_dict_key: str, a_word: str) -> None:
    if ((a_word in a_segment_data[a_keywords_dict_key]) == True):
        print("The keyword given already exist in the keywords list for this segment version file.")
        return a_segment_data
    
    t_text_key = SegmentData.transcript_dict_key() 
    if (a_keywords_dict_key == SegmentData.summary_keywords_dict_key()):
        t_text_key = SegmentData.summary_dict_key()
    
    a_segment_data[a_keywords_dict_key].update(
        get_words_frequency_from_text([a_word], a_segment_data[t_text_key], 99) #99 because number of keywords it shouldn't need to be limited.
    )

    print(f"Added the keyword {a_word} to {a_segment_data[a_keywords_dict_key]}")
    return a_segment_data