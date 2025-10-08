import time
from enum import Enum

#External Imports
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_mistralai import ChatMistralAI
from langchain_together import ChatTogether

from dotenv import load_dotenv
load_dotenv()

chatGPT_model_name = "gpt-4o-mini"
claude_model_name = "claude-3-5-sonnet-20240620"
gemma_model_name = "google/gemma-2-27b-it"
mistral_model_name = "mistral-large-2407"
llama_model_name = "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo"
wizard_model_name = "microsoft/WizardLM-2-8x22B"
databricks_model_name = "databricks/dbrx-instruct"
gryphe_model_name = "Gryphe/MythoMax-L2-13b-Lite"
upstage_model_name = "upstage/SOLAR-10.7B-Instruct-v1.0"
qwen_model_name = "Qwen/Qwen2.5-72B-Instruct-Turbo"
deep_seek_model_name = "deepseek-ai/deepseek-llm-67b-chat"


class LLmType(Enum):
    Question = 1
    Transcript = 2


def get_generation_llm(a_model_name: str, a_llm_type: LLmType):

    if (isinstance(a_llm_type, LLmType) == False):
        print("Must give valid LLM type.")
        return
    
    #Default
    t_context_size: int = 2048
    t_temp = 0.6

    if (a_llm_type == LLmType.Question):
        t_context_size = 2048
        t_temp = 0.6
    elif (a_llm_type == LLmType.Transcript):
        t_context_size = 2048
        t_temp = 0.15

    if (a_model_name == "chatgpt"):
        return ChatOpenAI(model = chatGPT_model_name, max_tokens = t_context_size, temperature = t_temp)

    elif (a_model_name == "claude"):
        return ChatAnthropic(model = claude_model_name, max_tokens = t_context_size, temperature = t_temp)
    
    elif (a_model_name == "gemma"):
        return ChatTogether(model = gemma_model_name, max_tokens = t_context_size, temperature = t_temp)

    elif (a_model_name == "mistral"):
        return ChatMistralAI(model = mistral_model_name, max_tokens = t_context_size, temperature = t_temp)
    
    elif (a_model_name == "llama"):
        return ChatTogether(model = llama_model_name, max_tokens = t_context_size, temperature = t_temp)
    
    elif (a_model_name == 'wizard'):
        return ChatTogether(model = wizard_model_name, max_tokens = t_context_size, temperature = t_temp)
    
    elif(a_model_name == "databricks"):
        return ChatTogether(model = databricks_model_name, max_tokens = t_context_size, temperature = t_temp)
    
    elif (a_model_name == "gryphe"):
        return ChatTogether(model = gryphe_model_name, max_tokens = t_context_size, temperature = t_temp)
    
    elif (a_model_name == "upstage"):
        return ChatTogether(model = upstage_model_name, max_tokens = t_context_size, temperature = t_temp)
    
    elif (a_model_name == "qwen"):
        return ChatTogether(model = qwen_model_name, max_tokens = t_context_size, temperature = t_temp)
    
    elif (a_model_name == "deep_seek"):
        return ChatTogether(model = deep_seek_model_name, max_tokens = t_context_size, temperature = t_temp)
    
    else:
        print("Not a valid model name.")
        return

#Questions Formatting
questions_formatting_llm = ChatOpenAI(model = chatGPT_model_name, max_tokens = 2048, temperature = 0.5)

#Keywords Formatting
keywords_formatting_llm = ChatOpenAI(model = chatGPT_model_name, max_tokens = 2048, temperature = 0.5)

#Summary Formatting
summary_formatting_llm = ChatOpenAI(model = chatGPT_model_name, max_tokens = 2048, temperature = 0.5)


def simple_request(a_llm, a_prompt: str) -> str:
    time.sleep(0.25) #Artificially add delay to prevent reaching the token limit too easily.
    return a_llm.invoke(a_prompt).content
