#Python imports
from pathlib import Path
import time

#External Imports
from langchain.prompts import FewShotPromptTemplate
from langchain.prompts import PromptTemplate

#Custom Imports
from utilities import file_manager

class FewShotRequestData:
    #Example data dict keys
    input_key = "user"
    output_key = "ai"

    examples_prompt = PromptTemplate.from_template("user: {" + input_key + "}\nai-response: {" + output_key + "}") 

    def __init__(
            self, 
            a_guidance_data_folder_path: Path,
            a_files_prefix: str,
            a_suffix_variables_names: list[str]
        ):
        #Folder existence check
        if (a_guidance_data_folder_path.exists() == False):
            print(f"\nThe guidance data folder provided does not exist. File path: {str(a_guidance_data_folder_path)}")
            return None

        t_prefix_strings_file_path = a_guidance_data_folder_path / (a_files_prefix + "-prefix-strings.txt")
        t_raw_examples_file_path = a_guidance_data_folder_path / (a_files_prefix + "-raw-examples.txt")
        t_suffix_templates_file_path = a_guidance_data_folder_path / (a_files_prefix + "-suffix-templates.txt")

        #File existence checks
        if (t_prefix_strings_file_path.exists() == False):
            print(f"\nThe prefix file provided does not exist. File path: {str(t_prefix_strings_file_path)}")
            return None
        if (t_raw_examples_file_path.exists() == False):
            print(f"\nThe raw examples file provided does not exist. File path: {str(t_raw_examples_file_path)}")
            return None
        if (t_suffix_templates_file_path.exists() == False):
            print(f"\nThe suffix templates file provided does not exist. File path: {str(t_suffix_templates_file_path)}")
            return None
        
        self.name = a_files_prefix

        self.suffix_templates: list[str] = file_manager.load_text_file_into_list(t_suffix_templates_file_path)
        self.prefix_strings: list[str] = file_manager.load_text_file_into_list(t_prefix_strings_file_path)
        self.suffix_variables_names: list[str] = a_suffix_variables_names

        #A list. An input variable per line.
        self.raw_examples = file_manager.load_text_file_into_list(t_raw_examples_file_path)
        
        #Debug
        #print(f"\nCollected Guidance data from {str(a_guidance_data_folder_path)}...")
        #print(f"\nPrefixes:\n{self.prefix_strings}")
        #print(f"\nExamples:\n{self.raw_examples}")
        #print(f"Formatted Examples:\n{self.get_formatted_examples()}")
        #print(f"\nSuffixes:\n{self.suffix_templates}")
        
        
    
    def get_formatted_examples(self, a_suffix_index: int = 0) -> list[dict]:
        t_suffix_template = self.suffix_templates[a_suffix_index]
        t_raw_examples = self.raw_examples
        t_suffix_variables_names = self.suffix_variables_names

        t_formatted_examples_list = []
        t_number_of_lines_per_example = len(t_suffix_variables_names) + 1 # +1 for the output line
        t_number_of_examples = int(len(t_raw_examples) / t_number_of_lines_per_example)

        for i in range(t_number_of_examples):
            t_input = t_suffix_template
            #The last line in the given example should be the output and we dont want to include that into the input, thus the -1
            for j in range(0, t_number_of_lines_per_example - 1):
                t_input = t_input.replace("{" + t_suffix_variables_names[j] + "}", t_raw_examples[i * t_number_of_lines_per_example + j].strip())
            
            t_output = t_raw_examples[i * t_number_of_lines_per_example + (t_number_of_lines_per_example - 1)]
        
            t_formatted_example = {
                FewShotRequestData.input_key : t_input,
                FewShotRequestData.output_key : t_output
            }
            t_formatted_examples_list.append(t_formatted_example)

        return t_formatted_examples_list
    

    def send_request(
            self,
            a_prefix_index: int,
            a_suffix: str,
            a_llm
        ) -> str:
        try: 
            print(f"\nUsing'{a_llm.model_name}'.")
        except:
            pass

        print(f"Sending few shot request for {self.name}.")

        t_request = FewShotPromptTemplate(
            prefix = self.prefix_strings[a_prefix_index],
            example_prompt = FewShotRequestData.examples_prompt,
            examples = self.get_formatted_examples(),
            suffix = a_suffix,
            input_variables = []
        )

        #Debug
        #print(f"\nFormatted response before sending: {t_request.format()}")

        time.sleep(0.25) #Artificially add delay to prevent reaching the token limit easily.
        t_response = a_llm.invoke(t_request.format())
        
        #Debug
        print(f"\nLLM Raw Response: {t_response}")
        
        return t_response.content