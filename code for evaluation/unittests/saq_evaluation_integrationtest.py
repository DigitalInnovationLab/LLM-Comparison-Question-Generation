"""
This file contains an integration test for evaluating the SAQs (short-answer questions) 
in a project based on reading comprehension, relevance, question difficulty, 
question clarity, and answer accuracy. 
The test uses the stored question, text, and keywords after the SAQ generation integration test.
Test Case 4.2.8 in Test Case Standards document
"""

import unittest
from project import Project
from segment_data import SegmentData

m_project_name: str = "TestProject_SAQ_Evaluation"
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

class TestSAQEvaluation(unittest.TestCase):

    def setUp(self):

        self.m_project = Project(a_name=m_project_name, a_transcript=m_transcript)
        self.m_project.initialise()

        self.m_project.generate_segments_summaries()
        self.m_project.generate_transcript_keywords()
        self.m_project.generate_summary_keywords()
        self.m_project.generate_questions_of_type(SegmentData.saqs_dict_key())

        self.m_project.evaluate_all_segments()


    def test_evaluate_saqs(self):
        """
        This test evaluates the SAQs based on reading comprehension, relevance, 
        question difficulty, question clarity, and answer accuracy.
        """
        t_number_of_segments: int = self.m_project.get_number_of_segments()

        for i in range(t_number_of_segments):
            t_segment_data: dict = self.m_project.get_segment_data(i)
            t_saqs: list = t_segment_data[SegmentData.saqs_dict_key()]

            # Evaluate each SAQ for multiple criteria
            for t_saq in t_saqs:
                t_question_eval = t_saq["question_evaluation"]

                # Evaluate reading comprehension
                t_reading_comprehension = t_question_eval["reading_comprehension"]["score"]
                t_reasoning_reading = t_question_eval["reading_comprehension"]["reasoning"]
                self.assertGreaterEqual(t_reading_comprehension, -1, "Invalid reading comprehension score.")
                self.assertLessEqual(t_reading_comprehension, 1, "Invalid reading comprehension score.")
                self.assertIsInstance(t_reasoning_reading, str, "Reading comprehension reasoning should be a string.")
                print(f"Reading Comprehension: {t_reading_comprehension}, Reasoning: {t_reasoning_reading}")

                # Evaluate relevance
                t_relevance = t_question_eval["relevance"]["score"]
                t_reasoning_relevance = t_question_eval["relevance"]["reasoning"]
                self.assertGreaterEqual(t_relevance, -1, "Invalid relevance score.")
                self.assertLessEqual(t_relevance, 1, "Invalid relevance score.")
                self.assertIsInstance(t_reasoning_relevance, str, "Relevance reasoning should be a string.")
                print(f"Relevance: {t_relevance}, Reasoning: {t_reasoning_relevance}")

                # Evaluate question difficulty
                t_difficulty = t_question_eval["question_difficulty"]["score"]
                t_reasoning_difficulty = t_question_eval["question_difficulty"]["reasoning"]
                self.assertGreaterEqual(t_difficulty, -1, "Invalid difficulty score.")
                self.assertLessEqual(t_difficulty, 1, "Invalid difficulty score.")
                self.assertIsInstance(t_reasoning_difficulty, str, "Difficulty reasoning should be a string.")
                print(f"Difficulty: {t_difficulty}, Reasoning: {t_reasoning_difficulty}")

                # Evaluate question clarity
                t_clarity = t_question_eval["question_clarity"]["score"]
                t_reasoning_clarity = t_question_eval["question_clarity"]["reasoning"]
                self.assertGreaterEqual(t_clarity, -1, "Invalid clarity score.")
                self.assertLessEqual(t_clarity, 1, "Invalid clarity score.")
                self.assertIsInstance(t_reasoning_clarity, str, "Clarity reasoning should be a string.")
                print(f"Clarity: {t_clarity}, Reasoning: {t_reasoning_clarity}")

                # Evaluate answer accuracy
                t_accuracy = t_question_eval["answer_correctness"]["score"]
                t_reasoning_accuracy = t_question_eval["answer_correctness"]["reasoning"]
                self.assertGreaterEqual(t_accuracy, -1, "Invalid answer accuracy score.")
                self.assertLessEqual(t_accuracy, 1, "Invalid answer accuracy score.")
                self.assertIsInstance(t_reasoning_accuracy, str, "Accuracy reasoning should be a string.")
                print(f"Answer Accuracy: {t_accuracy}, Reasoning: {t_reasoning_accuracy}")

if __name__ == "__main__":
    unittest.main()
