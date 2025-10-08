import unittest
import unittest.main
from project import Project
from segment_data import SegmentData
import evaluation_api as EvaluationAPI

#Description
"""
Objection: To test if the evaluation for reading comprehension of question is successful.
Expected Result: 
- A score from 0 - 1 for the question's reading comprehension.
- Reasoning for the score.
"""

#Params
m_project_name: str = "TestProject"
m_transcript: str = "The Gowanus Canal is a 1.8-mile-long (2.9 km) canal in the New York City borough of Brooklyn, on the westernmost portion of Long Island. It was created in the mid–19th century from local tidal wetlands and freshwater streams, and by the end of that century was very polluted due to heavy industrial use. Most industrial tenants had stopped using the canal by the middle of the 20th century, but it remained one of the most polluted bodies of water in the United States. Its proximity to Manhattan and upper-class Brooklyn neighborhoods has attracted waterfront redevelopment in recent years, alongside attempts at environmental cleanup. It was designated a Superfund site in 2009."
t_project = Project(a_name = m_project_name, a_transcript = m_transcript)

class UnitTest5(unittest.TestCase):
    def __initialize__(self):
        t_project.initialise()    

    def test_reading_comprehension(self):
        t_number_of_segments: int = t_project.get_number_of_segments()

        for i in range(t_number_of_segments):
            t_segment_data: dict = t_project.get_segment_data(i)
            t_summary: str = t_segment_data[SegmentData.summary_dict_key()]
            t_summary_keywords : dict = t_segment_data[SegmentData.generated_summary_keywords_dict_key()]
            t_transcript_keywords: dict = t_segment_data[SegmentData.generated_transcript_keywords_dict_key()]

            if (t_summary == ""):
                print(f"The summary is not generated for index {i}. Cannot test reading comprehension. Run the Summary generation test first.")
                return
            
            if (t_summary_keywords == {}):
                print(f"Summary keywords are not generated from index {i}. Cannot test reading comprehension. Run Summary keywords generation test first.")
                return
            
            if (t_transcript_keywords == {}):
                print(f"Transcript keywords are not generated from index {i}. Cannot test reading comprehension. Run Transcript keywords generation test first.")
                return

            t_project.generate_questions_of_type(SegmentData.saqs_dict_key())
            t_project.generate_questions_of_type(SegmentData.mcqs_dict_key())
            t_project.generate_questions_of_type(SegmentData.blqs_dict_key())
            t_project.generate_questions_of_type(SegmentData.gfqs_dict_key())

            if (t_project.get_all_questions_of_type(SegmentData.saqs_dict_key()) == []):
                print(f"Questions type {SegmentData.saqs_dict_key()} are not generated. Cannot test reading comprehension. Run Question generation test first.")
                return
            
            if (t_project.get_all_questions_of_type(SegmentData.mcqs_dict_key()) == []):
                print(f"Questions type {SegmentData.mcqs_dict_key()} are not generated. Cannot test reading comprehension. Run Question generation test first.")
                return
            
            if (t_project.get_all_questions_of_type(SegmentData.blqs_dict_key()) == []):
                print(f"Questions type {SegmentData.blqs_dict_key()} are not generated. Cannot test reading comprehension. Run Question generation test first.")
                return
            
            if (t_project.get_all_questions_of_type(SegmentData.gfqs_dict_key()) == []):
                print(f"Questions type {SegmentData.gfqs_dict_key()} are not generated. Cannot test reading comprehension. Run Question generation test first.")
                return
            
            for t_question in t_project.get_all_questions_of_type(SegmentData.saqs_dict_key()):
                t_result = EvaluationAPI.evaluate_reading_comprehension(t_question['question'])

                # check if score is from 0 to 1
                self.assertTrue(0 <= float(t_result['score']) <= 1)

                # check if there is reasoning
                self.assertFalse(t_result['reasoning'] == "")

if (__name__ == "__main__"):
    unittest.main()