import unittest
import unittest.main
from project import Project
from segment_data import SegmentData

#Description
"""
Objection: To test that BLQs are generated successfully.
Expected Result: 
- Generates correct number of questions.
- Generates correct question type.
- The questions are based on the text provided & reflect keywords provided.
- Answers are generated in JSON file.
"""

#Params
m_project_name: str = "TestProject"
m_transcript: str = "The Gowanus Canal is a 1.8-mile-long (2.9 km) canal in the New York City borough of Brooklyn, on the westernmost portion of Long Island. It was created in the mid–19th century from local tidal wetlands and freshwater streams, and by the end of that century was very polluted due to heavy industrial use. Most industrial tenants had stopped using the canal by the middle of the 20th century, but it remained one of the most polluted bodies of water in the United States. Its proximity to Manhattan and upper-class Brooklyn neighborhoods has attracted waterfront redevelopment in recent years, alongside attempts at environmental cleanup. It was designated a Superfund site in 2009."
t_project = Project(a_name = m_project_name, a_transcript = m_transcript)

class IntegrationTest6(unittest.TestCase):
    def __initialize__(self):
        t_project.initialise()

    # focus on BLQs
    def test_generate_questions(self):
        t_project.generate_segments_summaries()
        t_project.generate_summary_keywords()
        t_number_of_segments: int = t_project.get_number_of_segments()

        for i in range(t_number_of_segments):
            t_segment_data: dict = t_project.get_segment_data(i)
            t_summary: str = t_segment_data[SegmentData.summary_dict_key()]
            t_summary_keywords : dict = t_segment_data[SegmentData.generated_summary_keywords_dict_key()]
            t_transcript_keywords: dict = t_segment_data[SegmentData.generated_transcript_keywords_dict_key()]

            if (t_summary == ""):
                print(f"The summary is not generated for index {i}. Cannot test BLQ generation. Run the summary generation test first.")
                return
            
            if (t_summary_keywords == {}):
                print(f"Summary keywords are not generated from index {i}. Cannot test BLQ generation. Run Summary keywords generation test first.")
                return
            
            if (t_transcript_keywords == {}):
                print(f"Transcript keywords are not generated from index {i}. Cannot test BLQ generation. Run Transcript keywords generation test first.")
                return
            
        t_project.generate_questions_of_type(SegmentData.blqs_dict_key())
            
        for i in range(t_number_of_segments):
            t_segment_data: dict = t_project.get_segment_data(i)
            t_blqs: list = t_segment_data[SegmentData.blqs_dict_key()]

            #Check BLQs
            print(f"Testing BLQs for segment {i}")
            self.assertTrue(isinstance(t_blqs, list))
            self.assertGreaterEqual(t_project.number_of_questions, len(t_blqs))
            self.assertGreater(len(t_blqs), 0)
        
        # Ensure questions are correctly stored in the JSON file
        for t_blq in t_blqs:
            self.assertIn("question", t_blq, "BLQ does not have a 'question' field.")
            self.assertIn("answer", t_blq, "BLQ does not have an 'answer' field.")

if (__name__ == "__main__"):
    unittest.main()