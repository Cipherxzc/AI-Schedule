from typing import Optional
import os
import json

from langchain_openai import AzureChatOpenAI

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from operator import itemgetter
from typing import List

from langchain_openai.chat_models import ChatOpenAI

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field
from langchain_core.runnables import (
    RunnableLambda,
    ConfigurableFieldSpec,
    RunnablePassthrough,
    Runnable
)
from langchain_core.runnables.history import RunnableWithMessageHistory


class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """In memory implementation of chat message history."""

    messages: List[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        """Add a list of messages to the store"""
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []

# Here we use a global variable to store the chat message history.
# This will make it easier to inspect it to see the underlying results.
store = {}

def get_by_session_id(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryHistory()
    return store[session_id]


prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an AI life assistant for a university student. I need you to help me plan my schedule."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])

with open('schedule_schema.json', 'r') as file:
    schema_json = json.load(file)

llm = AzureChatOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    temperature=0.5,
)
structured_llm = llm.with_structured_output(schema_json)

class CustomAzureChatOpenAI(Runnable):
    def __init__(self, azure_endpoint, azure_deployment, openai_api_version, temperature, schema_json):
        self.llm = AzureChatOpenAI(
            azure_endpoint=azure_endpoint,
            azure_deployment=azure_deployment,
            openai_api_version=openai_api_version,
            temperature=temperature,
        )
        self.structured_llm = self.llm.with_structured_output(schema_json, include_raw=True)

    def invoke(self, *args, **kwargs):
        output = self.structured_llm.invoke(*args, **kwargs)
        return output['raw']

custom_llm = CustomAzureChatOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    temperature=0.5,
    schema_json=schema_json
)

chain = prompt | llm

chain_with_history = RunnableWithMessageHistory(
    chain,
    # Uses the get_by_session_id function defined in the example
    # above.
    get_by_session_id,
    input_messages_key="question",
    history_messages_key="history",
)

output = chain_with_history.invoke(  # noqa: T201
    {"question": "I need to study vocabulary every night from 9 PM to 11 PM."},
    config={"configurable": {"session_id": "foo"}}
)

print(output)

# Uses the store defined in the example above.
# print(store)  # noqa: T201

output = chain_with_history.invoke(  # noqa: T201
    {"ability": "math", "question": "What's its inverse"},
    config={"configurable": {"session_id": "foo"}}
)

print(output)
# print(store)  # noqa: T201