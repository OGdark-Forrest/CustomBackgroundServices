from openai import AzureOpenAI
import os

endpoint = "https://asasa.openai.azure.com/"
model_name = "gpt-5.4"
deployment = "gpt-5.4"

subscription_key = os.getenv("AZURE_OPENAI")
api_version = "2025-03-01-preview"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

def get_content(prompt: str):
    response = client.responses.create(
        model=deployment,
        input=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        tools=[
            {
                "type": "web_search"
            }
        ],
        max_output_tokens=16384
    )

    return response.output_text