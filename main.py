# Note: Replace **<YOUR_APPLICATION_TOKEN>** with your actual Application token

import argparse
import json
from argparse import RawTextHelpFormatter
import requests
from typing import Optional
import warnings
from bs4 import BeautifulSoup
import requests
try:
    from langflow.load import upload_file
except ImportError:
    warnings.warn("Langflow provides a function to help you upload files to the flow. Please install langflow to use it.")
    upload_file = None

BASE_API_URL = "http://127.0.0.1:7860"
FLOW_ID = "c3f6f3a1-a8ee-482e-b448-dc391d0dab55"
APPLICATION_TOKEN = "AstraCS:JPTsXyZmiRFtkOZnRUfvzoMD:1b07f3835fd45d89c598f4fab4ffe4f44c3e2bd6289cda5ab050524d5428b86f"
ENDPOINT = "" # You can set a specific endpoint name in the flow settings

# You can tweak the flow by adding a tweaks dictionary
# e.g {"OpenAI-XXXXX": {"model_name": "gpt-4"}}
TWEAKS = {
    "URL-ZMyq6": {"urls": ["avsystem.com", "https://avsystem.com/contact/"]},
    "ParseData-LXOQx": {"sep": "\n", "template": "{text}"},
    "Prompt-D3unq": {
        "instructions": "",
        "references": "",
        "template": "Below you have plain text of the website, do following: {instructions}\n\n---\n\n{references}\n\n\n\n\n",
    },
    "TextInput-uJJNh": {
        "input_value": "Find NIP, KRS and contact details, if any of them is not available, write it\n"
    },
    "ChatOutput-q4hC7": {
        "data_template": "{text}",
        "input_value": "",
        "sender": "Machine",
        "sender_name": "AI",
        "session_id": "",
        "should_store_message": True,
    },
    "OpenAIModel-eOzop": {
        "input_value": "",
        "json_mode": False,
        "max_tokens": None,
        "model_kwargs": {},
        "model_name": "gpt-4o-mini",
        "openai_api_base": "",
        "output_schema": {},
        "seed": 1,
        "stream": False,
        "system_message": "",
        "temperature": 0.1,
    },
}
from urllib.parse import urlparse
def myFunc(e):
    return len(e)
def extract_urls(url: str) -> list:
    """
    Extracts the URLs from a given URL.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    urls = list(set([a['href'].split("?")[0] for a in soup.find_all('a', href=True)]))
   
    urls.sort(key=myFunc)
    print(urls)
    # Filter out duplicates and empty URLs
    out = ""
    domain = urlparse(url).netloc
    
    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = True
    text_maker.ignore_images = True
    text_maker.ignore_emphasis = True
    text_maker.ignore_tables = True
    count = 14
    prepare = set()
    for i in urls:
        o = urlparse(i)
        if "." in o.path:
          print("skipping: ", i)
          continue
        
        if o.netloc == domain or o.netloc == "":

            test = "https://" + domain + o.path.rstrip("/")
            if urlparse(test).netloc == domain:
              prepare.add(test)
              
    prepare = list(prepare)
    prepare.sort(key=myFunc)
    for i in prepare:
      
        response = requests.get(i)
        print(i)
        
        out += text_maker.handle(response.text)
        count -= 1
        if count == 0 or len(out) > 25000:
          break
        
    out = (out[:25000] + '...') if len(out) > 25000 else out
    return out

def run_flow(message: str,
  endpoint: str,
  output_type: str = "chat",
  input_type: str = "chat",
  tweaks: Optional[dict] = None,
  application_token: Optional[str] = None) -> dict:
    """
    Run a flow with a given message and optional tweaks.

    :param message: The message to send to the flow
    :param endpoint: The ID or the endpoint name of the flow
    :param tweaks: Optional tweaks to customize the flow
    :return: The JSON response from the flow
    """
    api_url = f"{BASE_API_URL}/api/v1/run/{endpoint}"

    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    headers = None
    if tweaks:
        payload["tweaks"] = tweaks
    if application_token:
        headers = {"Authorization": "Bearer " + application_token, "Content-Type": "application/json"}
    response = requests.post(api_url, json=payload, headers=headers, timeout=30)
    return response.json()

def main(url, offer):
    global TWEAKS
    parser = argparse.ArgumentParser(description="""Run a flow with a given message and optional tweaks.
Run it like: python <your file>.py "your message here" --endpoint "your_endpoint" --tweaks '{"key": "value"}'""",
        formatter_class=RawTextHelpFormatter)
    parser.add_argument("message", type=str, help="The message to send to the flow")
    parser.add_argument("--endpoint", type=str, default=ENDPOINT or FLOW_ID, help="The ID or the endpoint name of the flow")
    # parser.add_argument("--tweaks", type=str, help="JSON string representing the tweaks to customize the flow", default=json.dumps(TWEAKS))
    parser.add_argument("--output_type", type=str, default="chat", help="The output type")
    parser.add_argument("--input_type", type=str, default="chat", help="The input type")
    parser.add_argument("--upload_file", type=str, help="Path to the file to upload", default=None)
    parser.add_argument("--components", type=str, help="Components to upload the file to", default=None)

    args = parser.parse_args()
    tweaks = {
      "TextInput-QcBYK": {
        "input_value": extract_urls(url)
      },
      "TextInput-tdaHM": {
        "input_value": offer
      }
    }
    # print(tweaks)

    if args.upload_file:
        if not upload_file:
            raise ImportError("Langflow is not installed. Please install it to use the upload_file function.")
        elif not args.components:
            raise ValueError("You need to provide the components to upload the file to.")
        tweaks = upload_file(file_path=args.upload_file, host=BASE_API_URL, flow_id=ENDPOINT, components=args.components, tweaks=tweaks)

    response = run_flow(
        message=args.message,
        endpoint=args.endpoint,
        output_type=args.output_type,
        input_type=args.input_type,
        tweaks=tweaks
    )
    # print(response)
    return response["outputs"][0]["outputs"][0]["results"]["message"]["data"]["text"]


import html2text
from flask import Flask, request, jsonify
from flask_cors import CORS
import markdown
if __name__ == "__main__":
    # urls = extract_urls("https://hacod.tech/")
    # for url in urls:
    #     print(url)
    # main()

    app = Flask(__name__)
    CORS(app)

    @app.route('/run_flow', methods=['POST'])
    def run_flow_endpoint():
      data = request.json
      message = data.get('message')
      
      response = markdown.markdown(main(message, data.get('offer')))
      return jsonify(response)

    if __name__ == "__main__":
      app.run(host='0.0.0.0', port=5000)
