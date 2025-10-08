import unittest
import unittest.main
from project import Project
from segment_data import SegmentData
import re

#Description
"""
Objection: To test if the summary generation is success.
Expected Result: 
- The text segments are summarized under the defined summary size limit.
- The text segments are stored in the correct json segment file.
- The summary is relevant to the text provided to summarize.
"""

#Params
m_project_name: str = "TestProject"
m_transcript: str = "The Gowanus Canal is a 1.8-mile-long (2.9 km) canal in the New York City borough of Brooklyn, on the westernmost portion of Long Island. It was created in the mid–19th century from local tidal wetlands and freshwater streams, and by the end of that century was very polluted due to heavy industrial use. Most industrial tenants had stopped using the canal by the middle of the 20th century, but it remained one of the most polluted bodies of water in the United States. Its proximity to Manhattan and upper-class Brooklyn neighborhoods has attracted waterfront redevelopment in recent years, alongside attempts at environmental cleanup. It was designated a Superfund site in 2009."
t_project = Project(a_name = m_project_name, a_transcript = m_transcript)

class UnitTest2(unittest.TestCase):
    def __initialize__(self):
        t_project.initialise()

    def test_generate_summary(self):
        t_project.generate_segments_summaries()

        for i in range(t_project.get_number_of_segments()):
            t_segment_data: dict = t_project.get_segment_data(i)
            t_summary: str = t_segment_data[SegmentData.summary_dict_key()]

            # check if the summary is in correct variable type
            self.assertTrue(isinstance(t_summary, str))

            # check if the summary is under defined size limit
            self.assertGreaterEqual(t_project.summaries_word_limit, len(t_summary.split(" ")))

            print('==-')
            print(t_summary.strip())
            list1 = re.sub("[^\w]", " ",  t_summary).split()
            list2 = re.sub("[^\w]", " ",  m_transcript).split()
            print(m_transcript.strip())
            # check if the summary is relevant
            # extract keywords from summary & transcript then check for overlap
            # if there is overlap, it means the summary is relevant to the text
            self.assertFalse(set(list1).isdisjoint(set(list2)))

if (__name__ == "__main__"):
    unittest.main()