"""
This file contains the test cases for evaluating the difficulty of generated questions 
in a project. The test checks the score given to questions based on how difficult the 
answers are to find within the reference text.
Test Case 4.1.7 in Test Case Standards Document
"""

import unittest
from project import Project
from segment_data import SegmentData
from questions.question_data import QuestionData

m_project_name: str = "TestProjectDifficulty"
m_transcript: str = """
The Gowanus Canal is a 1.8-mile-long (2.9 km) canal in the New York City borough of Brooklyn, 
on the westernmost portion of Long Island. It was created in the mid–19th century from local 
tidal wetlands and freshwater streams, and by the end of that century was very polluted due 
to heavy industrial use. Most industrial tenants had stopped using the canal by the middle of 
the 20th century, but it remained one of the most polluted bodies of water in the United States. 
Its proximity to Manhattan and upper-class Brooklyn neighborhoods has attracted waterfront 
redevelopment in recent years, alongside attempts at environmental cleanup. 
It was designated a Superfund site in 2009.
"""

class TestQuestionDifficulty(unittest.TestCase):

    def setUp(self):
        self.m_project = Project(a_name=m_project_name, a_transcript=m_transcript)
        self.m_project.initialise()

        self.m_project.generate_segments_summaries()
        self.m_project.generate_transcript_keywords()
        self.m_project.generate_summary_keywords()

        self.m_project.generate_questions_of_type(SegmentData.saqs_dict_key())
        self.m_project.generate_questions_of_type(SegmentData.mcqs_dict_key())
        self.m_project.generate_questions_of_type(SegmentData.blqs_dict_key())
        self.m_project.generate_questions_of_type(SegmentData.gfqs_dict_key())

        self.m_project.evaluate_all_segments()


    def test_question_difficulty_evaluation(self):
        """
        This test evaluates the difficulty level of the generated questions for each 
        segment. The expected score ranges from -1 to 1 based on how difficult it is 
        to find the answer in the provided transcript.
        """
        t_number_of_segments: int = self.m_project.get_number_of_segments()

        for i in range(t_number_of_segments):
            t_segment_data: dict = self.m_project.get_segment_data(i)
            t_saqs: list = t_segment_data[SegmentData.saqs_dict_key()]
            t_mcqs: list = t_segment_data[SegmentData.mcqs_dict_key()]
            t_gfqs: list = t_segment_data[SegmentData.gfqs_dict_key()]
            t_blqs: list = t_segment_data[SegmentData.blqs_dict_key()]

            # Evaluate difficulty for SAQs
            for t_saq in t_saqs:
                t_question_eval = t_saq["question_evaluation"]
                t_difficulty = t_question_eval["question_difficulty"]["score"]
                t_reason = t_question_eval["question_difficulty"]["reasoning"]
                self.assertGreaterEqual(t_difficulty, -1, "Invalid difficulty score for SAQ.")
                self.assertLessEqual(t_difficulty, 1, "Invalid difficulty score for SAQ.")
                self.assertIsInstance(t_reason, str, "Difficulty reasoning should be a string.")
                print(f"SAQ Difficulty: {t_difficulty}, Reason: {t_reason}")

            # Evaluate difficulty for MCQs
            for t_mcq in t_mcqs:
                t_question_eval = t_mcq["question_evaluation"]
                t_difficulty = t_question_eval["question_difficulty"]["score"]
                t_reason = t_question_eval["question_difficulty"]["reasoning"]
                self.assertGreaterEqual(t_difficulty, -1, "Invalid difficulty score for MCQ.")
                self.assertLessEqual(t_difficulty, 1, "Invalid difficulty score for MCQ.")
                self.assertIsInstance(t_reason, str, "Difficulty reasoning should be a string.")
                print(f"MCQ Difficulty: {t_difficulty}, Reason: {t_reason}")

            # Evaluate difficulty for GFQs
            for t_gfq in t_gfqs:
                t_question_eval = t_gfq["question_evaluation"]
                t_difficulty = t_question_eval["question_difficulty"]["score"]
                t_reason = t_question_eval["question_difficulty"]["reasoning"]
                self.assertGreaterEqual(t_difficulty, -1, "Invalid difficulty score for GFQ.")
                self.assertLessEqual(t_difficulty, 1, "Invalid difficulty score for GFQ.")
                self.assertIsInstance(t_reason, str, "Difficulty reasoning should be a string.")
                print(f"GFQ Difficulty: {t_difficulty}, Reason: {t_reason}")

            # Evaluate difficulty for BLQs
            for t_blq in t_blqs:
                t_question_eval = t_blq["question_evaluation"]
                t_difficulty = t_question_eval["question_difficulty"]["score"]
                t_reason = t_question_eval["question_difficulty"]["reasoning"]
                self.assertGreaterEqual(t_difficulty, -1, "Invalid difficulty score for BLQ.")
                self.assertLessEqual(t_difficulty, 1, "Invalid difficulty score for BLQ.")
                self.assertIsInstance(t_reason, str, "Difficulty reasoning should be a string.")
                print(f"BLQ Difficulty: {t_difficulty}, Reason: {t_reason}")


if __name__ == "__main__":
    unittest.main()
