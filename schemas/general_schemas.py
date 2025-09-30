import faiss
import numpy as np
from typing import List, Optional, Tuple, Callable, Dict, Any
from abc import ABC, abstractmethod

class VectorDatabase(ABC):
    """
    Abstract base class for vector databases.
    """
    @abstractmethod
    def embed_texts(self, samples: List) -> np.ndarray:
        """
        Convert raw samples into embedding vectors.
        """
        pass

    @abstractmethod
    def add_text(self, samples: List, ids: Optional[List[int]] = None) -> None:
        """
        Embed and add sample to the database.
        """
        pass

    @abstractmethod
    def add_texts(self, samples: List, ids: Optional[List[int]] = None) -> None:
        """
        Embed and add samples to the database.
        """
        pass

    @abstractmethod
    def save_index(self, path: str) -> None:
        """
        Save the database index to disk.
        """
        pass

    @abstractmethod
    def load_index(self, path: str) -> None:
        """
        Load the database index from disk.
        """
        pass

    @abstractmethod
    def clear_index(self) -> None:
        """
        Clear the database index.
        """
        pass

    @abstractmethod
    def search(self, query_samples: List, top_k: int = 5) -> List[List[Tuple[int, float]]]:
        """
        Search for nearest neighbors of embedded query samples.

        Returns similarity percentages.
        """
        pass




class LLMAPIManager(ABC):
    """
    Abstract base class for LLM API managers.
    Defines interface for validating credentials and sending messages.
    """
    @abstractmethod
    def validate(self) -> bool:
        """
        Validate that the API key or credentials are correct.
        Returns True if valid, False otherwise.
        """
        pass

    @abstractmethod
    def send_message(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Send a list of message dicts (with 'role' and 'content') to the LLM API.
        Returns the parsed JSON response.
        """
        pass

    @abstractmethod
    def send_messages(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Send a list of message dicts (with 'role' and 'content') to the LLM API.
        Returns the parsed JSON response.
        """
        pass

    @abstractmethod
    def send_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Send a single prompt string to the LLM API.
        Returns the parsed JSON response.
        """
        pass




class TextEmbedder(ABC):
    """
    Abstract base class for text embedders.
    """
    @abstractmethod
    def embed(self, texts: List[str]) -> np.ndarray:
        """
        Convert a list of text strings into a 2D numpy array of embeddings.

        Returns:
            np.ndarray of shape (n_texts, dim).
        """
        pass