from langchain_openai import ChatOpenAI
# from langchain_groq import ChatGroq
from langchain.vectorstores import  FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

from langgraph.graph import END, StateGraph

from dotenv import load_dotenv
from pprint import pprint
import os
import re as _re
import json as _json
from typing_extensions import TypedDict
from typing import List, TypedDict



### Helper functions for the notebook
from helper_functions import escape_quotes, text_wrap


class DashScopeEmbeddings(OpenAIEmbeddings):
    """兼容 DashScope 的 Embedding 包装类，发送纯字符串而非 token 数组"""

    def embed_documents(self, texts, **kwargs):
        results = []
        batch_size = 6
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = self.client.create(input=batch, model=self.model)
            results.extend([r.embedding for r in response.data])
        return results

    def embed_query(self, text):
        response = self.client.create(input=[text], model=self.model)
        return response.data[0].embedding

    # Ragas 等框架通过 async 方法调用 Embedding，此处回退到同步实现
    async def aembed_documents(self, texts, **kwargs):
        return self.embed_documents(texts, **kwargs)

    async def aembed_query(self, text):
        return self.embed_query(text)



"""
Set the environment variables for the API keys.
"""
load_dotenv(override=True)
os.environ["PYDEVD_WARN_EVALUATION_TIMEOUT"] = "100000"
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
os.environ["OPENAI_BASE_URL"] = os.getenv('OPENAI_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')



def create_retrievers():
    embeddings = DashScopeEmbeddings(model="text-embedding-v3")
    chunks_vector_store =  FAISS.load_local("chunks_vector_store", embeddings, allow_dangerous_deserialization=True)
    chapter_summaries_vector_store =  FAISS.load_local("chapter_summaries_vector_store", embeddings, allow_dangerous_deserialization=True)
    book_quotes_vectorstore =  FAISS.load_local("book_quotes_vectorstore", embeddings, allow_dangerous_deserialization=True)



    chunks_query_retriever = chunks_vector_store.as_retriever(search_kwargs={"k": 1})     
    chapter_summaries_query_retriever = chapter_summaries_vector_store.as_retriever(search_kwargs={"k": 1})
    book_quotes_query_retriever = book_quotes_vectorstore.as_retriever(search_kwargs={"k": 10})
    return chunks_query_retriever, chapter_summaries_query_retriever, book_quotes_query_retriever

chunks_query_retriever, chapter_summaries_query_retriever, book_quotes_query_retriever = create_retrievers()

def retrieve_context_per_question(state):
    """
    Retrieves relevant context for a given question. The context is retrieved from the book chunks and chapter summaries.

    Args:
        state: A dictionary containing the question to answer.
    """
    # Retrieve relevant documents
    print("Retrieving relevant chunks...")
    question = state["question"]
    docs = chunks_query_retriever.get_relevant_documents(question)

    # Concatenate document content
    context = " ".join(doc.page_content for doc in docs)



    print("Retrieving relevant chapter summaries...")
    docs_summaries = chapter_summaries_query_retriever.get_relevant_documents(state["question"])

    # Concatenate chapter summaries with citation information
    context_summaries = " ".join(
        f"{doc.page_content} (Chapter {doc.metadata['chapter']})" for doc in docs_summaries
    )

    print("Retrieving relevant book quotes...")
    docs_book_quotes = book_quotes_query_retriever.get_relevant_documents(state["question"])
    book_qoutes = " ".join(doc.page_content for doc in docs_book_quotes)


    all_contexts = context + context_summaries + book_qoutes
    all_contexts = escape_quotes(all_contexts)

    return {"context": all_contexts, "question": question}


def create_keep_only_relevant_content_chain():
    keep_only_relevant_content_prompt_template = """you receive a query: {query} and retrieved docuemnts: {retrieved_documents} from a
    vector store.
    You need to filter out all the non relevant information that don't supply important information regarding the {query}.
    your goal is just to filter out the non relevant information.
    you can remove parts of sentences that are not relevant to the query or remove whole sentences that are not relevant to the query.
    DO NOT ADD ANY NEW INFORMATION THAT IS NOT IN THE RETRIEVED DOCUMENTS.
    output the filtered relevant content.
    """


    class KeepRelevantContent(BaseModel):
        relevant_content: str = Field(description="The relevant content from the retrieved documents that is relevant to the query.")


    keep_only_relevant_content_prompt = PromptTemplate(
        template=keep_only_relevant_content_prompt_template,
        input_variables=["query", "retrieved_documents"],
    )


    keep_only_relevant_content_llm = ChatOpenAI(temperature=0, model_name="qwen-max", max_tokens=2000)
    keep_only_relevant_content_chain = keep_only_relevant_content_prompt | keep_only_relevant_content_llm.with_structured_output(KeepRelevantContent)
    return keep_only_relevant_content_chain

keep_only_relevant_content_chain = create_keep_only_relevant_content_chain()
def keep_only_relevant_content(state):
    """
    Keeps only the relevant content from the retrieved documents that is relevant to the query.

    Args:
        question: The query question.
        context: The retrieved documents.
        chain: The LLMChain instance.

    Returns:
        The relevant content from the retrieved documents that is relevant to the query.
    """
    question = state["question"]
    context = state["context"]

    input_data = {
    "query": question,
    "retrieved_documents": context
}
    print("keeping only the relevant content...")
    pprint("--------------------")
    output = keep_only_relevant_content_chain.invoke(input_data)
    relevant_content = output.relevant_content
    relevant_content = "".join(relevant_content)
    relevant_content = escape_quotes(relevant_content)

    return {"relevant_context": relevant_content, "context": context, "question": question}


def create_question_answer_from_context_cot_chain():
    class QuestionAnswerFromContext(BaseModel):
        answer_based_on_content: str = Field(description="generates an answer to a query based on a given context.")

    question_answer_from_context_llm = ChatOpenAI(temperature=0, model_name="qwen-max", max_tokens=2000)


    question_answer_cot_prompt_template = """
    Examples of Chain-of-Thought Reasoning for Financial Report Analysis

    Example 1

    Context: Total net revenue for FY2025 was $391 billion, up 5% year-over-year. Products revenue was $268 billion and Services revenue was $123 billion. Products gross margin was 37% while Services gross margin was 74%.
    Question: Which segment contributes more to overall profitability?
    Reasoning Chain:
    Products revenue is $268 billion with a 37% gross margin, yielding roughly $99.2 billion in gross profit.
    Services revenue is $123 billion with a 74% gross margin, yielding roughly $91.0 billion in gross profit.
    Although Products generates more total revenue, Services gross profit ($91B) is close to Products ($99.2B) despite being less than half the revenue.
    Services has a disproportionately high contribution to profitability relative to its revenue share.
    Therefore, while Products contributes slightly more absolute gross profit, Services is the stronger driver of profit margins.

    Example 2
    Context: The company faces risks related to supply chain concentration in certain regions. Geopolitical tensions could disrupt manufacturing operations. Additionally, regulatory changes in international markets may affect product availability.
    Question: What are the key supply chain risks mentioned?
    Reasoning Chain:
    The context identifies three distinct supply chain risks:
    1. Concentration of supply chain in specific geographic regions
    2. Geopolitical tensions that could disrupt manufacturing
    3. Regulatory changes in international markets affecting product availability
    These risks are interconnected — geographic concentration amplifies the impact of both geopolitical and regulatory disruptions.

    Example 3
    Context: Research and development expenses were $31.4 billion in FY2025, representing 8% of total net revenue.
    Question: How does R&D spending compare to the company's revenue growth rate?
    Reasoning Chain:
    The context states R&D expenses were $31.4 billion, which is 8% of total net revenue.
    However, the context does not provide the revenue growth rate or prior year R&D figures.
    Without comparative data from previous years, we cannot determine how R&D spending growth relates to revenue growth.
    We can only state the current R&D expense level based on the given context.

    For the question below, provide your answer by first showing your step-by-step reasoning process, breaking down the problem into a chain of thought before arriving at the final answer,
    just like in the previous examples.

    CRITICAL RULE: As a financial analyst, you MUST preserve ALL specific dollar amounts ($), percentages (%), and numerical figures found in the context. List every relevant number explicitly — never summarize numbers into vague phrases like "increased significantly" when the exact figure is available. Missing a key number is a serious error in financial analysis.

    Context
    {context}
    Question
    {question}
    """

    question_answer_from_context_cot_prompt = PromptTemplate(
        template=question_answer_cot_prompt_template,
        input_variables=["context", "question"],
    )
    question_answer_from_context_cot_chain = question_answer_from_context_cot_prompt | question_answer_from_context_llm.with_structured_output(QuestionAnswerFromContext)
    return question_answer_from_context_cot_chain

question_answer_from_context_cot_chain = create_question_answer_from_context_cot_chain()

def answer_question_from_context(state):
    """
    Answers a question from a given context.

    Args:
        question: The query question.
        context: The context to answer the question from.
        chain: The LLMChain instance.

    Returns:
        The answer to the question from the context.
    """
    question = state["question"]
    context = state["aggregated_context"] if "aggregated_context" in state else state["context"]

    input_data = {
    "question": question,
    "context": context
}
    print("Answering the question from the retrieved context...")

    output = question_answer_from_context_cot_chain.invoke(input_data)
    answer = output.answer_based_on_content
    print(f'answer before checking hallucination: {answer}')
    return {"answer": answer, "context": context, "question": question}




def create_is_relevant_content_chain():

    is_relevant_content_prompt_template = """you receive a query: {query} and a context: {context} retrieved from a vector store. 
    You need to determine if the document is relevant to the query. """

    class Relevance(BaseModel):
        is_relevant: bool = Field(description="Whether the document is relevant to the query.")
        explanation: str = Field(description="An explanation of why the document is relevant or not.")

    # is_relevant_json_parser = JsonOutputParser(pydantic_object=Relevance)
    # is_relevant_llm = ChatGroq(temperature=0, model_name="llama3-70b-8192", groq_api_key=groq_api_key, max_tokens=4000)
    is_relevant_llm = ChatOpenAI(temperature=0, model_name="qwen-max", max_tokens=2000)

    is_relevant_content_prompt = PromptTemplate(
        template=is_relevant_content_prompt_template,
        input_variables=["query", "context"],
        # partial_variables={"format_instructions": is_relevant_json_parser.get_format_instructions()},
    )
    is_relevant_content_chain = is_relevant_content_prompt | is_relevant_llm.with_structured_output(Relevance)
    return is_relevant_content_chain

is_relevant_content_chain = create_is_relevant_content_chain()

def is_relevant_content(state):
    """
    Determines if the document is relevant to the query.

    Args:
        question: The query question.
        context: The context to determine relevance.
    """

    question = state["question"]
    context = state["context"]

    input_data = {
    "query": question,
    "context": context
}

    # Invoke the chain to determine if the document is relevant
    output = is_relevant_content_chain.invoke(input_data)
    print("Determining if the document is relevant...")
    if output["is_relevant"] == True:
        print("The document is relevant.")
        return "relevant"
    else:
        print("The document is not relevant.")
        return "not relevant"


class _GroundedResult:
    """Simple container for grounding check result."""
    def __init__(self, grounded_on_facts: bool):
        self.grounded_on_facts = grounded_on_facts

def _parse_bool_from_llm(output, field_name="grounded_on_facts") -> bool:
    """从 LLM 文本输出中解析布尔值，兼容各种格式。"""
    text = output.content if hasattr(output, 'content') else str(output)
    text_lower = text.lower().strip()
    # 尝试 JSON 解析
    m = _re.search(r'\{[\s\S]*\}', text)
    if m:
        try:
            data = _json.loads(m.group())
            val = data.get(field_name, data.get("grounded", None))
            if val is not None:
                return bool(val)
        except _json.JSONDecodeError:
            pass
    # 关键词匹配
    if "true" in text_lower or "yes" in text_lower or "grounded" in text_lower:
        return True
    return False

def create_is_grounded_on_facts_chain():
    is_grounded_on_facts_llm = ChatOpenAI(temperature=0, model_name="qwen-max", max_tokens=2000)
    is_grounded_on_facts_prompt_template = """You are a fact-checker that determines if the given answer {answer} is grounded in the given context {context}
    you don't mind if it doesn't make sense, as long as it is grounded in the context.
    Reply with ONLY a JSON object: {{"grounded_on_facts": true}} or {{"grounded_on_facts": false}}
    """
    is_grounded_on_facts_prompt = PromptTemplate(
        template=is_grounded_on_facts_prompt_template,
        input_variables=["context", "answer"],
    )

    def _parse_grounded(output):
        return _GroundedResult(_parse_bool_from_llm(output, "grounded_on_facts"))

    is_grounded_on_facts_chain = is_grounded_on_facts_prompt | is_grounded_on_facts_llm | _parse_grounded
    return is_grounded_on_facts_chain


def create_can_be_answered_chain():
    can_be_answered_prompt_template = """You receive a query: {question} and a context: {context}. 
    You need to determine if the question can be fully answered based on the context."""

    class QuestionAnswer(BaseModel):
        can_be_answered: bool = Field(description="binary result of whether the question can be fully answered or not")
        explanation: str = Field(description="An explanation of why the question can be fully answered or not.")

    # can_be_answered_json_parser = JsonOutputParser(pydantic_object=QuestionAnswer)

    answer_question_prompt = PromptTemplate(
        template=can_be_answered_prompt_template,
        input_variables=["question","context"],
        # partial_variables={"format_instructions": can_be_answered_json_parser.get_format_instructions()},
    )

    # can_be_answered_llm = ChatGroq(temperature=0, model_name="llama3-70b-8192", groq_api_key=groq_api_key, max_tokens=4000)
    can_be_answered_llm = ChatOpenAI(temperature=0, model_name="qwen-max", max_tokens=2000)
    can_be_answered_chain = answer_question_prompt | can_be_answered_llm.with_structured_output(QuestionAnswer)
    return can_be_answered_chain


def create_is_distilled_content_grounded_on_content_chain():
    is_distilled_content_grounded_on_content_prompt_template = """you receive some distilled content: {distilled_content} and the original context: {original_context}.
        you need to determine if the distilled content is grounded on the original context.
        Reply with ONLY a JSON object: {{"grounded": true}} or {{"grounded": false}}
        """

    is_distilled_content_grounded_on_content_llm = ChatOpenAI(temperature=0, model_name="qwen-max", max_tokens=2000)

    is_distilled_content_grounded_on_content_prompt = PromptTemplate(
        template=is_distilled_content_grounded_on_content_prompt_template,
        input_variables=["distilled_content", "original_context"],
    )

    class _DistilledGroundedResult:
        def __init__(self, grounded: bool, explanation: str = ""):
            self.grounded = grounded
            self.explanation = explanation

    def _parse_distilled_grounded(output):
        return _DistilledGroundedResult(_parse_bool_from_llm(output, "grounded"))

    is_distilled_content_grounded_on_content_chain = is_distilled_content_grounded_on_content_prompt | is_distilled_content_grounded_on_content_llm | _parse_distilled_grounded
    return is_distilled_content_grounded_on_content_chain

is_distilled_content_grounded_on_content_chain = create_is_distilled_content_grounded_on_content_chain()

def is_distilled_content_grounded_on_content(state):
    pprint("--------------------")

    """
    Determines if the distilled content is grounded on the original context.
    Implements Graceful Degradation: after MAX_GROUNDING_RETRIES, accepts content as-is.
    """

    retry_count = (state.get("grounding_retry_count") or 0) + 1
    state["grounding_retry_count"] = retry_count

    # Graceful Degradation: 超过最大重试次数，强制接受当前内容
    if retry_count > MAX_GROUNDING_RETRIES:
        print(f"[Graceful Degradation] Grounding check retried {MAX_GROUNDING_RETRIES} times. "
              f"Accepting current content as-is.")
        return "grounded on the original context"

    print(f"Determining if the distilled content is grounded on the original context... (attempt {retry_count}/{MAX_GROUNDING_RETRIES})")
    distilled_content = state["relevant_context"]
    original_context = state["context"]

    input_data = {
        "distilled_content": distilled_content,
        "original_context": original_context
    }

    output = is_distilled_content_grounded_on_content_chain.invoke(input_data)
    grounded = output.grounded

    if grounded:
        print("The distilled content is grounded on the original context.")
        return "grounded on the original context"
    else:
        print("The distilled content is not grounded on the original context.")
        return "not grounded on the original context"
    

def retrieve_chunks_context_per_question(state):
    """
    Retrieves relevant context for a given question. The context is retrieved from the book chunks and chapter summaries.

    Args:
        state: A dictionary containing the question to answer.
    """
    # Retrieve relevant documents
    print("Retrieving relevant chunks...")
    question = state["question"]
    docs = chunks_query_retriever.get_relevant_documents(question)

    # Concatenate document content
    context = " ".join(doc.page_content for doc in docs)
    context = escape_quotes(context)
    return {"context": context, "question": question}

def retrieve_summaries_context_per_question(state):

    print("Retrieving relevant chapter summaries...")
    question = state["question"]

    docs_summaries = chapter_summaries_query_retriever.get_relevant_documents(state["question"])

    # Concatenate chapter summaries with citation information
    context_summaries = " ".join(
        f"{doc.page_content} (Chapter {doc.metadata['chapter']})" for doc in docs_summaries
    )
    context_summaries = escape_quotes(context_summaries)
    return {"context": context_summaries, "question": question}

def retrieve_book_quotes_context_per_question(state):
    question = state["question"]

    print("Retrieving relevant book quotes...")
    docs_book_quotes = book_quotes_query_retriever.get_relevant_documents(state["question"])
    book_qoutes = " ".join(doc.page_content for doc in docs_book_quotes)
    book_qoutes_context = escape_quotes(book_qoutes)

    return {"context": book_qoutes_context, "question": question}



MAX_GROUNDING_RETRIES = 3  # 内层 Grounding Check 最大重试次数

class QualitativeRetrievalGraphState(TypedDict):
    """
    Represents the state of our graph.
    """

    question: str
    context: str
    relevant_context: str
    grounding_retry_count: int  # Grounding Check 重试计数


def create_qualitative_retrieval_book_chunks_workflow_app():
    qualitative_chunks_retrieval_workflow = StateGraph(QualitativeRetrievalGraphState)

    # Define the nodes
    qualitative_chunks_retrieval_workflow.add_node("retrieve_chunks_context_per_question",retrieve_chunks_context_per_question)
    qualitative_chunks_retrieval_workflow.add_node("keep_only_relevant_content",keep_only_relevant_content)

    # Build the graph
    qualitative_chunks_retrieval_workflow.set_entry_point("retrieve_chunks_context_per_question")

    qualitative_chunks_retrieval_workflow.add_edge("retrieve_chunks_context_per_question", "keep_only_relevant_content")

    qualitative_chunks_retrieval_workflow.add_conditional_edges(
        "keep_only_relevant_content",
        is_distilled_content_grounded_on_content,
        {"grounded on the original context":END,
        "not grounded on the original context":"keep_only_relevant_content"},
        )

    
    qualitative_chunks_retrieval_workflow_app = qualitative_chunks_retrieval_workflow.compile()
    return qualitative_chunks_retrieval_workflow_app


def create_qualitative_retrieval_chapter_summaries_workflow_app():
    qualitative_summaries_retrieval_workflow = StateGraph(QualitativeRetrievalGraphState)

    # Define the nodes
    qualitative_summaries_retrieval_workflow.add_node("retrieve_summaries_context_per_question",retrieve_summaries_context_per_question)
    qualitative_summaries_retrieval_workflow.add_node("keep_only_relevant_content",keep_only_relevant_content)

    # Build the graph
    qualitative_summaries_retrieval_workflow.set_entry_point("retrieve_summaries_context_per_question")

    qualitative_summaries_retrieval_workflow.add_edge("retrieve_summaries_context_per_question", "keep_only_relevant_content")

    qualitative_summaries_retrieval_workflow.add_conditional_edges(
        "keep_only_relevant_content",
        is_distilled_content_grounded_on_content,
        {"grounded on the original context":END,
        "not grounded on the original context":"keep_only_relevant_content"},
        )


    qualitative_summaries_retrieval_workflow_app = qualitative_summaries_retrieval_workflow.compile()
    return qualitative_summaries_retrieval_workflow_app


def create_qualitative_book_quotes_retrieval_workflow_app():
    qualitative_book_quotes_retrieval_workflow = StateGraph(QualitativeRetrievalGraphState)

    # Define the nodes
    qualitative_book_quotes_retrieval_workflow.add_node("retrieve_book_quotes_context_per_question",retrieve_book_quotes_context_per_question)
    qualitative_book_quotes_retrieval_workflow.add_node("keep_only_relevant_content",keep_only_relevant_content)

    # Build the graph
    qualitative_book_quotes_retrieval_workflow.set_entry_point("retrieve_book_quotes_context_per_question")

    qualitative_book_quotes_retrieval_workflow.add_edge("retrieve_book_quotes_context_per_question", "keep_only_relevant_content")

    qualitative_book_quotes_retrieval_workflow.add_conditional_edges(
        "keep_only_relevant_content",
        is_distilled_content_grounded_on_content,
        {"grounded on the original context":END,
        "not grounded on the original context":"keep_only_relevant_content"},
        )

    qualitative_book_quotes_retrieval_workflow_app = qualitative_book_quotes_retrieval_workflow.compile()

    return qualitative_book_quotes_retrieval_workflow_app



is_grounded_on_facts_chain = create_is_grounded_on_facts_chain()

def is_answer_grounded_on_context(state):
    """Determines if the answer to the question is grounded in the facts.
    
    Args:
        state: A dictionary containing the context and answer.
    """
    print("Checking if the answer is grounded in the facts...")
    context = state["context"]
    answer = state["answer"]
    
    result = is_grounded_on_facts_chain.invoke({"context": context, "answer": answer})
    grounded_on_facts = result.grounded_on_facts
    if not grounded_on_facts:
        print("The answer is hallucination.")
        return "hallucination"
    else:
        print("The answer is grounded in the facts.")
        return "grounded on context"


def create_qualitative_answer_workflow_app():
    class QualitativeAnswerGraphState(TypedDict):
        """
        Represents the state of our graph.

        """

        question: str
        context: str
        answer: str

    qualitative_answer_workflow = StateGraph(QualitativeAnswerGraphState)

    # Define the nodes

    qualitative_answer_workflow.add_node("answer_question_from_context",answer_question_from_context)

    # Build the graph
    qualitative_answer_workflow.set_entry_point("answer_question_from_context")

    qualitative_answer_workflow.add_conditional_edges(
    "answer_question_from_context",is_answer_grounded_on_context ,{"hallucination":"answer_question_from_context", "grounded on context":END}

    )

    qualitative_answer_workflow_app = qualitative_answer_workflow.compile()
    return qualitative_answer_workflow_app


MAX_REPLAN_RETRIES = 5  # 最大重规划次数，超过后触发兜底回答

class PlanExecute(TypedDict):
    curr_state: str
    question: str
    anonymized_question: str
    query_to_retrieve_or_answer: str
    plan: List[str]
    past_steps: List[str]
    mapping: dict
    curr_context: str
    aggregated_context: str
    tool: str
    response: str
    replan_count: int  # 重规划计数器，用于 Graceful Degradation

class Plan(BaseModel):
        """Plan to follow in future"""

        steps: List[str] = Field(
            description="different steps to follow, should be in sorted order"
        )


def _repair_json(raw: str) -> dict:
    """尝试修复 qwen-max 返回的常见 JSON 格式问题"""
    # 提取 JSON 对象
    m = _re.search(r'\{[\s\S]*\}', raw)
    s = m.group() if m else raw

    # 替换中文引号
    s = s.replace('\u201c', '"').replace('\u201d', '"')
    s = s.replace('\u2018', "'").replace('\u2019', "'")

    # 修复多余的引号: ""]} -> "]}
    s = _re.sub(r'"{2,}(\s*[\]\}])', r'"\1', s)

    # 修复缺少逗号: "..." "..." -> "...", "..."
    s = _re.sub(r'"\s*\n\s*"', '", "', s)

    try:
        return _json.loads(s)
    except _json.JSONDecodeError:
        pass

    # 更激进：用正则提取所有引号内的步骤字符串
    steps = _re.findall(r'"((?:[^"\\]|\\.)+)"', s)
    if steps:
        # 过滤掉 key 名称 "steps"
        steps = [st for st in steps if st.lower().strip() != "steps"]
        return {"steps": steps}

    raise ValueError(f"无法解析 Plan JSON: {raw[:300]}")


def robust_parse_plan(output) -> Plan:
    """从 LLM 文本输出中解析 Plan，带 JSON 修复"""
    text = output.content if hasattr(output, 'content') else str(output)
    data = _repair_json(text)
    return Plan(steps=data.get("steps", []))


def create_plan_chain():
    

    planner_prompt =""" For the given query {question} about a company's 10-K annual filing, come up with a simple step by step plan of how to figure out the answer.

    This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps.
    The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.
    Available information sources: report text chunks, section summaries, and key financial metrics extracted from the filing.

    Output ONLY a valid JSON object in this exact format (no other text):
    {{"steps": ["step 1", "step 2", "step 3"]}}
    """

    planner_prompt = PromptTemplate(
        template=planner_prompt,
        input_variables=["question"],
        )

    planner_llm = ChatOpenAI(temperature=0, model_name="qwen-max", max_tokens=2000)

    planner = planner_prompt | planner_llm | robust_parse_plan
    return planner


def create_break_down_plan_chain():

    break_down_plan_prompt_template = """You receive a plan {plan} which contains a series of steps to follow in order to answer a query about a company's 10-K annual report.
    you need to go through the plan refine it according to this:
    1. every step has to be able to be executed by either:
        i. retrieving relevant information from a vector store of 10-K report text chunks (for specific details, clauses, or passages)
        ii. retrieving relevant information from a vector store of section summaries (for high-level overview of sections like Business, Risk Factors, MD&A)
        iii. retrieving relevant information from a vector store of key financial metrics (for specific numbers: revenue, profit, margins, percentages)
        iv. answering a question from a given context.
    2. every step should contain all the information needed to execute it.

    Output ONLY a valid JSON object in this exact format (no other text):
    {{"steps": ["step 1", "step 2", "step 3"]}}
    """

    break_down_plan_prompt = PromptTemplate(
        template=break_down_plan_prompt_template,
        input_variables=["plan"],
    )

    break_down_plan_llm = ChatOpenAI(temperature=0, model_name="qwen-max", max_tokens=2000)

    break_down_plan_chain = break_down_plan_prompt | break_down_plan_llm | robust_parse_plan

    return break_down_plan_chain

def create_replanner_chain():
    # class ActPossibleResults(BaseModel):
    #     """Possible results of the action."""
    #     plan: Plan = Field(description="Plan to follow in future.")
    #     explanation: str = Field(description="Explanation of the action.")
        

    # act_possible_results_parser = JsonOutputParser(pydantic_object=ActPossibleResults)

    replanner_prompt_template =""" For the given objective about a company's 10-K annual filing, come up with a simple step by step plan of how to figure out the answer.
    This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps.
    The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.
    You can retrieve information from: report text chunks, section summaries, or key financial metrics. You can also answer questions from aggregated context.

    assume that the answer was not found yet and you need to update the plan accordingly, so the plan should never be empty.

    Your objective was this:
    {question}

    Your original plan was this:
    {plan}

    You have currently done the follow steps:
    {past_steps}

    You already have the following context:
    {aggregated_context}

    Update your plan accordingly. If further steps are needed, fill out the plan with only those steps.
    Do not return previously done steps as part of the plan.

    Output ONLY a valid JSON object in this exact format (no other text):
    {{"steps": ["step 1", "step 2", "step 3"]}}
    """

    replanner_prompt = PromptTemplate(
        template=replanner_prompt_template,
        input_variables=["question", "plan", "past_steps", "aggregated_context"],
    )

    replanner_llm = ChatOpenAI(temperature=0, model_name="qwen-max", max_tokens=2000)

    replanner = replanner_prompt | replanner_llm | robust_parse_plan
    return replanner

def create_task_handler_chain():
    tasks_handler_prompt_template = """You are a task handler for analyzing a company's 10-K annual filing. You receive a task {curr_task} and have to decide which tool to use.
    You have the following tools at your disposal:
    Tool A: retrieves relevant information from a vector store of 10-K report text chunks.
    - use Tool A when you need specific details, contract terms, risk descriptions, or detailed passages from the report.
    Tool B: retrieves relevant information from a vector store of section summaries.
    - use Tool B when you need a high-level overview of a section (e.g., Business Overview, Risk Factors, MD&A).
    Tool C: retrieves relevant information from a vector store of key financial metrics.
    - use Tool C when you need specific numerical data like revenue, profit, margins, growth rates, or dollar amounts.
    Tool D: answers a question from a given context.
    - use Tool D ONLY when the current task can be answered by the aggregated context {aggregated_context}

    you also receive the last tool used {last_tool}
    if {last_tool} was retrieve_chunks, use other tools than Tool A.

    You also have the past steps {past_steps} that you can use to make decisions and understand the context of the task.
    You also have the initial user's question {question} that you can use to make decisions and understand the context of the task.
    if you decide to use Tools A,B or C, output the query to be used for the tool and also output the relevant tool.
    if you decide to use Tool D, output the question to be used for the tool, the context, and also that the tool to be used is Tool D.

    """

    class TaskHandlerOutput(BaseModel):
        """Output schema for the task handler."""
        query: str = Field(description="The query to be either retrieved from the vector store, or the question that should be answered from context.")
        curr_context: str = Field(description="The context to be based on in order to answer the query.")
        tool: str = Field(description="MUST be exactly one of these four values: retrieve_chunks, retrieve_summaries, retrieve_quotes, answer_from_context")


    task_handler_prompt = PromptTemplate(
        template=tasks_handler_prompt_template,
        input_variables=["curr_task", "aggregated_context", "last_tool" "past_steps", "question"],
    )

    task_handler_llm = ChatOpenAI(temperature=0, model_name="qwen-max", max_tokens=2000)
    task_handler_chain = task_handler_prompt | task_handler_llm.with_structured_output(TaskHandlerOutput)
    return task_handler_chain

def create_anonymize_question_chain():
    class AnonymizeQuestion(BaseModel):
        """Anonymized question and mapping."""
        anonymized_question : str = Field(description="Anonymized question.")
        mapping: dict = Field(description="Mapping of original name entities to variables.")
        explanation: str = Field(description="Explanation of the action.")

    anonymize_question_parser = JsonOutputParser(pydantic_object=AnonymizeQuestion)


    anonymize_question_prompt_template = """ You are a question anonymizer. The input you receive is a string containing several words that
    construct a question {question}. Your goal is to change all named entities (company names, product names, people names, specific fiscal years) in the input to variables, and remember the mapping.
    ```example1:
            if the input is \"How did Apple's iPhone revenue perform in FY2025?\" the output should be \"How did X's Y revenue perform in Z?\" and the mapping should be {{\"X\": \"Apple\", \"Y\": \"iPhone\", \"Z\": \"FY2025\"}} ```
    ```example2:
            if the input is \"What are the risks related to China supply chain mentioned by Tim Cook?\"
            the output should be \"What are the risks related to X Y mentioned by Z?\" and the mapping should be {{\"X\": \"China\", \"Y\": \"supply chain\", \"Z\": \"Tim Cook\"}}```
    you must replace all named entities in the input with variables, and remember the mapping of the original named entities to the variables.
    output the anonymized question and the mapping as two separate fields in a json format as described here, without any additional text apart from the json format.
   """



    anonymize_question_prompt = PromptTemplate(
        template=anonymize_question_prompt_template,
        input_variables=["question"],
        partial_variables={"format_instructions": anonymize_question_parser.get_format_instructions()},
    )

    anonymize_question_llm = ChatOpenAI(temperature=0, model_name="qwen-max", max_tokens=2000)
    anonymize_question_chain = anonymize_question_prompt | anonymize_question_llm | anonymize_question_parser
    return anonymize_question_chain


def create_deanonymize_plan_chain():
    de_anonymize_plan_prompt_template = """ you receive a list of tasks: {plan}, where some of the words are replaced with mapped variables. you also receive
    the mapping for those variables to words {mapping}. replace all the variables in the list of tasks with the mapped words. if no variables are present,
    return the original list of tasks.

    Output ONLY a valid JSON object in this exact format (no other text):
    {{"plan": ["step 1 with real names", "step 2 with real names"]}}
    """

    de_anonymize_plan_prompt = PromptTemplate(
        template=de_anonymize_plan_prompt_template,
        input_variables=["plan", "mapping"],
    )

    de_anonymize_plan_llm = ChatOpenAI(temperature=0, model_name="qwen-max", max_tokens=2000)

    class _DeAnonymizedPlan:
        def __init__(self, plan):
            self.plan = plan

    def _parse_deanonymized(output):
        text = output.content if hasattr(output, 'content') else str(output)
        data = _repair_json(text)
        steps = data.get("plan", data.get("steps", []))
        return _DeAnonymizedPlan(steps)

    de_anonymize_plan_chain = de_anonymize_plan_prompt | de_anonymize_plan_llm | _parse_deanonymized
    return de_anonymize_plan_chain

def create_can_be_answered_already_chain():
    can_be_answered_already_prompt_template = """You receive a query: {question} and a context: {context}.
    You need to determine if the question can be fully answered relying only the given context.
    The only infomation you have and can rely on is the context you received.
    you have no prior knowledge of the question or the context.
    Reply with ONLY a JSON object: {{"can_be_answered": true}} or {{"can_be_answered": false}}
    """

    can_be_answered_already_prompt = PromptTemplate(
        template=can_be_answered_already_prompt_template,
        input_variables=["question","context"],
    )

    class _CanBeAnsweredResult:
        def __init__(self, can_be_answered: bool):
            self.can_be_answered = can_be_answered

    def _parse_can_be_answered(output):
        return _CanBeAnsweredResult(_parse_bool_from_llm(output, "can_be_answered"))

    can_be_answered_already_llm = ChatOpenAI(temperature=0, model_name="qwen-max", max_tokens=2000)
    can_be_answered_already_chain = can_be_answered_already_prompt | can_be_answered_already_llm | _parse_can_be_answered
    return can_be_answered_already_chain


task_handler_chain = create_task_handler_chain()
qualitative_chunks_retrieval_workflow_app = create_qualitative_retrieval_book_chunks_workflow_app()
qualitative_summaries_retrieval_workflow_app = create_qualitative_retrieval_chapter_summaries_workflow_app()
qualitative_book_quotes_retrieval_workflow_app = create_qualitative_book_quotes_retrieval_workflow_app()
qualitative_answer_workflow_app = create_qualitative_answer_workflow_app()
de_anonymize_plan_chain = create_deanonymize_plan_chain()
planner = create_plan_chain()
break_down_plan_chain = create_break_down_plan_chain()
replanner = create_replanner_chain()
anonymize_question_chain = create_anonymize_question_chain()
can_be_answered_already_chain = create_can_be_answered_already_chain()


def run_task_handler_chain(state: PlanExecute):
    """ Run the task handler chain to decide which tool to use to execute the task.
    Args:
       state: The current state of the plan execution.
    Returns:
       The updated state of the plan execution.
    """
    state["curr_state"] = "task_handler"
    print("the current plan is:")
    print(state["plan"])
    pprint("--------------------") 

    if not state['past_steps']:
        state["past_steps"] = []

    curr_task = state["plan"][0]

    inputs = {"curr_task": curr_task,
               "aggregated_context": state["aggregated_context"],
                "last_tool": state["tool"],
                "past_steps": state["past_steps"],
                "question": state["question"]}
    
    output = task_handler_chain.invoke(inputs)

    state["past_steps"].append(curr_task)
    state["plan"].pop(0)

    tool_name = output.tool.lower().strip()
    state["query_to_retrieve_or_answer"] = output.query

    if "chunk" in tool_name or tool_name in ("tool a", "a"):
        state["tool"] = "retrieve_chunks"
    elif "summar" in tool_name or tool_name in ("tool b", "b"):
        state["tool"] = "retrieve_summaries"
    elif "quote" in tool_name or "metric" in tool_name or tool_name in ("tool c", "c"):
        state["tool"] = "retrieve_quotes"
    elif "answer" in tool_name or "context" in tool_name or tool_name in ("tool d", "d"):
        state["curr_context"] = output.curr_context
        state["tool"] = "answer"
    else:
        print(f"Warning: unexpected tool '{output.tool}', defaulting to retrieve_summaries")
        state["tool"] = "retrieve_summaries"
    return state  



def retrieve_or_answer(state: PlanExecute):
    """Decide whether to retrieve or answer the question based on the current state.
    Args:
        state: The current state of the plan execution.
    Returns:
        updates the tool to use .
    """
    state["curr_state"] = "decide_tool"
    print("deciding whether to retrieve or answer")
    if state["tool"] == "retrieve_chunks":
        return "chosen_tool_is_retrieve_chunks"
    elif state["tool"] == "retrieve_summaries":
        return "chosen_tool_is_retrieve_summaries"
    elif state["tool"] == "retrieve_quotes":
        return "chosen_tool_is_retrieve_quotes"
    elif state["tool"] == "answer":
        return "chosen_tool_is_answer"
    else:
        raise ValueError("Invalid tool was outputed. Must be either 'retrieve' or 'answer_from_context'")  



def run_qualitative_chunks_retrieval_workflow(state):
    """
    Run the qualitative chunks retrieval workflow.
    Args:
        state: The current state of the plan execution.
    Returns:
        The state with the updated aggregated context.
    """
    state["curr_state"] = "retrieve_chunks"
    print("Running the qualitative chunks retrieval workflow...")
    question = state["query_to_retrieve_or_answer"]
    inputs = {"question": question}
    for output in qualitative_chunks_retrieval_workflow_app.stream(inputs):
        for _, _ in output.items():
            pass 
        pprint("--------------------")
    if not state["aggregated_context"]:
        state["aggregated_context"] = ""
    state["aggregated_context"] += output['relevant_context']
    return state

def run_qualitative_summaries_retrieval_workflow(state):
    """
    Run the qualitative summaries retrieval workflow.
    Args:
        state: The current state of the plan execution.
    Returns:
        The state with the updated aggregated context.
    """
    state["curr_state"] = "retrieve_summaries"
    print("Running the qualitative summaries retrieval workflow...")
    question = state["query_to_retrieve_or_answer"]
    inputs = {"question": question}
    for output in qualitative_summaries_retrieval_workflow_app.stream(inputs):
        for _, _ in output.items():
            pass 
        pprint("--------------------")
    if not state["aggregated_context"]:
        state["aggregated_context"] = ""
    state["aggregated_context"] += output['relevant_context']
    return state

def run_qualitative_book_quotes_retrieval_workflow(state):
    """
    Run the qualitative book quotes retrieval workflow.
    Args:
        state: The current state of the plan execution.
    Returns:
        The state with the updated aggregated context.
    """
    state["curr_state"] = "retrieve_book_quotes"
    print("Running the qualitative book quotes retrieval workflow...")
    question = state["query_to_retrieve_or_answer"]
    inputs = {"question": question}
    for output in qualitative_book_quotes_retrieval_workflow_app.stream(inputs):
        for _, _ in output.items():
            pass 
        pprint("--------------------")
    if not state["aggregated_context"]:
        state["aggregated_context"] = ""
    state["aggregated_context"] += output['relevant_context']
    return state
   


def run_qualtative_answer_workflow(state):
    """
    Run the qualitative answer workflow.
    Args:
        state: The current state of the plan execution.
    Returns:
        The state with the updated aggregated context.
    """
    state["curr_state"] = "answer"
    print("Running the qualitative answer workflow...")
    question = state["query_to_retrieve_or_answer"]
    context = state["curr_context"]
    inputs = {"question": question, "context": context}
    for output in qualitative_answer_workflow_app.stream(inputs):
        for _, _ in output.items():
            pass 
        pprint("--------------------")
    if not state["aggregated_context"]:
        state["aggregated_context"] = ""
    state["aggregated_context"] += output["answer"]
    return state

def run_qualtative_answer_workflow_for_final_answer(state):
    """
    Run the qualitative answer workflow for the final answer.
    Args:
        state: The current state of the plan execution.
    Returns:
        The state with the updated response.
    """
    state["curr_state"] = "get_final_answer"
    print("Running the qualitative answer workflow for final answer...")
    question = state["question"]
    context = state["aggregated_context"]
    inputs = {"question": question, "context": context}
    for output in qualitative_answer_workflow_app.stream(inputs):
        for _, value in output.items():
            pass  
        pprint("--------------------")
    state["response"] = value
    return state


def anonymize_queries(state: PlanExecute):
    """
    Anonymizes the question.
    Args:
        state: The current state of the plan execution.
    Returns:
        The updated state with the anonymized question and mapping.
    """
    state["curr_state"] = "anonymize_question"
    print("state['question']: ", state['question'])
    print("Anonymizing question")
    pprint("--------------------")
    input_values = {"question": state['question']}
    anonymized_question_output = anonymize_question_chain.invoke(input_values)
    print(f'anonymized_question_output: {anonymized_question_output}')
    anonymized_question = anonymized_question_output["anonymized_question"]
    print(f'anonimized_querry: {anonymized_question}')
    pprint("--------------------")
    mapping = anonymized_question_output["mapping"]
    state["anonymized_question"] = anonymized_question
    state["mapping"] = mapping
    return state


def deanonymize_queries(state: PlanExecute):
    """
    De-anonymizes the plan.
    Args:
        state: The current state of the plan execution.
    Returns:
        The updated state with the de-anonymized plan.
    """
    state["curr_state"] = "de_anonymize_plan"
    print("De-anonymizing plan")
    pprint("--------------------")
    deanonimzed_plan = de_anonymize_plan_chain.invoke({"plan": state["plan"], "mapping": state["mapping"]})
    state["plan"] = deanonimzed_plan.plan
    print(f'de-anonimized_plan: {deanonimzed_plan.plan}')
    return state


def plan_step(state: PlanExecute):
    """
    Plans the next step.
    Args:
        state: The current state of the plan execution.
    Returns:
        The updated state with the plan.
    """
    state["curr_state"] = "planner"
    print("Planning step")
    pprint("--------------------")
    plan = planner.invoke({"question": state['anonymized_question']})
    state["plan"] = plan.steps
    print(f'plan: {state["plan"]}')
    return state


def break_down_plan_step(state: PlanExecute):
    """
    Breaks down the plan steps into retrievable or answerable tasks.
    Args:
        state: The current state of the plan execution.
    Returns:
        The updated state with the refined plan.
    """
    state["curr_state"] = "break_down_plan"
    print("Breaking down plan steps into retrievable or answerable tasks")
    pprint("--------------------")
    refined_plan = break_down_plan_chain.invoke(state["plan"])
    state["plan"] = refined_plan.steps
    return state



def replan_step(state: PlanExecute):
    """
    Replans the next step. Increments replan_count for graceful degradation.
    """
    state["curr_state"] = "replan"
    state["replan_count"] = (state.get("replan_count") or 0) + 1
    print(f"Replanning step (attempt {state['replan_count']}/{MAX_REPLAN_RETRIES})")
    pprint("--------------------")
    inputs = {"question": state["question"], "plan": state["plan"], "past_steps": state["past_steps"], "aggregated_context": state["aggregated_context"]}
    plan = replanner.invoke(inputs)
    state["plan"] = plan.steps
    return state


def can_be_answered(state: PlanExecute):
    """
    Determines if the question can be answered.
    Implements Graceful Degradation: after MAX_REPLAN_RETRIES attempts,
    forces a best-effort answer instead of continuing the loop.
    """
    state["curr_state"] = "can_be_answered_already"
    replan_count = state.get("replan_count") or 0

    # Graceful Degradation: 超过最大重试次数，强制生成兜底回答
    if replan_count >= MAX_REPLAN_RETRIES:
        print(f"[Graceful Degradation] Reached max replan retries ({MAX_REPLAN_RETRIES}). "
              f"Forcing best-effort answer with available context.")
        pprint("--------------------")
        ctx = state.get("aggregated_context", "")
        if not ctx.strip():
            state["aggregated_context"] = (
                f"[系统提示] 经过 {replan_count} 轮检索，未能找到足够的相关信息来完整回答该问题。"
                f"请用户确认该信息是否包含在 10-K 年报的其他章节中。"
            )
        return "can_be_answered_already"

    print("Checking if the ORIGINAL QUESTION can be answered already")
    pprint("--------------------")
    question = state["question"]
    context = state["aggregated_context"]
    inputs = {"question": question, "context": context}
    output = can_be_answered_already_chain.invoke(inputs)
    if output.can_be_answered == True:
        print("The ORIGINAL QUESTION can be fully answered already.")
        pprint("--------------------")
        print("the aggregated context is:")
        print(text_wrap(state["aggregated_context"]))
        print("--------------------")
        return "can_be_answered_already"
    else:
        print("The ORIGINAL QUESTION cannot be fully answered yet.")
        pprint("--------------------")
        return "cannot_be_answered_yet"



def create_agent():
    
    agent_workflow = StateGraph(PlanExecute)

    # Add the anonymize node
    agent_workflow.add_node("anonymize_question", anonymize_queries)

    # Add the plan node
    agent_workflow.add_node("planner", plan_step)

    # Add the break down plan node

    agent_workflow.add_node("break_down_plan", break_down_plan_step)

    # Add the deanonymize node
    agent_workflow.add_node("de_anonymize_plan", deanonymize_queries)

    # Add the qualitative chunks retrieval node
    agent_workflow.add_node("retrieve_chunks", run_qualitative_chunks_retrieval_workflow)

    # Add the qualitative summaries retrieval node
    agent_workflow.add_node("retrieve_summaries", run_qualitative_summaries_retrieval_workflow)

    # Add the qualitative book quotes retrieval node
    agent_workflow.add_node("retrieve_book_quotes", run_qualitative_book_quotes_retrieval_workflow)


    # Add the qualitative answer node
    agent_workflow.add_node("answer", run_qualtative_answer_workflow)

    # Add the task handler node
    agent_workflow.add_node("task_handler", run_task_handler_chain)

    # Add a replan node
    agent_workflow.add_node("replan", replan_step)

    # Add answer from context node
    agent_workflow.add_node("get_final_answer", run_qualtative_answer_workflow_for_final_answer)

    # Set the entry point
    agent_workflow.set_entry_point("anonymize_question")

    # From anonymize we go to plan
    agent_workflow.add_edge("anonymize_question", "planner")

    # From plan we go to deanonymize
    agent_workflow.add_edge("planner", "de_anonymize_plan")

    # From deanonymize we go to break down plan

    agent_workflow.add_edge("de_anonymize_plan", "break_down_plan")

    # From break_down_plan we go to task handler
    agent_workflow.add_edge("break_down_plan", "task_handler")

    # From task handler we go to either retrieve or answer
    agent_workflow.add_conditional_edges("task_handler", retrieve_or_answer, {"chosen_tool_is_retrieve_chunks": "retrieve_chunks", "chosen_tool_is_retrieve_summaries":
                                                                            "retrieve_summaries", "chosen_tool_is_retrieve_quotes": "retrieve_book_quotes", "chosen_tool_is_answer": "answer"})

    # After retrieving we go to replan
    agent_workflow.add_edge("retrieve_chunks", "replan")

    agent_workflow.add_edge("retrieve_summaries", "replan")

    agent_workflow.add_edge("retrieve_book_quotes", "replan")

    # After answering we go to replan
    agent_workflow.add_edge("answer", "replan")

    # After replanning we check if the question can be answered, if yes we go to get_final_answer, if not we go to task_handler
    agent_workflow.add_conditional_edges("replan",can_be_answered, {"can_be_answered_already": "get_final_answer", "cannot_be_answered_yet": "break_down_plan"})

    # After getting the final answer we end
    agent_workflow.add_edge("get_final_answer", END)


    plan_and_execute_app = agent_workflow.compile()

    return plan_and_execute_app