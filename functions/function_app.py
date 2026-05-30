import azure.functions as func
import logging
import json
import os
from openai import AzureOpenAI

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

openai_client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_KEY"],
    api_version="2024-02-01"
)

@app.route(route="summarize", methods=["POST"])
def summarize_document(req: func.HttpRequest) -> func.HttpResponse:
    body = req.get_json()
    text = body.get("text", "")
    if not text:
        return func.HttpResponse("Missing 'text' field", status_code=400)
    
    response = openai_client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "Summarize the following text in 3 bullet points."},
            {"role": "user", "content": text}
        ]
    )
    summary = response.choices[0].message.content
    return func.HttpResponse(json.dumps({"summary": summary}), mimetype="application/json")

