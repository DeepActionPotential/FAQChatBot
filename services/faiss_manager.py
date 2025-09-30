import faiss
import logging
import pickle
from sentence_transformers import SentenceTransformer
from typing import List, Tuple
import numpy as np

from schemas.general_schemas import VectorDatabase


class FaissVectorDatabase(VectorDatabase):
    def __init__(self, model_name: str, logger: logging.Logger) -> None:
        """
        Initializes the manager with the given model name.

        Args:
            model_name: str
                The name of the sentence transformer model to use.
            logger: logging.Logger
                The logger instance used for logging.
        """
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.get_sentence_embedding_dimension()
        # Use inner product index for efficient dot-product similarity
        self.index = faiss.IndexFlatIP(self.dim)
        self.logger = logger
        # Store texts for mapping indices to original content
        self.texts: List[str] = []
        self.logger.info(f"Initialized FaissIndexManager with model '{model_name}' and dimension {self.dim}.")

    def embed_texts(self, texts: List[str], normalize: bool = True) -> np.ndarray:
        """
        Embeds a list of texts into vectors.

        Args:
            texts: List[str] - list of strings to embed
            normalize: bool - whether to L2-normalize embeddings

        Returns:
            np.ndarray of shape (len(texts), dim)
        """
        self.logger.debug(f"Embedding {len(texts)} texts.")
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        if normalize:
            faiss.normalize_L2(embeddings)
        return embeddings

    def add_text(self, text: str) -> None:
        """
        Embeds and adds a single text to the FAISS index.

        Args:
            text: str - the text to add
        """
        self.logger.debug(f"Adding single text to index: {text}")
        vec = self.embed_texts([text])
        self.index.add(vec)
        self.texts.append(text)
        self.logger.info(f"Added text to index. Total size: {self.index.ntotal} vectors.")

    def add_texts(self, texts: List[str]) -> None:
        """
        Embeds and adds multiple texts to the FAISS index.

        Args:
            texts: List[str] - texts to add
        """
        self.logger.debug(f"Adding {len(texts)} texts to index.")
        vecs = self.embed_texts(texts)
        self.index.add(vecs)
        self.texts.extend(texts)
        self.logger.info(f"Added {len(texts)} texts. Total size: {self.index.ntotal} vectors.")

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Searches the FAISS index for the top_k nearest neighbors to the query,
        returning cosine similarity scores.

        Args:
            query: str - the search query text
            top_k: int - number of nearest neighbors to return

        Returns:
            List of tuples (text, similarity)
        """
        self.logger.debug(f"Searching for top {top_k} results for query: {query}")
        q_vec = self.embed_texts([query])
        # For IP index, higher is more similar
        similarities, indices = self.index.search(q_vec, top_k)

        results: List[Tuple[str, float]] = []
        for sim, idx in zip(similarities[0], indices[0]):
            if idx < len(self.texts) and idx >= 0:
                results.append((self.texts[idx], float(sim)))
        self.logger.info(f"Search returned {len(results)} results.")
        return results

    def clear_index(self) -> None:
        """
        Clears the FAISS index and stored texts.
        """
        self.index = faiss.IndexFlatIP(self.dim)
        self.texts = []
        self.logger.info("Cleared FAISS index and text store.")

    def save_index(self, index_path: str, metadata_path: str) -> None:
        """
        Saves the FAISS index and associated text metadata.

        Args:
            index_path: str - file path to save the FAISS index
            metadata_path: str - file path to save the texts metadata
        """
        self.logger.debug(f"Saving FAISS index to {index_path} and metadata to {metadata_path}.")
        faiss.write_index(self.index, index_path)
        with open(index_path, 'wb') as f:
            pickle.dump(self.texts, f)
        self.logger.info("Index and metadata saved successfully.")

    def load_index(self, index_path: str, metadata_path: str) -> None:
        """
        Loads the FAISS index and associated text metadata.

        Args:
            index_path: str - file path to load the FAISS index from
            metadata_path: str - file path to load the texts metadata from
        """
        self.logger.debug(f"Loading FAISS index from {index_path} and metadata from {metadata_path}.")
        self.index = faiss.read_index(index_path)
        with open(metadata_path, 'rb') as f:
            self.texts = pickle.load(f)
        self.logger.info(f"Index and metadata loaded. Total vectors: {self.index.ntotal}.")