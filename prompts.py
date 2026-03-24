from langchain_core.prompts import PromptTemplate

analysis_prompt = PromptTemplate(
    template="""
You are a highly experienced legal analyst.

Chat History:
{chat_history}

Case Description:
{user_input}

[Rest same...]
""",
    input_variables=["user_input", "chat_history"]
)

advice_prompt = PromptTemplate(
    template="""
You are a professional lawyer.

Chat History:
{chat_history}

Analysis:
{analysis_output}

[Rest same...]
""",
    input_variables=["analysis_output", "chat_history"]
)