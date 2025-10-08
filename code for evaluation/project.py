import pandas

#Python Imports
from dataclasses import asdict
from pathlib import Path

#Utility 
from utilities import file_manager

#Data structure classes
from project_files_schema import ProjectFilesSchema
from segment_data import SegmentData
from questions.question_evaluation_data import QuestionEvaluationData, EvaluationData
from questions.questions_generation_request_data import QuestionsGenerationRequestData
from questions.question_data import QuestionData
from project_settings import ProjectSettings
import project_settings

#Handlers
from keywords import keywords_handler
from transcript import transcription_handler
from questions import questions_handler


class Project:

    def __init__(
            self,
            a_name: str,
            a_transcript: str,
            a_settings: ProjectSettings = None,

            a_project_folder_location: Path = Path("../Projects-Data"),
        ):
        
        #If path invalid, exit.
        if (a_project_folder_location.exists() == False):
            print("Double check if the project folder location is correct. Aborting...")
            return None
        
        #Storing all necessary folder paths and names
        self.files_schema = ProjectFilesSchema(
            a_project_folder_path = a_project_folder_location / a_name
        )
        
        #If no settings are provided, use saved settings. If no saved found, it will fallback to default.
        if (isinstance(a_settings, ProjectSettings) == False):
            a_settings = self.get_saved_settings()
        
        self.name: str = a_name
        self.raw_transcript: str = a_transcript
        self.settings: ProjectSettings = a_settings
    
    def save_settings(self):
        print("Saving Project Settings...")
        file_manager.create_json_file(self.files_schema.project_settings_path, asdict(self.settings))

    def get_saved_settings(self):
        try: 
            t_settings_dict = file_manager.load_json_file_data(self.files_schema.project_settings_path)
            return ProjectSettings.dict_to_object(t_settings_dict)
        except:
            print("No saved settings, using default.")
            return project_settings.default

    def initialise(self):
        print(f"Initializing project {self.name}")

        #Creating needed folders
        file_manager.create_folder_if_not_exist(self.files_schema.project_folder_path)
        file_manager.create_folder_if_not_exist(self.files_schema.segments_folder_path)
        file_manager.create_folder_if_not_exist(self.files_schema.keywords_history_folder_path)
        
        self.save_settings()

        #Segmenting the transcript
        t_transcript_segments: list[str] = transcription_handler.segment_transcript(self.raw_transcript, self.settings.transcript_segment_size)

        t_number_of_segments: int = len(t_transcript_segments)
        t_initial_segment_file_paths: list[Path] = self._get_all_segment_file_paths()
        t_initial_number_of_segment_files: int = len(t_initial_segment_file_paths)
        print(f"Number of segments: {t_number_of_segments}, Current number of segment files: {t_initial_number_of_segment_files}.")

        for i in range(t_number_of_segments):
            #Delete extra segment files if they exist
            for j in range(t_number_of_segments, t_initial_number_of_segment_files, 1):
                file_manager.delete_file(t_initial_segment_file_paths[j])

            

            #Checking if a file with the same transcript already exists
            t_current_segment_data_dict: dict = self.get_segment_data(i)
            if (t_current_segment_data_dict != {}):
                try: 
                    #Skip if there is a segment file and it has the same transcript. This will preserve and other info in that file.
                    if (t_current_segment_data_dict[SegmentData.transcript_dict_key()] == t_transcript_segments[i]):
                        print(f"The segment file at index {i} already has the same transcript data.")
                        continue
                except:
                    print(f"The segment file at index {i} or did not contain valid segment data, writing new data...")

            #Only get here is segment file was not there, or one that was there did not contain valid data.
            t_transcript: str = t_transcript_segments[i]
            if (isinstance(t_transcript, str) == False):
                t_transcript = str(t_transcript)

            t_segment_data = SegmentData(
                transcript = t_transcript
            )

            file_manager.create_segment_file(
                a_file_path = self.files_schema.get_segment_file_path(i),
                a_data = asdict(t_segment_data)
            )



    #Transcript section*
    def generate_segments_summaries(self) -> None:
        for t_segment_file_path in self._get_all_segment_file_paths():
            t_segment_data_dict = file_manager.load_json_file_data(t_segment_file_path)
            t_segment_data_dict[SegmentData.summary_dict_key()] = transcription_handler.generate_segment_summary(
                a_transcript = t_segment_data_dict[SegmentData.transcript_dict_key()], 
                a_word_limit = self.settings.summaries_word_limit, 
                a_llm_name = self.settings.llm_name
            )
            file_manager.create_segment_file(t_segment_file_path, t_segment_data_dict)


    def get_full_transcript(self)-> str:
        return transcription_handler.get_full_transcript(self._get_all_segments_data())
    


    #Keywords section*
    def _generate_keywords(
            self, 
            a_text_dict_key: str, 
            a_keywords_storage_dict_key: str,
            a_number_of_keywords: int
        ) -> None:

        if (a_keywords_storage_dict_key != SegmentData.generated_summary_keywords_dict_key() and a_keywords_storage_dict_key != SegmentData.generated_transcript_keywords_dict_key()):
            print(f"The keyword storage dict key given is not for generated summary nor generate transcript keywords! Aborting. Given: {a_keywords_storage_dict_key}")
            return

        t_segment_file_paths = self._get_all_segment_file_paths()
        for i, t_segment_file_path in enumerate(t_segment_file_paths):
            t_segment_data_dict: dict = self.get_segment_data(i)

            #Generate keywords
            t_keywords = keywords_handler.generate(
                a_text = t_segment_data_dict[a_text_dict_key],
                a_number_of_keywords = a_number_of_keywords,
                a_llm_name = self.settings.llm_name,
                a_prefix_index = self.settings.saq_prefix_index,
                a_suffix_index = self.settings.saq_suffix_index
            )
            t_segment_data_dict[a_keywords_storage_dict_key] = t_keywords
            
            if (a_keywords_storage_dict_key == SegmentData.generated_summary_keywords_dict_key()):
                t_segment_data_dict[SegmentData.blqs_keywords_dict_key()] = t_keywords
                t_segment_data_dict[SegmentData.gfqs_keywords_dict_key()] = t_keywords
            elif (a_keywords_storage_dict_key == SegmentData.generated_transcript_keywords_dict_key()):
                t_segment_data_dict[SegmentData.saqs_keywords_dict_key()] = t_keywords
                t_segment_data_dict[SegmentData.mcqs_keywords_dict_key()] = t_keywords

            #Debugging
            print(f"Generated {a_keywords_storage_dict_key} for {self.files_schema.get_segment_file_name(i)}.")
            print(f"Keywords: {t_segment_data_dict[a_keywords_storage_dict_key]}")

            file_manager.create_segment_file(t_segment_file_path, t_segment_data_dict)


    def generate_transcript_keywords(self) -> None:
        self._generate_keywords(
            a_text_dict_key = SegmentData.transcript_dict_key(),
            a_keywords_storage_dict_key = SegmentData.generated_transcript_keywords_dict_key(),
            a_number_of_keywords = self.settings.number_of_transcript_keywords
        )


    def generate_summary_keywords(self) -> None:
        self._generate_keywords(
            a_text_dict_key = SegmentData.summary_dict_key(),
            a_keywords_storage_dict_key = SegmentData.generated_summary_keywords_dict_key(),
            a_number_of_keywords = self.settings.number_of_summary_keywords
        )

    
    def remove_keyword_from_segment(self, a_segment_index: int, a_user_keywords_type: str, a_keyword: str) -> bool:
        t_segment_data: dict = self.get_segment_data(a_segment_index)
        if (t_segment_data == {}):
            print("Given indexes for removing a keyword is out of range. Aborting removing keyword...")
            return False

        if (SegmentData.does_question_keyword_type_exist(a_user_keywords_type) == False):
            return False
        
        t_segment_data = keywords_handler.remove_keyword_from_segment(t_segment_data, a_user_keywords_type, a_keyword)
        file_manager.create_segment_file(self._get_all_segment_file_paths()[a_segment_index], t_segment_data)
        return True


    def add_keyword_to_segment(self, a_segment_index: int, a_user_keywords_type: str, a_keyword: str) -> None:
        t_segment_file_paths = self._get_all_segment_file_paths()
        if (a_segment_index < 0 or a_segment_index >= len(t_segment_file_paths)):
            print("Given indexes for adding a keyword is out of range. Aborting adding keyword...")
            return "Index out of range."
        
        if (SegmentData.does_question_keyword_type_exist(a_user_keywords_type) == False):
            return "Invalid keyword type."
        
        t_segment_data = file_manager.load_json_file_data(t_segment_file_paths[a_segment_index])
        t_segment_data = keywords_handler.add_keyword_to_segment(t_segment_data, a_user_keywords_type, a_keyword)
        file_manager.create_segment_file(t_segment_file_paths[a_segment_index], t_segment_data)
        return "Successful"



    #Question section*
    def generate_questions_of_type(self, a_question_type: str) -> list:
        if (SegmentData.does_question_type_exist(a_question_type = a_question_type) == False):
            print(f"\nThe provided question type dict key does not exist! All question types dict keys: {', '.join(SegmentData.question_types())}. Aborting...")
            return []

        t_segment_file_paths = self._get_all_segment_file_paths()
        for i, t_segment_file_path in enumerate(t_segment_file_paths):
            t_segment_data = file_manager.load_json_file_data(t_segment_file_path)
            t_questions_generation_request_data = self._get_questions_generation_request_data(
                a_segment_data = t_segment_data, 
                a_question_type = a_question_type
            )
            t_questions_data_list = questions_handler.generate(t_questions_generation_request_data)
            
            t_questions_dict_list = []
            for t_question_data in t_questions_data_list:
                t_question_dict = asdict(t_question_data)
                t_questions_dict_list.append(t_question_dict)

            t_segment_data[a_question_type] = t_questions_dict_list

            #Debugging
            #print(f"\nGenerated {a_question_type} for segment-{i}.")
            #print(f"{a_question_type}: {t_segment_data[a_question_type]}")
        
            file_manager.create_segment_file(t_segment_file_paths[i], t_segment_data)
        
        return t_questions_dict_list
    
    def generate_segment_questions_of_type(self, a_segment_id: int, a_question_type: str) -> list:
        if (SegmentData.does_question_type_exist(a_question_type = a_question_type) == False):
            print(f"\nThe provided question type dict key does not exist! All question types dict keys: {', '.join(SegmentData.question_types())}. Aborting...")
            return []
        
        t_segment_file_paths = self._get_all_segment_file_paths()
        if (t_segment_file_paths == []):
            print("No segments to generate questions for.")
            return []
        
        t_segment_file_path = t_segment_file_paths[a_segment_id]
        t_segment_data = file_manager.load_json_file_data(t_segment_file_path)

        t_questions_generation_request_data = self._get_questions_generation_request_data(
            a_segment_data = t_segment_data, 
            a_question_type = a_question_type
        )
        t_questions_data_list = questions_handler.generate(t_questions_generation_request_data)
        
        t_questions_dict_list = []
        for t_question_data in t_questions_data_list:
            t_question_dict = asdict(t_question_data)
            t_questions_dict_list.append(t_question_dict)

        t_segment_data[a_question_type] = t_questions_dict_list

        #Debugging
        #print(f"\nGenerated {a_question_type} for segment-{i}.")
        #print(f"{a_question_type}: {t_segment_data[a_question_type]}")
    
        file_manager.create_segment_file(t_segment_file_path, t_segment_data)
        
        return t_questions_dict_list



    def get_all_questions_of_type(self, a_question_type: str) -> list[dict]:
        if (SegmentData.does_question_type_exist(a_question_type = a_question_type) == False):
            print(f"\nThe provided question type dict key does not exist! All question types dict keys: {', '.join(SegmentData.question_types())}. Aborting...")
            return []
        
        return questions_handler.get_all_questions_of_type(
            a_all_segments_data = self._get_all_segments_data(), 
            a_question_type = a_question_type
        )
    

    def _get_questions_generation_request_data(self, a_segment_data: dict, a_question_type: str) -> QuestionsGenerationRequestData:
        if (SegmentData.does_question_type_exist(a_question_type) == False):
            return None
        
        t_text = ""
        t_keywords = []
        t_prefix = 0
        t_suffix = 0
        
        #I really dont like these if statements, will do for now. Too much repetition.
        if (a_question_type == SegmentData.saqs_dict_key() or a_question_type == SegmentData.mcqs_dict_key()):
            t_text = a_segment_data[SegmentData.transcript_dict_key()]
            if (a_question_type == SegmentData.saqs_dict_key()):
                t_keywords = a_segment_data[SegmentData.saqs_keywords_dict_key()].keys()
                t_prefix = self.settings.saq_prefix_index
                t_suffix = self.settings.saq_suffix_index
            else:
                t_keywords = a_segment_data[SegmentData.mcqs_keywords_dict_key()].keys()
                t_suffix = self.settings.mcq_prefix_index
                t_prefix = self.settings.mcq_suffix_index

        elif (a_question_type == SegmentData.gfqs_dict_key() or a_question_type == SegmentData.blqs_dict_key()):
            t_text = a_segment_data[SegmentData.summary_dict_key()]
            if (a_question_type == SegmentData.gfqs_dict_key()):
                t_keywords = a_segment_data[SegmentData.gfqs_keywords_dict_key()].keys()
                t_prefix = self.settings.gfq_prefix_index
                t_suffix = self.settings.gfq_suffix_index
            else:
                t_keywords = a_segment_data[SegmentData.blqs_keywords_dict_key()].keys()
                t_prefix = self.settings.blq_prefix_index
                t_suffix = self.settings.blq_suffix_index

        t_questions_generation_request_data = QuestionsGenerationRequestData(
            a_question_type = a_question_type,
            a_text = t_text,
            a_keywords = t_keywords,
            a_number_of_question = self.settings.number_of_questions,
            a_llm_name = self.settings.llm_name,
            a_prefix_index = t_prefix,
            a_suffix_index = t_suffix
        )

        return t_questions_generation_request_data



    #Evaluation*
    def evaluate_all_segments(
            self,
            a_do_saqs: bool = True, 
            a_do_mcqs: bool = True, 
            a_do_gfqs: bool = True, 
            a_do_blqs: bool = True,
        ) -> None:
        t_segments_count = len(self._get_all_segment_file_paths())
        for i in range(t_segments_count):
            self.evaluate_segment(i, a_do_saqs, a_do_mcqs, a_do_gfqs, a_do_blqs)
    

    def evaluate_segment(
            self, 
            a_segment_index: int, 
            a_do_saqs: bool = True, 
            a_do_mcqs: bool = True, 
            a_do_gfqs: bool = True, 
            a_do_blqs: bool = True,
        ) -> None:

        t_segment_data_dict: dict = self.get_segment_data(a_segment_index)
        if (t_segment_data_dict == {}):
            print(f"No segment data at the given index: {a_segment_index}.")
            return False

        t_segment_file_path: Path = self._get_all_segment_file_paths()[a_segment_index]
        
        #SAQs Evaluation
        print("\nEvaluating SAQs...")
        if (a_do_saqs == True):
            t_saqs: list[dict] = t_segment_data_dict[SegmentData.saqs_dict_key()]
            for t_saq_question_data in t_saqs:
                t_saq_question_data[QuestionData.question_evaluation_dict_key()] = asdict(QuestionEvaluationData.evaluate_question(
                    a_text = t_segment_data_dict[SegmentData.transcript_dict_key()],
                    a_ground_truth = ", ".join(t_segment_data_dict[SegmentData.saqs_keywords_dict_key()]),
                    a_question = t_saq_question_data[QuestionData.question_dict_key()],
                    a_answer = t_saq_question_data[QuestionData.answer_dict_key()]
                ))
            t_segment_data_dict[SegmentData.saqs_dict_key()] = t_saqs

        #Save changes
        file_manager.create_segment_file(t_segment_file_path, t_segment_data_dict)

        #MCQs Evaluation
        print("\nEvaluating MCQs...")
        if (a_do_mcqs == True):
            t_mcqs: list[dict] = t_segment_data_dict[SegmentData.mcqs_dict_key()]
            for t_mcq_question_data in t_mcqs:
                #Check Answer formatting
                t_mcq_answer = t_mcq_question_data[QuestionData.answer_dict_key()]
                if (isinstance(t_mcq_answer, str) == True): 
                    t_mcq_answer = t_mcq_answer.split(", ")[0]
                else:
                    t_mcq_answer = t_mcq_answer[0]

                t_mcq_question_data[QuestionData.question_evaluation_dict_key()] = asdict(QuestionEvaluationData.evaluate_question(
                    a_text = t_segment_data_dict[SegmentData.transcript_dict_key()],
                    a_ground_truth = ", ".join(t_segment_data_dict[SegmentData.mcqs_keywords_dict_key()]),
                    a_question = t_mcq_question_data[QuestionData.question_dict_key()],
                    a_answer = t_mcq_answer
                ))
            t_segment_data_dict[SegmentData.mcqs_dict_key()] = t_mcqs

        #Save changes
        file_manager.create_segment_file(t_segment_file_path, t_segment_data_dict)

        #GFQs Evaluation
        print("\nEvaluating GFQs...")
        if (a_do_gfqs == True):
            t_gfqs: list[dict] = t_segment_data_dict[SegmentData.gfqs_dict_key()]
            for t_gfq_question_data in t_gfqs:
                #Check Answer formatting
                t_gfq_answer = t_gfq_question_data[QuestionData.answer_dict_key()]
                if (isinstance(t_gfq_answer, list) == True): 
                    t_gfq_answer = ", ".join(t_gfq_answer)

                t_gfq_question_data[QuestionData.question_evaluation_dict_key()] = asdict(QuestionEvaluationData.evaluate_question(
                    a_text = t_segment_data_dict[SegmentData.summary_dict_key()],
                    a_ground_truth = ", ".join(t_segment_data_dict[SegmentData.gfqs_keywords_dict_key()]),
                    a_question = t_gfq_question_data[QuestionData.question_dict_key()],
                    a_answer = t_gfq_answer
                ))
            t_segment_data_dict[SegmentData.gfqs_dict_key()] = t_gfqs

        #Save changes
        file_manager.create_segment_file(t_segment_file_path, t_segment_data_dict)

        #BLQs Evaluation
        print("\nEvaluating BLQs...")
        if (a_do_blqs == True):
            t_blqs: list[dict] = t_segment_data_dict[SegmentData.blqs_dict_key()]
            for t_blq_question_data in t_blqs:
                t_blq_question_data[QuestionData.question_evaluation_dict_key()] = asdict(QuestionEvaluationData.evaluate_question(
                    a_text = t_segment_data_dict[SegmentData.summary_dict_key()],
                    a_ground_truth = ", ".join(t_segment_data_dict[SegmentData.blqs_keywords_dict_key()]),
                    a_question = t_blq_question_data[QuestionData.question_dict_key()],
                    a_answer = t_blq_question_data[QuestionData.answer_dict_key()]
                ))
            t_segment_data_dict[SegmentData.blqs_dict_key()] = t_blqs
        
        #Save changes
        file_manager.create_segment_file(t_segment_file_path, t_segment_data_dict)
    

    def get_project_data_as_csv(self):
        t_all_segment_data: list[dict] = self._get_all_segments_data()

        t_columns: list[str] = [
            "segment_index", 
            "question_index", 
            "questions_type", 
            "text_used", 
            "keywords_used", 
            "question", 
            "answer", 
            "relevance", 
            "reading_comprehension", 
            "question_difficulty", 
            "question_clarity", 
            "answer_relevancy",
            "answer_correctness",
            "context_utilisation",
            "generation_time"
        ]

        t_csv_data = pandas.DataFrame(columns = t_columns)

        
        for i, t_segment_data in enumerate(t_all_segment_data):
            print(f"Collecting data for segment {i}")
            
            #SAQs
            for j, t_question_data in enumerate(t_segment_data[SegmentData.saqs_dict_key()]):
                t_evaluation_data = t_question_data[QuestionData.question_evaluation_dict_key()]
                t_csv_row_dict: dict = {
                    "segment_index": i,
                    "questions_type": SegmentData.saqs_dict_key(),
                    "question_index": j,
                    "text_used": t_segment_data[SegmentData.transcript_dict_key()],
                    "keywords_used": [", ".join(t_segment_data[SegmentData.saqs_keywords_dict_key()].keys())],
                    "question": t_question_data[QuestionData.question_dict_key()],
                    "answer": t_question_data[QuestionData.answer_dict_key()],
                    "relevance": t_evaluation_data[QuestionEvaluationData.relevance_dict_key()][EvaluationData.score_dict_key()],
                    "reading_comprehension": t_evaluation_data[QuestionEvaluationData.reading_comprehension_dict_key()][EvaluationData.score_dict_key()],
                    "question_difficulty": t_evaluation_data[QuestionEvaluationData.question_difficulty_dict_key()][EvaluationData.score_dict_key()],
                    "question_clarity": t_evaluation_data[QuestionEvaluationData.question_clarity_dict_key()][EvaluationData.score_dict_key()],
                    "answer_relevancy": t_evaluation_data[QuestionEvaluationData.answer_relevance_dict_key()][EvaluationData.score_dict_key()],
                    "answer_correctness": t_evaluation_data[QuestionEvaluationData.answer_correctness_dict_key()][EvaluationData.score_dict_key()],
                    "context_utilisation" : t_evaluation_data[QuestionEvaluationData.context_utilisation_dict_key()][EvaluationData.score_dict_key()],
                    "generation_time" : t_evaluation_data[QuestionEvaluationData.generation_time_dict_key()]
                }

                t_saq_csv_row = pandas.DataFrame(t_csv_row_dict, index = [0])
                t_csv_data = pandas.concat([t_csv_data, t_saq_csv_row], ignore_index = True)

            #MCQs
            for j, t_question_data in enumerate(t_segment_data[SegmentData.mcqs_dict_key()]):
                t_evaluation_data = t_question_data[QuestionData.question_evaluation_dict_key()]
                
                t_csv_row_dict: dict = {
                    "segment_index": i,
                    "questions_type": SegmentData.mcqs_dict_key(),
                    "question_index": j,
                    "text_used": t_segment_data[SegmentData.transcript_dict_key()],
                    "keywords_used": [", ".join(t_segment_data[SegmentData.saqs_keywords_dict_key()].keys())],
                    "question": t_question_data[QuestionData.question_dict_key()],
                    "answer": [t_question_data[QuestionData.answer_dict_key()]],
                    "relevance": t_evaluation_data[QuestionEvaluationData.relevance_dict_key()][EvaluationData.score_dict_key()],
                    "reading_comprehension": t_evaluation_data[QuestionEvaluationData.reading_comprehension_dict_key()][EvaluationData.score_dict_key()],
                    "question_difficulty": t_evaluation_data[QuestionEvaluationData.question_difficulty_dict_key()][EvaluationData.score_dict_key()],
                    "question_clarity": t_evaluation_data[QuestionEvaluationData.question_clarity_dict_key()][EvaluationData.score_dict_key()],
                    "answer_relevancy": t_evaluation_data[QuestionEvaluationData.answer_relevance_dict_key()][EvaluationData.score_dict_key()],
                    "answer_correctness": t_evaluation_data[QuestionEvaluationData.answer_correctness_dict_key()][EvaluationData.score_dict_key()],
                    "context_utilisation" : t_evaluation_data[QuestionEvaluationData.context_utilisation_dict_key()][EvaluationData.score_dict_key()],
                    "generation_time" : t_evaluation_data[QuestionEvaluationData.generation_time_dict_key()]
                }

                t_mcq_csv_row = pandas.DataFrame(t_csv_row_dict, index = [0])
                t_csv_data = pandas.concat([t_csv_data, t_mcq_csv_row], ignore_index = True)

            #BLQs
            for j, t_question_data in enumerate(t_segment_data[SegmentData.blqs_dict_key()]):
                t_evaluation_data = t_question_data[QuestionData.question_evaluation_dict_key()]
                t_csv_row_dict: dict = {
                    "segment_index": i,
                    "questions_type": SegmentData.blqs_dict_key(),
                    "question_index": j,
                    "text_used": t_segment_data[SegmentData.summary_dict_key()],
                    "keywords_used": [", ".join(t_segment_data[SegmentData.saqs_keywords_dict_key()].keys())],
                    "question": t_question_data[QuestionData.question_dict_key()],
                    "answer": t_question_data[QuestionData.answer_dict_key()],
                    "relevance": t_evaluation_data[QuestionEvaluationData.relevance_dict_key()][EvaluationData.score_dict_key()],
                    "reading_comprehension": t_evaluation_data[QuestionEvaluationData.reading_comprehension_dict_key()][EvaluationData.score_dict_key()],
                    "question_difficulty": t_evaluation_data[QuestionEvaluationData.question_difficulty_dict_key()][EvaluationData.score_dict_key()],
                    "question_clarity": t_evaluation_data[QuestionEvaluationData.question_clarity_dict_key()][EvaluationData.score_dict_key()],
                    "answer_relevancy": t_evaluation_data[QuestionEvaluationData.answer_relevance_dict_key()][EvaluationData.score_dict_key()],
                    "answer_correctness": t_evaluation_data[QuestionEvaluationData.answer_correctness_dict_key()][EvaluationData.score_dict_key()],
                    "context_utilisation" : t_evaluation_data[QuestionEvaluationData.context_utilisation_dict_key()][EvaluationData.score_dict_key()],
                    "generation_time" : t_evaluation_data[QuestionEvaluationData.generation_time_dict_key()]
                }

                t_blq_csv_row = pandas.DataFrame(t_csv_row_dict, index = [0])
                t_csv_data = pandas.concat([t_csv_data, t_blq_csv_row], ignore_index = True)

            #GFQs
            for j, t_question_data in enumerate(t_segment_data[SegmentData.gfqs_dict_key()]):
                t_evaluation_data = t_question_data[QuestionData.question_evaluation_dict_key()]
                t_csv_row_dict: dict = {
                    "segment_index": i,
                    "questions_type": SegmentData.gfqs_dict_key(),
                    "question_index": j,
                    "text_used": t_segment_data[SegmentData.summary_dict_key()],
                    "keywords_used": [", ".join(t_segment_data[SegmentData.saqs_keywords_dict_key()].keys())],
                    "question": t_question_data[QuestionData.question_dict_key()],
                    "answer": [t_question_data[QuestionData.answer_dict_key()]],
                    "relevance": t_evaluation_data[QuestionEvaluationData.relevance_dict_key()][EvaluationData.score_dict_key()],
                    "reading_comprehension": t_evaluation_data[QuestionEvaluationData.reading_comprehension_dict_key()][EvaluationData.score_dict_key()],
                    "question_difficulty": t_evaluation_data[QuestionEvaluationData.question_difficulty_dict_key()][EvaluationData.score_dict_key()],
                    "question_clarity": t_evaluation_data[QuestionEvaluationData.question_clarity_dict_key()][EvaluationData.score_dict_key()],
                    "answer_relevancy": t_evaluation_data[QuestionEvaluationData.answer_relevance_dict_key()][EvaluationData.score_dict_key()],
                    "answer_correctness": t_evaluation_data[QuestionEvaluationData.answer_correctness_dict_key()][EvaluationData.score_dict_key()],
                    "context_utilisation" : t_evaluation_data[QuestionEvaluationData.context_utilisation_dict_key()][EvaluationData.score_dict_key()],
                    "generation_time" : t_evaluation_data[QuestionEvaluationData.generation_time_dict_key()]
                }

                t_gfq_csv_row = pandas.DataFrame(t_csv_row_dict, index = [0])
                t_csv_data = pandas.concat([t_csv_data, t_gfq_csv_row], ignore_index = True)

        t_csv_file_name = self.name + ".csv"
        t_csv_file_path = str(self.files_schema.project_folder_path / t_csv_file_name)
        t_csv_data.to_csv(t_csv_file_path, index = False)

        return t_csv_data


    #Project settings*
    def set_number_of_questions_to_generate(self, a_number_of_question: int) -> None:
        self.settings.number_of_questions = a_number_of_question
        print(f"\nChanged the number of questions the LLM will generate to {a_number_of_question}")


    def set_number_of_keywords_to_generate(self, a_number_of_keywords: int) -> None:
        self.settings.number_of_transcript_keywords = a_number_of_keywords
        print(f"\nChanged the number of keywords the LLM will generate to {a_number_of_keywords}")
    

    
    #Utility*
    def _get_all_segment_file_paths(self) -> list[Path]:
        t_segments_folder_paths: list[Path] = file_manager.get_folder_file_paths_list(self.files_schema.segments_folder_path)

        t_file_paths = []
        for i, t_path in enumerate(t_segments_folder_paths):
            #No point check if its not a json file, which they always should be.
            if (t_path.suffix == ".json"):
                t_file_paths.append(self.files_schema.get_segment_file_path(i))

        return t_file_paths
    
    def _get_all_segments_data(self) -> list[dict]:
        t_segments_file_paths = self._get_all_segment_file_paths()

        t_all_segment_data: list[dict] = []
        for i in range(len(t_segments_file_paths)):
            t_all_segment_data.append(self.get_segment_data(i))

        return t_all_segment_data
    
    def get_segment_data(self, a_index) -> dict:
        if (a_index < 0):
            print(f"The given index ({a_index}) for retrieving segment data is too small. Given index.")
            return {}
        
        t_segments_folder_path = self.files_schema.segments_folder_path
        t_segments_folder_list = file_manager.get_folder_file_paths_list(t_segments_folder_path)

        if (a_index >= len(t_segments_folder_list)):
            print(f"The given index ({a_index}) for retrieving segment data is out of bounds, too large.")
            return {}
        
        t_data_dict = file_manager.load_json_file_data(self.files_schema.get_segment_file_path(a_index))
        return t_data_dict
    
    def get_number_of_segments(self) -> int:
        return len(self._get_all_segment_file_paths())
    
    def is_project_file_system_valid(self) -> bool:
        return self.files_schema.is_project_file_system_valid()
