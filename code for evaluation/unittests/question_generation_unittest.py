import unittest
import unittest.main
from project import Project
from segment_data import SegmentData
from questions.question_data import QuestionData

"""
Description: 
This file contains unit tests for validating the generation of different question types (MCQs, GFQs, BLQs, and SAQs)
in the project system. It ensures that the correct number and type of questions are generated and stored properly 
in the corresponding JSON arrays in the project segment files.
Test Case 4.1.4 in Test Case Standards document.
"""

#Params
m_project_name: str = "question_generation_test"
m_transcript: str = "The Gowanus Canal is a 1.8-mile-long (2.9 km) canal in the New York City borough of Brooklyn, on the westernmost portion of Long Island. It was created in the mid–19th century from local tidal wetlands and freshwater streams, and by the end of that century was very polluted due to heavy industrial use. Most industrial tenants had stopped using the canal by the middle of the 20th century, but it remained one of the most polluted bodies of water in the United States. Its proximity to Manhattan and upper-class Brooklyn neighborhoods has attracted waterfront redevelopment in recent years, alongside attempts at environmental cleanup. It was designated a Superfund site in 2009."

class QuestionGenerationTest(unittest.TestCase):


    def test_generate_questions(self):
        t_project = Project(a_name = m_project_name, a_transcript = m_transcript)
        #t_project.initialise()

        t_number_of_segments: int = t_project.get_number_of_segments()

        for i in range(t_number_of_segments):
            t_segment_data: dict = t_project.get_segment_data(i)
            t_summary: str = t_segment_data[SegmentData.summary_dict_key()]
            t_summary_keywords : dict = t_segment_data[SegmentData.generated_summary_keywords_dict_key()]
            t_transcript_keywords: dict = t_segment_data[SegmentData.generated_transcript_keywords_dict_key()]

            if (t_summary == ""):
                print(f"The summary is not generated for index {i}. Cannot test summary keywords generation. Run the summary generation test first.")
                return
            
            if (t_summary_keywords == {}):
                print(f"Summary keywords are not generated from index {i}. Cannot test questions generation. Run Summary keywords generation test first.")
                return
            
            if (t_transcript_keywords == {}):
                print(f"Transcript keywords are not generated from index {i}. Cannot test questions generation. Run Transcript keywords generation test first.")
                return
            
        t_project.generate_questions_of_type(SegmentData.saqs_dict_key())
        t_project.generate_questions_of_type(SegmentData.mcqs_dict_key())
        t_project.generate_questions_of_type(SegmentData.blqs_dict_key())
        t_project.generate_questions_of_type(SegmentData.gfqs_dict_key())
            
        for i in range(t_number_of_segments):
            t_segment_data: dict = t_project.get_segment_data(i)
            t_saqs: list = t_segment_data[SegmentData.saqs_dict_key()]
            t_mcqs: list = t_segment_data[SegmentData.mcqs_dict_key()]
            t_gfqs: list = t_segment_data[SegmentData.gfqs_dict_key()]
            t_blqs: list = t_segment_data[SegmentData.blqs_dict_key()]

            #Check SAQs
            print(f"Testing SAQs for segment {i}")
            self.assertTrue(isinstance(t_saqs, list))
            self.assertGreaterEqual(t_project.number_of_questions, len(t_saqs))
            self.assertGreater(len(t_saqs), 0)

            #Check MCQs
            print(f"Testing MCQs for segment {i}")
            self.assertTrue(isinstance(t_mcqs, list))
            self.assertGreaterEqual(t_project.number_of_questions, len(t_mcqs))
            self.assertGreater(len(t_mcqs), 0)

            #Check GFQs
            print(f"Testing GFQs for segment {i}")
            self.assertTrue(isinstance(t_gfqs, list))
            self.assertGreaterEqual(t_project.number_of_questions, len(t_gfqs))
            self.assertGreater(len(t_gfqs), 0)

            #Check BLQs
            print(f"Testing BLQs for segment {i}")
            self.assertTrue(isinstance(t_blqs, list))
            self.assertGreaterEqual(t_project.number_of_questions, len(t_blqs))
            self.assertGreater(len(t_blqs), 0)

        if (__name__ == "__main__"):
            unittest.main()