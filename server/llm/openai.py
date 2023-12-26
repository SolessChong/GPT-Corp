# llm/openai.py

class OpenAIConfig:
    @staticmethod
    def get_credentials():
        # These should be replaced with environment variables or a secure method to store credentials
        URL = "https://ai98.vip/v1"
        API_KEY = "sk-ILF01mttjbDHoF7pA01aB6690d3643B98c1411D186725aEa"

        # Jingcheng
        # URL = "https://api.jingcheng.love/v1"
        # API_KEY = "sk-CPK90xN6naFR0lTuB8Da8e67Ab054cF4A5978cAa4dC6B445"
        return URL, API_KEY
