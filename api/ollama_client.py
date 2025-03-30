import requests

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434", model="llama"):
        """
        Initialize the Ollama API client.
        :param base_url: The base URL of the Ollama API (default: http://localhost:11434).
        :param model: The name of the model to use (default: llama).
        """
        self.base_url = base_url
        self.model = model

    def generate_response(self, prompt):
        """
        Send a prompt to the Ollama API and retrieve the response.
        :param prompt: The input prompt to send to the model.
        :return: The response text from the model.
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "max_new_tokens": 512,
            "temperature": 0.7,
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()  # Raise an error for HTTP errors
            data = response.json()
            return data.get("response", "")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to connect to Ollama API: {e}")

    def set_model(self, model):
        """
        Set the model to use for the API requests.
        :param model: The name of the model to use.
        """
        self.model = model