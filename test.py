import json
import os
from langchain_openai import AzureChatOpenAI

with open('schedule_schema.json', 'r') as file:
    json_schema = json.load(file)

llm = AzureChatOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    temperature=0.5,
)
structured_llm = llm.with_structured_output(json_schema)

output = structured_llm.invoke("Help me design a schedule as a university student")

with open('schedule.json', 'w') as outfile:
    json.dump(output, outfile, indent=4)

print("Output saved to schedule.json")
