from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from app.agents.email_tool import send_email

llm = ChatOpenAI(temperature=0)
tools = [send_email]

email_agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)