#Python Imports
from pathlib import Path

#External Imports
from langchain.text_splitter import RecursiveCharacterTextSplitter

#Custom Imports
from segment_data import SegmentData
from utilities import langchain_llm
from utilities.few_shot_request_data import FewShotRequestData


m_transcript_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 200,
    chunk_overlap = 0,
    length_function = len
)

m_transcript_summary_prompt = """Summarize the provided text. Maintain fidelity of all the important ideas and topics. \
Aim for a summary word limit of {word_limit} or less. Your output must ONLY include the summary and NOTHING ELSE, no heading, no caption, etc. \
In the output DO NOT add prefixes like 'The Summary' or 'Summary', etc. \
\nThe text: {text}"""

m_suffix_variables_names = ["previous_llm_output"]
m_summary_formatting_few_shot_request_data = FewShotRequestData(
    a_guidance_data_folder_path = Path("../Guidance-Data/Summary-Formatting"),
    a_files_prefix = "Summary-Formatting",
    a_suffix_variables_names = m_suffix_variables_names
)


def segment_transcript(a_transcript: str, a_segment_size: int) -> list[str]:
    m_transcript_splitter._chunk_size = a_segment_size
    t_transcript_segments =  m_transcript_splitter.split_text(a_transcript)

    #Debugging
    print("Transcript Segments:\n")
    for i in range(len(t_transcript_segments)):
        print(f"Segment {i} size: {len(t_transcript_segments[i])}.\n" )

    return t_transcript_segments


def generate_segment_summary(a_transcript: str, a_word_limit: int, a_llm_name: str) -> str:

    if (isinstance(a_transcript, str) == False):
        a_transcript = str(a_transcript)

    #If its already small enough, no point summarizing 
    if (len(a_transcript.strip().split(" ")) <= a_word_limit):
        print("\nThe transcript was already smaller than the word limit.")

        #Return back the transcript
        return a_transcript.strip()
    else:
        t_summary_prompt: str = m_transcript_summary_prompt.format(text = a_transcript, word_limit = a_word_limit)
        t_generated_summary = langchain_llm.simple_request(
            a_llm = langchain_llm.get_generation_llm(a_llm_name, a_llm_type = langchain_llm.LLmType.Transcript),
            a_prompt = t_summary_prompt
        ).strip()

        #Debugging
        #print(f"\nOriginal Transcript: {a_transcript}")
        #print(f"\nSummary Generated: {t_generated_summary}")

        #Format the summary generation
        t_summary_formatting_suffix = m_summary_formatting_few_shot_request_data.suffix_templates[0].format(previous_llm_output = t_generated_summary)
        t_formatted_summary = m_summary_formatting_few_shot_request_data.send_request(
            a_prefix_index = 0,
            a_suffix = t_summary_formatting_suffix,
            a_llm = langchain_llm.summary_formatting_llm
        ).strip()

        #Debugging
        print(f"\nFormatted Summary: {t_formatted_summary}")

        return t_formatted_summary
    

def get_full_transcript(a_all_segments_data: list[dict]) -> str:
    t_full_transcript: str = ""

    for t_segment_data_dict in a_all_segments_data:
        t_full_transcript += t_segment_data_dict[SegmentData.transcript_dict_key()]+ " "

    #Debugging
    print(f"\nFull Transcript: {t_full_transcript}")

    return t_full_transcript