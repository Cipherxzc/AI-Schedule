import json
import os
from typing import List

from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, ToolMessage
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from langchain_core.utils.function_calling import convert_to_openai_tool


template_str = """
Here is my current schedule, given in JSON format:
{schedule}

My requirements are as follows:
{requirements}

Please help me optimize my schedule according to my requirements.
"""

prompt_template = PromptTemplate(
    input_variables=['schedule', 'requirements'],
    template=template_str
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an AI life assistant for a university student. I need you to help me plan my schedule."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])


# load model
with open('schedule_schema.json', 'r') as file:
    schema_json = json.load(file)

# schema_tool = convert_to_openai_tool(schema_json, strict=True)
# tools = {"Schedule": schema_tool}

# llm = AzureChatOpenAI(
#     azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
#     azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
#     openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
#     temperature=0.5,
# )
# structured_llm = llm.with_structured_output(schema_json)

class CustomAzureChatOpenAI(Runnable):
    def __init__(self, azure_endpoint, azure_deployment, openai_api_version, temperature, schema_json):
        self.llm = AzureChatOpenAI(
            azure_endpoint=azure_endpoint,
            azure_deployment=azure_deployment,
            openai_api_version=openai_api_version,
            temperature=temperature,
        )
        self.structured_llm = self.llm.with_structured_output(schema_json, include_raw=False)

    def invoke(self, input, *args, **kwargs):
        output = self.structured_llm.invoke(input, *args, **kwargs)
        output = json.dumps(output, indent=2)

        return AIMessage(content=output)
    
        # output = output['raw']
        # output.content = json.loads(output.additional_kwargs['tool_calls'][0]['function']['arguments'])
        # output.content = json.dumps(output.content, indent=2)

        # messages = [output]
        # tool_calls = output.additional_kwargs.get('tool_calls', [])
        # if tool_calls:
        #     for tool_call in tool_calls:
        #         # print(tool_call)
        #         tool_msg = ToolMessage(role='tool',
        #                                content=structured_llm.last.invoke(output),
        #                                tool_call_id=tool_call['id'],
        #                                name='Schedule')
        #         # print(tool_msg)
        #         messages.append(tool_msg)

        # print(self.structured_llm.invoke(messages))

        # output.additional_kwargs.clear()
        # return output

custom_llm = CustomAzureChatOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    temperature=0.5,
    schema_json=schema_json
)

chain = prompt | custom_llm


# build conversation
class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """In memory implementation of chat message history."""

    messages: List[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        """Add a list of messages to the store"""
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []

store = {}

def get_by_session_id(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryHistory()
    return store[session_id]

conversation = RunnableWithMessageHistory(
    runnable=chain,
    get_session_history=get_by_session_id,
    input_messages_key="question",
    history_messages_key="history",
)


schedule_file = './data/schedule.json'

def generate_schedule(requirements):
    """
    interact with model
    """
    
    # format prompt
    with open(schedule_file, 'r') as file:
        schedule_json = json.load(file)
    schedule_str = json.dumps(schedule_json, indent=2)

    formatted_prompt = prompt_template.format(schedule=schedule_str, requirements=requirements)

    # generate output
    # output = chain.invoke({"schedule": schedule_str, "requirements": requirements})
    output = conversation.invoke({"question": formatted_prompt},
                                 config={"configurable": {"session_id": "foo"}},)

    output = json.loads(output.content)
    # print(store)
    # print('\n')

    with open(schedule_file, 'w') as outfile:
        json.dump(output, outfile, indent=2)

    print(f"Output saved to {schedule_file}")


# requirements = """
# I need to study vocabulary every night from 9 PM to 11 PM.
# """

# generate_schedule(requirements)

def main():
    while True:
        requirements = input("Enter your requirements (or type 'exit' to quit): \n")
        if requirements.lower() == 'exit':
            break

        generate_schedule(requirements)

if __name__ == "__main__":
    main()