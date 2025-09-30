
from dataclasses import dataclass
from typing import List, Dict, Any




@dataclass
class GeneralCfg:

    """
    GeneralCfg is a dataclass that holds configuration parameters for the chatbot application.
    Attributes:
    text_embedding_model_name (str): Name of the text embedding model to use. Default is "all-MiniLM-L6-v2".
    llm_api_model_name (str): Name of the LLM API model to use. Default is "llama-3.3-70b-versatile".
    n_char (int): Number of characters to process in each chunk. Default is 1000.
    overlap (int): Number of overlapping characters between chunks. Default is 200.
    top_k (int): Number of top results to retrieve. Default is 10.
    n_answers (int): Number of answers to return. (Value not set in the code snippet.)
    """

    text_embedding_model_name: str = "all-MiniLM-L6-v2"
    llm_api_model_name: str = "gemini-2.0-flash"

    n_char = 1000
    overlap = 200
    top_k = 10
    n_answers = 3







@dataclass
class LLMPrompts:

    FAQ_answer_prompt = """


You are an intelligent assistant whose sole responsibility is to answer user queries strictly using information retrieved from a company-provided vector database. Do NOT generate any answers from your training data or prior knowledge. Only use the results explicitly retrieved and supplied in the variable search_results.

Your task:
- Use Retrieval-Augmented Generation (RAG) to find and present the most relevant questions and answers related to the user query.
- Return your response in **valid JSON format**, structured as a list of Q&A objects sorted by relevance.
- Each Q&A object should include:
  - "question": the closely matching question from the database
  - "answer": the corresponding answer
  - "score" (optional): a confidence or similarity score if available

Input:
- User Question: `{question}`
- Retrieved Results: `{search_results}` (This is the ONLY source of truth)

Instructions:
- RETURN a normal response if the USER QUESTION is not a question, the normal response should NOT be json, it should be a normal text, like (hello -> Hi, how I can help you today) and so on.
- chekc the prompt question provided, if its a normal question that does not relate to the Retrieved restults, you should reply normally.
- Do NOT fabricate or hallucinate answers.
- DO NOT WRITE any introductory messages.
- DO NOT WRITE any closing messages.
- Do NOT WRITE Duplicated answers.
- If the search_results is empty, return this message "No databse provided, please add database first"
- Filter out duplicated answers.
- Remove the question or answer order or number if there is a one.
- If the database does not contain relevant results, return an empty JSON array `[

(
    "question": the non-relevant question,
    "answer": "The bot ca not find a relavent answer in the database",
    "score": 0.0
  )

]`.
- Ensure that all output is properly escaped and parseable JSON.
- Return at most {n_answers} answers, even if more are available in search_results.
- Do NOT fabricate or hallucinate answers.



Example Output:
[
  (
    "question": "How do I track my Amazon package?",
    "answer": "Visit “Your Orders” and click “Track package” to see delivery status.",
    "score": 0.94
  ),
  (
    "question": "What if my package shows delivered but I can’t find it?",
    "answer": "Check delivery driver’s photo note, wait a bit, then contact Amazon support.",
    "score": 0.91
  )
]




"""