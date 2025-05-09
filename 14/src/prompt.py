from langchain_core.prompts import PromptTemplate

def get_prompt(template: str) -> PromptTemplate:
    """
    주어진 문자열 템플릿을 기반으로 LangChain의 PromptTemplate 객체를 생성합니다.

    Args:
        template (str): 프롬프트 문자열. 예: "{context}\n\n질문: {question}"

    Returns:
        PromptTemplate: LangChain에서 사용할 수 있는 프롬프트 템플릿 객체
    """
    return PromptTemplate.from_template(template)