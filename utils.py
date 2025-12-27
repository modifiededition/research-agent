import requests
from tools import web_search, arxiv_search, fetch_url
from function_declarations import web_search_dec, fetch_url_dec, arxiv_search_dec
from config import get_config
import os
import json

available_functions = {
  'web_search': web_search,
  'arxiv_search': arxiv_search,
  'fetch_url' : fetch_url,
}

def generate_response(messages, model=None, thinking_level=None, tools = []):
    try:
      config = get_config()
      model = model or config.GEMINI_MODEL
      thinking_level = thinking_level or config.THINKING_LEVEL
      url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={config.GEMINI_API_KEY}"
      headers = {
          "Content-Type": "application/json",
      }

      payload = {
          "contents": messages,
          "generationConfig": {
              "thinkingConfig": {
                  "thinkingLevel": thinking_level
              },
          }
      }

      if tools:
        payload["tools"] = [
              {"functionDeclarations": tools}
          ]

      response = requests.post(url = url, headers = headers, json = payload)
      response.raise_for_status()
      return response.json()
    
    except Exception as e:
      raise Exception(f"Failed to generate response: {str(e)}")

def prepare_message(user_message = "", model_message = "", tool_calls = [], tools_response= []):
    
    if user_message:
       return {"role":"user", "parts":[{"text":user_message}]} 
    elif model_message:
       return {"role":"model", "parts":[{"text":model_message}]}
    elif tool_calls:
       return {"role":"model", "parts":tool_calls}
    elif tools_response:
       return {"role":"user", "parts":tools_response}
    
def extract_content(response):
    try:
        candidate = response["candidates"][0]
        content = candidate["content"]
        parts = content["parts"]

        # check if text is present
        if "text" in parts[0]:
            return parts[0]["text"]
        
        # if text not present, return fn calls
        return parts

    except Exception as e:
        raise Exception(f"Failed to generate response: {str(e)}")

def convert_response_to_json(content):
    try:
        # Handle markdown code blocks
        if isinstance(content, str) and "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()

        # If content is not a string, convert it
        if not isinstance(content, str):
            raise ValueError(f"Expected string content, got {type(content)}")

        # Try to parse JSON
        if not content.strip():
            raise ValueError("Empty content received - cannot parse JSON")

        return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Content received: {content[:200]}...")
        raise Exception(f"Failed to parse JSON response. Content preview: {content[:100]}")
    except Exception as e:
        print(f"Error converting response to JSON: {e}")
        print(f"Content type: {type(content)}, Content: {str(content)[:200]}")
        raise

def generate_response_with_fn_calls(conv_messsages, event_handler=None, max_iterations=None):
    config = get_config()
    max_iterations = max_iterations or config.MAX_TOOL_ITERATIONS
    iteration_count = 0

    while iteration_count < max_iterations:
        iteration_count += 1
        response = generate_response(
            messages=conv_messsages,
            thinking_level="medium",
            tools = [web_search_dec, arxiv_search_dec, fetch_url_dec]
            )

        content = extract_content(response)

        if type(content) == list and content:
            conv_messsages.append(prepare_message(tool_calls = content))
            results = []
            for fn in content:
                fn_call = fn["functionCall"]
                if fn_call["name"] in available_functions:
                    print(f"Calling {fn_call["name"]} with arguments {fn_call["args"]}")
                    fn_result = available_functions[fn_call["name"]](**fn_call["args"])
                    print("Results from fn: ", fn_result[:100])

                    # Emit tool call event if handler provided
                    if event_handler:
                        event_handler.emit_tool_call(
                            fn_call["name"],
                            fn_call["args"],
                            fn_result
                        )

                    # add the tool result to the messages
                    results.append({
                        "functionResponse":{
                            "name": fn_call["name"],
                            "response": {"result":fn_result}
                        }
                    })

            if results:
                conv_messsages.append(prepare_message(tools_response = results))
        else:
            print("\nFinal Message Generated")
            break

    if iteration_count >= max_iterations:
        print(f"\nWarning: Reached maximum tool iterations ({max_iterations})")
        # Force a final response without tools to get the summary
        print("Requesting final summary without additional tool calls...")
        final_response = generate_response(
            messages=conv_messsages,
            thinking_level="medium",
            tools=[]  # No tools - force text response
        )
        content = extract_content(final_response)

    return content