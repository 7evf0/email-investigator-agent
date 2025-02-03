from smolagents import Tool
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from smolagents import OpenAIServerModel, tool
import json  # Import JSON for structured responses

from tools.chart_creator import barchart_generator
from test import run_llm

llm = OpenAIServerModel(temperature=0.3, model_id="gpt-4o-mini")

class RetrieverTool(Tool):
    name = "retriever"
    description = "Uses semantic search to retrieve the parts of the documentation that could be most relevant to answer your query."
    inputs = {
        "query": {
        "type": "string",
        "description": "The query to perform. This should be semantically close to your target documents. Use the affirmative form rather than a question.",
        }
    }
    output_type = "string"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self.vector_db = FAISS.load_local("vector_storage", OpenAIEmbeddings(), allow_dangerous_deserialization=True)
        except Exception:
            print("FAISS index not found. Creating a new one...")
            self.vector_db = FAISS.from_documents([], OpenAIEmbeddings())

    def forward(self, query: str) -> str:
        assert isinstance(query, str), "Your search query must be a string"
        docs = self.vector_db.similarity_search(query, k=50)

        # Return a structured JSON object
        return {
            "retrieved_docs": [
                {"doc_id": i, "content": doc.page_content}
                for i, doc in enumerate(docs)
            ]
        }

retriever_tool = RetrieverTool()

from smolagents import CodeAgent
import json

@tool
def process_json_string(input_string: str) -> object:
    """
        Processes the output result and turns it into valid JSON format.

        Args:
            input_string: Output coming from the model that needs to be turned into a valid JSON instance.
    """
    # Check if the input starts with '''json and ends with '''
    if input_string.startswith("```json") and input_string.endswith("```"):
        # Remove the '''json prefix and ''' suffix
        trimmed_string = input_string[7:-3]  # Remove first 7 characters and last 3 characters
        # Load the resulting string into a JSON object
        try:
            json_object = json.loads(trimmed_string)
            return json_object
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)
            return None
    else:
        return json.loads(input_string)

# Define the agent
agent = CodeAgent(
    tools=[barchart_generator], model=llm, additional_authorized_imports=['itertools', 'queue', 'statistics', 'unicodedata',
'collections', 'math', 'time', 'stat', 're', 'datetime', 'random'], max_steps=6
)

def run_agent(prompt: str, chat_history: list[dict[str, str]]) -> dict:

    json_format = { 
        "query": "string",
        "result": "string",
        "source_documents": "object",
        "bar_chart_object": "object (e.g., bar chart data or empty object)"
    }

    response = agent.run(f"""
        You are a reasoning agent trying to clarify how to approach the given query and find the final descriptive result with the retrieved emails.

        You will be generating chain of thought steps with the objective of generating a concise, suitable, and interpretable response. Each step should clearly indicate:
        1. What specific action is being performed (e.g., filtering emails, retrieving metadata).
        2. How the action contributes to solving the query (e.g., counting all retrieved emails, matching specific criteria).
        3. The result of the step (include in a 'Result' field for every step).

        Ensure the steps are detailed enough to explain how the final result was achieved, specifically for queries involving document operations, metadata, or counting.

        Steps should include:
        1- Beginning analysis
        2- Creating a plan
        3- Wrapping up the analysis
        4- Parsing the final output in the correct structure.
                         
        You **must** do the following steps in your chain-of-thought:
        1. Call the 'retriever_tool' using the exact format: retriever(query="{{prompt}}").
        2. Analyze the extracted documents to form both the reasoning chain and final answer.

        Return the final output in JSON format, which should be starting with {{ and finishing with }} and cannot start with '''json at any cost with:
        - A 'chain' field containing a list of steps (each step as {{step: string, result: string}}).
        - A 'result' field with descriptive and coherent response explaining the final result. Keep this field as much informative as possible. Do not directly put JSON data here, generate a easy-to-look template.

        Here is the query: {prompt}
        """)
    
    if isinstance(response, dict):  # Check if the response is already a dictionary
        return response  # Return as-is
    
    try:
        return json.loads(response)  # Convert response into JSON if it's a string
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response from agent"}
    
def run_chart_agent(query: str, response: str) -> dict:

    outputs = { 
        "query": {
            "type": "string",
            "description": "Return the input prompt itself"
        },
        "result": {
            "type": "boolean",
            "description": "Return whether the prompt was suitable for bar chart generation for data analysis. Return only 'True' or 'False'"
        },
        "bar_chart_object": {
            "type": "object",
            "description": "Return the required bar chart data if the prompt implies for bar chart generation. If not, leave the field as an empty object."
        }
    }

    """Runs the agent and returns a structured response."""
    response = agent.run(f"""
                         You are a decision maker agent, deciding whether the given reasoning steps require a bar chart for data analysis visualization.
                         Look for keywords in the query such as 'plot', 'categorize' and 'count' to continue making bar chart.
                         Never assume any values for the keys. If no specific values for the keys have been provided by the response, do not generate the chart.
                         If bar chart generation is considered required for the provided prompt,use 'barchart_generator' tool to obtain required fields for the bar chart.
                         Always use the 'response' input for bar chart data generation, which is '{response}'.

                         Return an output JSON object based on the given prompt: {query}.
                         Output JSON format has the form of {json.dumps(outputs)}.""")
    
    if isinstance(response, dict):  # Check if the response is already a dictionary
        return response  # Return as-is
    
    try:
        return json.loads(response)  # Convert response into JSON if it's a string
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response from agent"}
    

