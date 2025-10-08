from pathlib import Path

class ProjectFilesSchema:

    #Storing all necessary naming convention for files or folders that are created n number of times.
    m_segment_file_name: str = "segment-file-"

    def __init__(self, a_project_folder_path: Path):
        #Storing all necessary folder paths and names
        self.project_folder_path: Path = a_project_folder_path

        self.segments_folder_path: Path = self.project_folder_path / "Segments"
        self.keywords_history_folder_path: Path = self.project_folder_path / "Keywords-History"
        self.project_settings_path: Path = self.project_folder_path / "settings.json"
    
    @staticmethod
    def get_segment_file_name(a_segment_number: int) -> str:
        return ProjectFilesSchema.m_segment_file_name + str(a_segment_number) + ".json"
    
    def get_segment_file_path(self, a_segment_number: int) -> Path:
        return self.segments_folder_path / ProjectFilesSchema.get_segment_file_name(a_segment_number)
    
    
    def is_project_file_system_valid(self) -> bool:
        if (self.segments_folder_path.exists() == False):
            return False
    
        #if (self.keywords_history_folder_path.exists() == False):
            #return False
        
        return True