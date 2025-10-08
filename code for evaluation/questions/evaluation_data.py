from dataclasses import dataclass

@dataclass
class EvaluationData:
    score: float = -1
    reasoning: str = ""

    @classmethod
    def score_dict_key(cls) -> str:
        return "score"
    
    @classmethod
    def reasoning_dict_key(cls) -> str:
        return "reasoning"

    @staticmethod
    def dict_to_object(a_dict: dict):
        try:
            t_evaluation_object = EvaluationData()
            t_evaluation_object.score = a_dict[EvaluationData.score_dict_key()]
            t_evaluation_object.reasoning = a_dict[EvaluationData.reasoning_dict_key()]
            return t_evaluation_object
        except Exception as t_exception:
            print("The dictionary provided to convert to an EvaluationData object is not valid! Return empty object...")
            print(f"Dict provided:\n{a_dict}")
            print(f"Exception:\n{t_exception}")
            return EvaluationData()

        