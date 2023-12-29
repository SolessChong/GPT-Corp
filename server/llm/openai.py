# llm/openai.py

class OpenAIConfig:
    BASIC_RATE = 0.001 / 1000

    # Cost ratio for different models
    MODEL_RATIOS = {
        'gpt-3.5-turbo': 2,
        'gpt-4-1106-preview': 30,
        'gpt-4-all': 30
    }

    @staticmethod
    def get_credentials():
        # These should be replaced with environment variables or a secure method to store credentials
        URL = "https://ai98.vip/v1"
        API_KEY = "sk-ILF01mttjbDHoF7pA01aB6690d3643B98c1411D186725aEa"

        # Jingcheng
        # URL = "https://api.jingcheng.love/v1"
        # API_KEY = "sk-CPK90xN6naFR0lTuB8Da8e67Ab054cF4A5978cAa4dC6B445"
        return URL, API_KEY

    @classmethod
    def get_model_cost_ratios(cls):
        return {model: cls.BASIC_RATE * ratio for model, ratio in cls.MODEL_RATIOS.items()}