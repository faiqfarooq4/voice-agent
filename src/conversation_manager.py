from enum import Enum
from loguru import logger

class Stage(Enum):
    FRONTER = "Fronter"
    VERIFIER = "Verifier"
    CLOSER = "Closer"

class ConversationManager:
    def __init__(self, llm):
        self.llm = llm
        self.stage = Stage.FRONTER
        self.user_data = {"name": None, "query": None, "verified": False, "account_id": None}
        self.history = []
        self.script = {
            Stage.FRONTER: [
                "Hello, this is Horizon Telecom. My name is Assistant. May I have your name, please?",
                "Thank you, {name}. I’m reaching out to ensure you’re getting the best from our telecom services. Are you interested in exploring our latest plans or resolving any issues with your account?"
            ],
            Stage.VERIFIER: [
                "Great, {name}. It sounds like you’re interested in {query}. Could you provide your account ID or let me know if this is about billing, technical support, or a new plan?",
                "Thank you, {name}. Just to confirm, you’d like assistance with {query}. Is that correct?"
            ],
            Stage.CLOSER: [
                "Perfect, {name}. Let’s address your {query}. {resolution}",
                "Is there anything else I can assist you with, {name}? We have some exclusive offers on premium plans if you’re interested!"
            ]
        }

    def process_input(self, user_input):
        self.history.append({"role": "user", "content": user_input})

        if not user_input or self.is_irrelevant(user_input):
            response = self.handle_irrelevant(user_input)
            return response, self.stage.value

        if self.stage == Stage.FRONTER:
            response = self.handle_fronter(user_input)
        elif self.stage == Stage.VERIFIER:
            response = self.handle_verifier(user_input)
        else:
            response = self.handle_closer(user_input)

        self.history.append({"role": "assistant", "content": response})
        return response, self.stage.value

    def is_irrelevant(self, user_input):
        irrelevant_keywords = ["weather", "joke", "random", "movie", "news", "thank you", "hi", "hello"]
        return not user_input or any(keyword in user_input.lower() for keyword in irrelevant_keywords)

    def handle_irrelevant(self, user_input):
        prompt = (
            f"The caller said: '{user_input}'. Politely redirect them to focus on telecom services or account issues. "
            f"Keep the response short, professional, and sales-oriented, under 20 words."
        )
        return self.llm.generate_response(prompt) or "I appreciate that, but let’s discuss how we can assist with your telecom needs."

    def handle_fronter(self, user_input):
        if not self.user_data["name"]:
            self.user_data["name"] = user_input.split()[-1] or "Customer"
            return self.script[Stage.FRONTER][1].format(name=self.user_data["name"])
        else:
            self.user_data["query"] = user_input
            self.stage = Stage.VERIFIER
            return self.script[Stage.VERIFIER][0].format(name=self.user_data["name"], query=self.user_data["query"])

    def handle_verifier(self, user_input):
        if not self.user_data["account_id"]:
            self.user_data["account_id"] = user_input[:10] if user_input else "unknown"
            return self.script[Stage.VERIFIER][0].format(name=self.user_data["name"], query=self.user_data["query"])
        elif "yes" in user_input.lower() or "correct" in user_input.lower():
            self.user_data["verified"] = True
            self.stage = Stage.CLOSER
            return self.script[Stage.VERIFIER][1].format(name=self.user_data["name"], query=self.user_data["query"])
        else:
            prompt = f"The caller said: '{user_input}'. Clarify their query and ask for confirmation in a sales-oriented way."
            return self.llm.generate_response(prompt)

    def handle_closer(self, user_input):
        resolution = self.get_resolution(user_input)
        return self.script[Stage.CLOSER][0].format(name=self.user_data["name"], query=self.user_data["query"], resolution=resolution)

    def get_resolution(self, user_input):
        prompt = (
            f"You are a CSR for Horizon Telecom. The caller asked: '{user_input}'. Their query is '{self.user_data['query']}'. "
            f"Provide a concise, professional resolution (e.g., billing fix, technical steps, upsell plan). "
            f"Keep it empathetic, sales-focused, under 100 words."
        )
        return self.llm.generate_response(prompt)