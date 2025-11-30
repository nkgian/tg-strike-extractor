import ollama
import json
import os

def extract_location_from_post(post_text, instruction_prompt, model_name="gpt-oss:20b"):
    """
    Extracts the location from a social media post using a local Ollama model.    
    
    Args:
        post_text (str): The raw text of the social media post.
        instruction_prompt (str): The instruction prompt to guide the model.
        model_name (str): The model tag (default: gpt-oss:20b).
        
    Returns:
        dict: The extracted location or error message.
    """
    try:
        response = ollama.chat(
            model=model_name,
            format='json', 
            messages=[
                {'role': 'system', 'content': instruction_prompt},
                {'role': 'user', 'content': post_text},
            ]
        )
        
        message_data = response['message']        
        content_data = json.loads(message_data['content'])
        model_thinking = message_data.get('thinking', "Reasoning field not found in message payload.")
        duration = response.get('total_duration', 0) / 1e9

        final_output = {
            "final_answer": content_data.get('location', "Not Found"),
            # NOTE!: Thinking is not extracted from JSON
            "thinking": model_thinking, 
            "model_name": response.get('model', model_name),
            "time_taken_seconds": round(duration, 3)
        }
        
        return final_output
        
    except json.JSONDecodeError:
        return {"error": "Model did not return valid JSON in the 'content' field", "raw": response['message']['content']}
    except Exception as e:
        return {"error": f"Ollama Error: {str(e)}", "raw_response_keys": list(response['message'].keys())}


def extract_location_local_prompt(post_text, model_name="gpt-oss:20b"):
    """
    Sends a social media post to a local Ollama model to extract location data. Uses
    a local prompt.txt file to instruct the model.    
    
    Args:
        post_text (str): The raw text of the social media post.
        model_name (str): The model tag (e.g., 'llama3.2', 'gpt-oss:20b' <- default).
        
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

    result_data = extract_location_local_prompt(demo_post, model_name="gpt-oss:20b") 
    
    print("-" * 30)
    print(json.dumps(result_data, indent=4))