import requests
from loguru import logger

class LLM:
    def __init__(self, config):
        self.api_key = config["api_key"]
        self.model = "mistralai/Mixtral-8x7B-Instruct-v0.1"  # Valid model
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"

    def generate_response(self, prompt):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "inputs": prompt,
            "parameters": {"max_length": 200, "temperature": 0.7}
        }
        try:
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            return result[0]["generated_text"].strip() if result else ""
        except requests.exceptions.HTTPError as e:
            logger.error(f"LLM HTTP error: {e}")
            return "I'm sorry, I encountered an issue with the language model. Could you repeat your query?"
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return "I'm sorry, I encountered an issue. Could you repeat?"