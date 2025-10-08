import unittest
import unittest.main
from project import Project

#Description
"""
Objection: To test if the project creation is success.
Expected Result: 
- The project is created with correct folder system.
- The project has an appropriate number of JSON segment files with segmented transcript text and the text is split correctly among segments.
- The text is in the correct order with the context of text segment maintained.
"""

#Params
m_project_name: str = "TestProject"
m_transcript: str = "The Gowanus Canal is a 1.8-mile-long (2.9 km) canal in the New York City borough of Brooklyn, on the westernmost portion of Long Island. It was created in the mid–19th century from local tidal wetlands and freshwater streams, and by the end of that century was very polluted due to heavy industrial use. Most industrial tenants had stopped using the canal by the middle of the 20th century, but it remained one of the most polluted bodies of water in the United States. Its proximity to Manhattan and upper-class Brooklyn neighborhoods has attracted waterfront redevelopment in recent years, alongside attempts at environmental cleanup. It was designated a Superfund site in 2009."
t_project = Project(a_name = m_project_name, a_transcript = m_transcript)

class UnitTest1(unittest.TestCase):
    def __initialize__(self):
        t_project.initialise()

    def test_create_project(self):
        # check if project is created
        self.assertIsNotNone(t_project)

        # check if project has correct folder structure
        self.assertTrue(t_project.files_schema.project_folder_path.exists())
        self.assertTrue(t_project.files_schema.segments_folder_path.exists())
        self.assertTrue(t_project.files_schema.keywords_history_folder_path.exists())
    
    def test_correct_json_files_number(self):
        # check number of json files are correct
        # this input should result in 2 segment files
        self.assertEqual(t_project.get_number_of_segments(), 2)

    def test_correct_splitted_segments(self):
        # check if the splitted segments are correct
        # and are in correct order
        self.assertEqual(m_transcript.strip(), t_project.get_full_transcript().strip())

if (__name__ == "__main__"):
    unittest.main()