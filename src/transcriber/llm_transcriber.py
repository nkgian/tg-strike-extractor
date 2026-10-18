import json
import time

from openai import OpenAI

from src.settings import LOCAL_LLM_API_KEY, LOCAL_LLM_BASE_URL, LOCAL_LLM_MODEL


def extract_location_from_post(post_text, instruction_prompt, model_name=None):
    """
    Extracts the location from a social media post using a local model served
    through an OpenAI-compatible API (e.g. LM Studio, llama.cpp server, vLLM).

    Args:
        post_text (str): The raw text of the social media post.
        instruction_prompt (str): The instruction prompt to guide the model.
        model_name (str): The model identifier (default: LOCAL_LLM_MODEL env var).

    Returns:
        dict: The extracted location or error message.
    """
    model_name = model_name or LOCAL_LLM_MODEL
    client = OpenAI(base_url=LOCAL_LLM_BASE_URL, api_key=LOCAL_LLM_API_KEY)

    start_time = time.perf_counter()
    try:
        response = client.chat.completions.create(
            model=model_name,
            response_format={"type": "json_object"},
            messages=[
                {'role': 'system', 'content': instruction_prompt},
                {'role': 'user', 'content': post_text},
            ]
        )
    except Exception as e:
        return {"error": f"Local LLM request failed: {str(e)}"}

    duration = time.perf_counter() - start_time
    message = response.choices[0].message
    content = message.content or ""

    try:
        content_data = json.loads(content)
    except json.JSONDecodeError:
        return {"error": "Model did not return valid JSON in the 'content' field", "raw": content}

    final_output = {
        "final_answer": content_data.get('location', "Not Found"),
        "thinking": getattr(message, "reasoning_content", None) or "Reasoning field not found in message payload.",
        "model_name": response.model or model_name,
        "time_taken_seconds": round(duration, 3)
    }

    return final_output


def extract_location_local_prompt(post_text, model_name=None):
    """
    Sends a social media post to a local OpenAI-compatible model server to
    extract location data. Uses a local prompt.txt file to instruct the model.

    Args:
        post_text (str): The raw text of the social media post.
        model_name (str): The model identifier (default: LOCAL_LLM_MODEL env var).

    Returns:
        dict: The extracted location or error message.
    """
    try:
        with open('prompt.txt', 'r') as f:
            local_prompt = f.read()
    except Exception as e:
        return {"error": f"Error loading prompt.txt. Make sure it exists in the same dir.: {str(e)}"}

    return extract_location_from_post(post_text, local_prompt, model_name)

# debug
if __name__ == "__main__":
    demo_post = "Can't believe the coffee here at The Grind in Shoreditch. Best way to start a rainy Tuesday in London! #coffee #uk"

    result_data = extract_location_local_prompt(demo_post)

    print("-" * 30)
    print(json.dumps(result_data, indent=4))
