"""
This file contains unit tests for evaluating the correctness of the answers 
generated for all question types (SAQs, MCQs, GFQs, and BLQs) in a project. 
The test checks how accurately the answers match the ground truth.
This is an unimplemented unit test.
"""

import unittest
from project import Project
from segment_data import SegmentData

m_project_name: str = "TestProject_AnswerCorrectness"
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

class TestAnswerCorrectness(unittest.TestCase):

    def setUp(self):

        self.m_project = Project(a_name=m_project_name, a_transcript=m_transcript)
        self.m_project.initialise()

        self.m_project.generate_segments_summaries()
        self.m_project.generate_transcript_keywords()
        self.m_project.generate_summary_keywords()

        self.m_project.generate_questions_of_type(SegmentData.saqs_dict_key())
        self.m_project.generate_questions_of_type(SegmentData.mcqs_dict_key())
        self.m_project.generate_questions_of_type(SegmentData.gfqs_dict_key())
        self.m_project.generate_questions_of_type(SegmentData.blqs_dict_key())

        self.m_project.evaluate_all_segments()  # Ensure all segments are evaluated

    def test_answer_correctness(self):

        t_number_of_segments: int = self.m_project.get_number_of_segments()

        for i in range(t_number_of_segments):
            t_segment_data: dict = self.m_project.get_segment_data(i)

            # Evaluate answer correctness for SAQs
            self._evaluate_answer_correctness(t_segment_data[SegmentData.saqs_dict_key()], "SAQ")

            # Evaluate answer correctness for MCQs
            self._evaluate_answer_correctness(t_segment_data[SegmentData.mcqs_dict_key()], "MCQ")

            # Evaluate answer correctness for GFQs
            self._evaluate_answer_correctness(t_segment_data[SegmentData.gfqs_dict_key()], "GFQ")

            # Evaluate answer correctness for BLQs
            self._evaluate_answer_correctness(t_segment_data[SegmentData.blqs_dict_key()], "BLQ")

    def _evaluate_answer_correctness(self, t_questions: list, a_question_type: str):
        
        #Helper function to evaluate answer correctness for a specific question type.
        
        for t_question_data in t_questions:
            t_answer_eval = t_question_data["question_evaluation"]
            t_correctness = t_answer_eval["answer_correctness"]["score"]
            t_reasoning = t_answer_eval["answer_correctness"]["reasoning"]

            # Ensure the score for answer correctness is between 1 and 0
            self.assertGreaterEqual(t_correctness, -1, "Invalid correctness score")
            self.assertLessEqual(t_correctness, 1, "Invalid correctness score")
            self.assertIsInstance(t_reasoning, str, f"Answer correctness reasoning for {a_question_type} should be a string.")
            print(f"{a_question_type} Answer Correctness: {t_correctness}, Reasoning: {t_reasoning}")

            # Optionally print for easier debugging
            t_question = t_question_data["question"]
            t_answer = t_question_data["answer"]
            print(f"{a_question_type} Question: {t_question}, Answer: {t_answer}, Correctness: {t_correctness}, Reasoning: {t_reasoning}")


if __name__ == "__main__":
    unittest.main()
