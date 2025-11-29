from .schema.tool import ToolList
import os


from agno.agent import Agent
from agno.models.openai import OpenAILike
from .kb import load_kb

model = OpenAILike(
    id=os.getenv("MODEL"),
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"),
)


def rag_agent(task, software="scmcp"):
    knowledge_base = load_kb(software=software)
    agent = Agent(
        model=model,
        knowledge=knowledge_base,
        show_tool_calls=True,
        search_knowledge=True,
        instructions="""
        MUST query the knowledge base, and return the code example that can be used to solve the task.
        Query the knowledge base to provide several complete code snippets/guides for input TASK resolution. The return format should be
        <code_example>
            <demo1>
                [code_example1]
            </demo1>
            <demo2>
                [code_example2]
            </demo2>
            ...
        </code_example>
        
        if there are multiple code examples, you should score them based on the relevance and match to the task, and rank them.
        """,
    )
    query = f"""
    <task>
    {task}
    </task>
    """
    rep = agent.run(query)
    return rep.content


def select_tool(query):
    agent = Agent(
        model=model,
        output_schema=ToolList,
        use_json_mode=True,
        instructions="""
        you are a bioinformatician, you are given a task and a list of tools, you need to select the most directly relevant tools to use to solve the task，
        if the task is not related to the tools, you should return an empty list.
        if there are multiple tools that are related to the task, you should rank them based on the relevance and match to the task.
        """,
    )
    rep = agent.run(query)
    return rep.content
