
from typing import List, Tuple, Dict, Any
from groq import Groq
import google.generativeai as genai

from schemas.general_schemas import LLMAPIManager






class GeminiLLMAPIManager(LLMAPIManager):
    """
    Manager for interacting with Google Gemini LLM API via the official
    `google-generativeai` client, mirroring the Groq manager's interface.

    Adds support for specifying the model name at initialization and helpers for
    sending a single message, multiple messages, or a raw prompt.
    """

    def __init__(self, api_key: str, model_name: str) -> None:
        """
        Args:
            api_key: Your Google Generative AI API key.
            model_name: The model identifier, e.g. "gemini-1.5-pro".
        """
        genai.configure(api_key=api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)

    def validate(self) -> bool:
        """
        Validate that the API key and model name are correct.

        Returns:
            True if valid, False otherwise.
        """
        try:
            # Attempt a trivial generation to validate credentials and model
            self.send_message({"role": "system", "content": "Test message to validate API key."})
            return True
        except Exception as e:
            print(f"Validation failed: {e}")
            return False

    def _messages_to_gemini_input(self, messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Convert a list of {role, content} dicts into Gemini input parts.
        Gemini supports role annotations, but for simplicity we pass the content
        as sequential parts preserving roles.
        """
        parts: List[Dict[str, Any]] = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            # Represent each message as a dict with role and text.
            parts.append({"role": role, "parts": [content]})
        return parts

    def send_message(self, message: Dict[str, str]) -> Dict[str, Any]:
        """
        Send a single chat message to Gemini API and return the raw response.

        Args:
            message: Dict with 'role' and 'content'.
        Returns:
            The API response as a dict-like object where applicable.
        """
        # Use a non-streaming generate_content call for simplicity.
        result = self.model.generate_content(message.get("content", ""))
        return result

    def send_messages(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Send chat messages to Gemini API and return the raw response.

        Args:
            messages: List of dicts with 'role' and 'content'.
        Returns:
            The API response as a dict-like object where applicable.
        """
        # Convert messages to a multi-turn chat input
        contents = self._messages_to_gemini_input(messages)
        result = self.model.generate_content(contents)
        return result

    def send_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Send a single prompt to Gemini API and return the text output.

        Args:
            prompt: The text prompt to send.
        Returns:
            The text output string if available, otherwise a fallback message.
        """
        result = self.model.generate_content(prompt)
        try:
            # Prefer the consolidated text helper when available
            text = getattr(result, "text", None)
            if callable(text):
                text = result.text
            if isinstance(text, str) and text.strip():
                return text
            # Fallback to candidates structure
            candidates = getattr(result, "candidates", None) or []
            for c in candidates:
                parts = (
                    (c.get("content") or {}).get("parts")
                    if isinstance(c, dict)
                    else getattr(getattr(c, "content", None), "parts", None)
                )
                if parts:
                    # Take first textual part
                    first = parts[0]
                    if isinstance(first, dict) and "text" in first:
                        return first["text"]
                    if isinstance(first, str):
                        return first
        except Exception:
            pass
        return "No response received"

