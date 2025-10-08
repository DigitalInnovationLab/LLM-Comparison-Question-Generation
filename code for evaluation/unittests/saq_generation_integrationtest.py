"""
This file contains integration tests for validating the generation of SAQs (short-answer questions) 
based on the transcript keywords after the transcript keyword integration test.
The test ensures the correct number and type of questions are generated and stored properly 
in the corresponding JSON arrays in the project segment files.
Integration Test 4.2.4 in the Test Case Standards Document
"""

import unittest
from project import Project
from segment_data import SegmentData
from keywords.keywords_handler import get_words_frequency_from_text

m_project_name: str = "TestProject_SAQ_Integration"
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

class TestSAQIntegration(unittest.TestCase):

    def setUp(self):

        self.m_project = Project(a_name=m_project_name, a_transcript=m_transcript)
        self.m_project.initialise()

        self.m_project.generate_segments_summaries()
        self.m_project.generate_transcript_keywords()
        self.m_project.generate_summary_keywords()

        self.m_project.evaluate_all_segments()


    def test_saq_generation(self):
        """
        This test evaluates the generation of SAQs based on the stored transcript 
        and keywords. The expected result is the correct number of SAQs, 
        stored in the appropriate JSON segment files.
        """
        t_number_of_segments: int = self.m_project.get_number_of_segments()

        for i in range(t_number_of_segments):
            t_segment_data: dict = self.m_project.get_segment_data(i)
            t_summary_keywords: dict = t_segment_data[SegmentData.generated_summary_keywords_dict_key()]
            t_transcript_keywords: dict = t_segment_data[SegmentData.generated_transcript_keywords_dict_key()]

            # Ensure keywords exist before generating questions
            self.assertGreater(len(t_summary_keywords), 0, "Summary keywords are missing.")
            self.assertGreater(len(t_transcript_keywords), 0, "Transcript keywords are missing.")

        # Generate SAQs based on keywords
        self.m_project.generate_questions_of_type(SegmentData.saqs_dict_key())

        for i in range(t_number_of_segments):
            t_segment_data: dict = self.m_project.get_segment_data(i)
            t_saqs: list = t_segment_data[SegmentData.saqs_dict_key()]

            # Check SAQs generation
            print(f"Testing SAQs for segment {i}")
            self.assertTrue(isinstance(t_saqs, list), "SAQs should be stored as a list.")
            self.assertGreater(len(t_saqs), 0, "No SAQs generated.")
            self.assertGreaterEqual(self.m_project.number_of_questions, len(t_saqs), "Fewer than expected SAQs generated.")

            # Ensure questions are correctly stored in the JSON
            for t_saq in t_saqs:
                self.assertIn("question", t_saq, "SAQ does not have a 'question' field.")
                self.assertIn("answer", t_saq, "SAQ does not have an 'answer' field.")
                print(f"SAQ: {t_saq['question']}, Answer: {t_saq['answer']}")


if __name__ == "__main__":
    unittest.main()