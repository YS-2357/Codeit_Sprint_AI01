from langchain_core.prompts import PromptTemplate

def get_prompt():
    return PromptTemplate.from_template(
        """
아래에 주어진 맥락을 이용해 질문에 대해 답변해 줘.
주어진 맥락으로 답변이 어려운 상황이라면, 그냥 모른다고 답하면 되고 억지로 답변을 꾸며 내지 마.
최대한 자세하게 답변해 줘.
반드시 한국어로 답변해야 해.

맥락:
{context}

질문:
{question}
"""
    )