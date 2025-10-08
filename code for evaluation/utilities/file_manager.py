#Python Imports
import os
import json
from pathlib import Path
import shutil


def create_json_file(a_file_path: Path, a_dictionary: dict):
    try: 
        with open(str(a_file_path), "w", encoding = "utf8") as t_json_file:
            json.dump(a_dictionary, t_json_file, indent = 4)
    except Exception as e:
        print(f"Error in creating the json file at path {a_file_path}. Error: {e}")


def load_json_file_data(a_file_path: Path) -> dict:
    try:
        with open(str(a_file_path), "r", encoding = "utf8") as t_json_file:
            return json.load(t_json_file)
    except Exception as e:
        print(e)
        return {}
    

def load_text_file_into_list(a_text_file_path: Path, a_sanitize: bool = True)-> list[str]:
    t_read_text_file_lines = []
    t_output_text_file_lines = []

    try: 
        with open(str(a_text_file_path), "r", encoding = "utf8") as t_text_file:
            t_read_text_file_lines = t_text_file.readlines()
    except Exception as e:
        print(e)
        return t_output_text_file_lines

    for i, t_read_text_file_line in enumerate(t_read_text_file_lines):
        t_output_text_file_line = t_read_text_file_line.strip()

        if (t_output_text_file_line == ""):
            continue
        elif (a_sanitize == True):
            t_output_text_file_line = t_output_text_file_line.replace('\n', '')

        t_output_text_file_lines.append(t_output_text_file_line)

    return t_output_text_file_lines


def load_text_file_into_string(a_text_file_path: Path, a_sanitize: bool = True) -> str:
    t_text_file_lines = load_text_file_into_list(
        a_text_file_path = a_text_file_path, 
        a_sanitize = a_sanitize
    )
    return "".join(t_text_file_lines)


def create_folder_if_not_exist(a_folder_path: Path):
    if (os.path.exists(a_folder_path) == False):
        print(f"Creating folder... {str(a_folder_path)}")
        os.makedirs(a_folder_path)


def get_folder_file_paths_list(a_path: Path) -> list[Path]:
    t_path_list: list[Path] = []

    try: 
        t_path_str_list: list[str] = os.listdir(str(a_path))
        for i in range(len(t_path_str_list)):
            t_path_list.append(Path(t_path_str_list[i]))   
    except Exception as e:
        print(e)

    return t_path_list
    


def delete_folder(a_path: Path) -> bool:
    if (a_path.exists() == False):
        return False
    
    try:
        shutil.rmtree(a_path)
    except:
        return False
    
    print("Deleted folder " + str(a_path))
    return True


def delete_file(a_path: Path) -> bool:
    if (a_path.exists() == False):
        print(f"The file at {str(a_path)} does not exist.")
        return False
    
    try:
        os.remove(a_path)
    except:
        print(f"Could not delete the file at {str(a_path)}.")
        return False
    
    print("Deleted file " + str(a_path))
    return True


#returns true or false depending on where it made the file or not.
def create_segment_file(a_file_path: Path, a_data: dict) -> bool:
    if (a_file_path.parent.exists() == False):
        print("File path parent folder given to create a segment file does not exist.")
        return False

    t_versions_in_folder: list[str] = os.listdir(a_file_path.parent)
    for i in range(len(t_versions_in_folder)):
        with open(str(a_file_path.parent / t_versions_in_folder[i]), "r", encoding = "utf8") as t_version_file:
            t_data = json.load(t_version_file)
            if (t_data == a_data):
                print("There is a file with the same contents as this segment data. "
                    + "You must makes changes before saving another segment file.")
                return False

    #Debugging
    print(f"Creating a segment file at path {str(a_file_path)}")

    create_json_file(a_file_path, a_data)
    return True
