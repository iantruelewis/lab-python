# Ai Agent
# 1. Setup requirements
# 2. Imports + basic code set up
# 3. Import API key
# 4. LLM functionality
# 5. Structured output
# 6. Prompt template(s)
# 7. Create agent'
# 8. Output parsing
# 9. Call prebuilt tools
# 10. Call custom tools

# imports from .env
from dotenv import load_dotenv
from pydantic import BaseModel
# llm models
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
# imports chat/prompt framework
from langchain_core.prompts import ChatMessagePromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
# creates agent
from langchain.agents import create_tool_calling_agent, AgentExecutor
# imports search tool
from tools import search_tool, wiki_tool, save_tool

load_dotenv()
# defines Python class that will specify type of content LLM generates
class ResearchResponse(BaseModel):
    # defines output from LLM as topic, summary, sources, and tools used
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]

# llm2 = ChatOpenAI(model="gpt-4o-mini") # placeholder model
llm = ChatAnthropic(model="claude-3-5-sonnet") # placeholder model
parser = PydanticOutputParser(pydantic_object=ResearchResponse)

# agent instructions and guidelines
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a research assistant that will help generate a research paper.
            Answer the user query and use necessary tools.
            Wrap the output in this format and provide no other text\n{format_instructions}
            """
        )
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

# calls agent and tools
tools = [search_tool, wiki_tool, save_tool]
agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt,
    tools=tools,
)

# directs agent to show thought process, calls reponse
agent_executor = AgentExecutor(agent=agent, tools=[], verbose=True)
query = input("What can I help you research?") # prompts user with question to task agent
raw_response = agent_executor.invoke({"query": query}) # allows user to provide prompt to agent

# calls structured response through parser, tests output run
try:
    structured_response = parser.parse(raw_response.get("output")[0]["text"])
    print(structured_response)
except Exception as e:
    print("Error parsing response", e, "Raw Response - ", raw_response)