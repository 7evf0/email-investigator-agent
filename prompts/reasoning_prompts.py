def formatted_reasoning_query(query: str):
    return f"""
        You are a reasoning agent trying to clarify how to approach the given query.

        You will be generating chain of thought steps with the objective of generating a concise, suitable, and interpretable response. Each step should clearly indicate:
        1. What specific action is being performed (e.g., filtering documents, retrieving metadata).
        2. How the action contributes to solving the query (e.g., counting all retrieved documents, matching specific criteria).
        3. The result of the step (include in a 'Result' field for every step).

        Ensure the steps are detailed enough to explain how the final result was achieved, specifically for queries involving document operations, metadata, or counting.

        Steps should include:
        1- Beginning analysis
        2- Creating a plan
        3- Wrapping up the analysis
        4- Parsing the final output in the correct structure.

        Return the final output in JSON format, which should be starting with {{ and finishing with }} and cannot start with '''json at any cost with:
        - A 'chain' field containing a list of steps (each step as {{step: string, result: string}}).
        - A 'result' field with a user-friendly and descriptive response explaining the final result. Keep this field as much informative as possible. The user will understand the final result looking only through here.

        Here is the query: {query}
    """

def formatted_query(query: str):
    return f"""
        You are a reasoning agent trying to clarify how to approach the given query.

        You will be generating chain of thoughts steps with the objective of generating a concise, suitable and interpretable response.
        Specifically include reasoning step numbers and focus on approaching the problem specifically step by step.
        Each step should be specifically focused on the query problem itself. Do not generate generic steps (e.g. Identify the relevant information from the provided context)
        Each step should include it's own result field named as 'Result' in all steps, which will be the direct application of the step's instruction.


        Return the final output in JSON format, as the generated steps are inserted into JSON list in order within 'chain' field.
        Also add a 'result' field to the output, which will generate a user-friendly and descriptive response of the final result.
        The format is: {{chain: [{{step: string, result: string}}...], result: string}}

        Steps should include:
        1- Beginning analysis
        2- Creating a plan
        3- Wrapping up the analysis
        4- Parsing the final output in the correct structure.

        Here is the query that you need to find a concise, suitable and interpretable response with multi-step reasoning: {query}
    """