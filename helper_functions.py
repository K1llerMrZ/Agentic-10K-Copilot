import tiktoken
import re 
from langchain.docstore.document import Document
import PyPDF2
import pylcs
import pandas as pd
import textwrap




def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """
    Calculates the number of tokens in a given string using a specified encoding.

    Args:
        string: The input string to tokenize.
        encoding_name: The name of the encoding to use (e.g., 'cl100k_base').

    Returns:
        The number of tokens in the string according to the specified encoding.
    """
    try:
        encoding = tiktoken.encoding_for_model(encoding_name)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string))
    return num_tokens


def replace_t_with_space(list_of_documents):
    """
    Replaces all tab characters ('\t') with spaces in the page content of each document.

    Args:
        list_of_documents: A list of document objects, each with a 'page_content' attribute.

    Returns:
        The modified list of documents with tab characters replaced by spaces.
    """

    for doc in list_of_documents:
        doc.page_content = doc.page_content.replace('\t', ' ')  # Replace tabs with spaces
    return list_of_documents

def replace_double_lines_with_one_line(text):
    """
    Replaces consecutive double newline characters ('\n\n') with a single newline character ('\n').

    Args:
        text: The input text string.

    Returns:
        The text string with double newlines replaced by single newlines.
    """

    cleaned_text = re.sub(r'\n\n', '\n', text)  # Replace double newlines with single newlines
    return cleaned_text


def split_into_chapters(book_path):
    """
    Splits a 10-K filing PDF into sections based on 'Item X.' headers.

    Args:
        book_path (str): The path to the 10-K PDF file.

    Returns:
        list: A list of Document objects, each representing a section with its text content and section metadata.
    """

    with open(book_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = " ".join([page.extract_text() for page in pdf_reader.pages])

    # Match 10-K section headers like "Item 1.", "Item 1A.", "Item 7.", "Item 9C."
    header_pattern = re.compile(r'(Item\s+\d+[A-C]?)\.\s', re.IGNORECASE)

    matches = list(header_pattern.finditer(text))

    if not matches:
        # Fallback: treat whole document as one section
        return [Document(page_content=text, metadata={"chapter": 1, "title": "Full Document"})]

    # Deduplicate: keep only the LAST occurrence of each Item
    # (table of contents entries come first; actual sections come later)
    seen = {}
    for match in matches:
        key = re.sub(r'\s+', ' ', match.group(1)).strip().lower()
        seen[key] = match
    unique_matches = sorted(seen.values(), key=lambda m: m.start())

    chapter_docs = []
    for i, match in enumerate(unique_matches):
        start = match.start()
        end = unique_matches[i + 1].start() if i + 1 < len(unique_matches) else len(text)
        chapter_text = text[start:end].strip()
        title = re.sub(r'\s+', ' ', match.group(1)).strip()
        doc = Document(page_content=chapter_text, metadata={"chapter": i + 1, "title": title})
        chapter_docs.append(doc)

    return chapter_docs


import re
from langchain.schema import Document

def extract_book_quotes_as_documents(documents, min_length=30):
    """
    针对财报场景重写：提取包含核心财务数据（如营收、利润、百分比、美元）的句子
    为了尽量不改动主干代码，我们保留原函数名，但里面执行的是“财务数据提取”逻辑
    """
    quotes_as_documents = []
    
    # 定义我们要重点抓取的财务关键词
    financial_keywords = ['revenue', 'sales', 'income', 'margin', 'profit', 'cash flow', 'eps', 'dividend', 'decrease', 'increase']

    for doc in documents:
        content = doc.page_content
        # 把换行符替换为空格，避免句子被切断
        content = content.replace('\n', ' ')
        
        # 按照句号进行简单的分句
        sentences = content.split('. ')
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # 规则 1：必须包含数字
            has_number = bool(re.search(r'\d', sentence))
            
            # 规则 2：必须包含美元符号 '$'、百分号 '%'，或者核心财务关键词
            has_money_or_pct = '$' in sentence or '%' in sentence
            has_keyword = any(keyword in sentence_lower for keyword in financial_keywords)
            
            # 如果句子长度达标，且满足财务数据特征，则提取出来
            if len(sentence) >= min_length and has_number and (has_money_or_pct or has_keyword):
                # 封装成 LangChain 的 Document 格式
                quote_doc = Document(page_content=sentence.strip() + '.')
                quotes_as_documents.append(quote_doc)
    
    return quotes_as_documents



def escape_quotes(text):
  """Escapes both single and double quotes in a string.

  Args:
    text: The string to escape.

  Returns:
    The string with single and double quotes escaped.
  """
  return text.replace('"', '\\"').replace("'", "\\'")



def text_wrap(text, width=120):
    """
    Wraps the input text to the specified width.

    Args:
        text (str): The input text to wrap.
        width (int): The width at which to wrap the text.

    Returns:
        str: The wrapped text.
    """
    return textwrap.fill(text, width=width)


def is_similarity_ratio_lower_than_th(large_string, short_string, th):
    """
    Checks if the similarity ratio between two strings is lower than a given threshold.

    Args:
        large_string: The larger string to compare.
        short_string: The shorter string to compare.
        th: The similarity threshold.

    Returns:
        True if the similarity ratio is lower than the threshold, False otherwise.
    """

    # Calculate the length of the longest common subsequence (LCS)
    lcs = pylcs.lcs_sequence_length(large_string, short_string)

    # Calculate the similarity ratio
    similarity_ratio = lcs / len(short_string)

    # Check if the similarity ratio is lower than the threshold
    if similarity_ratio < th:
        return True
    else:
        return False
    

def analyse_metric_results(results_df):
    """
    Analyzes and prints the results of various metrics.

    Args:
        results_df: A pandas DataFrame containing the metric results.
    """

    for metric_name, metric_value in results_df.items():
        print(f"\n**{metric_name.upper()}**")

        # Extract the numerical value from the Series object
        if isinstance(metric_value, pd.Series):
            metric_value = metric_value.values[0]  # Assuming the value is at index 0

        # Print explanation and score for each metric
        if metric_name == "faithfulness":
            print("Measures how well the generated answer is supported by the retrieved documents.")
            print(f"Score: {metric_value:.4f}")
            # Interpretation: Higher score indicates better faithfulness.
        elif metric_name == "answer_relevancy":
            print("Measures how relevant the generated answer is to the question.")
            print(f"Score: {metric_value:.4f}")
            # Interpretation: Higher score indicates better relevance.
        elif metric_name == "context_precision":
            print("Measures the proportion of retrieved documents that are actually relevant.")
            print(f"Score: {metric_value:.4f}")
            # Interpretation: Higher score indicates better precision (avoiding irrelevant documents).
        elif metric_name == "context_relevancy":
            print("Measures how relevant the retrieved documents are to the question.")
            print(f"Score: {metric_value:.4f}")
            # Interpretation: Higher score indicates better relevance of retrieved documents.
        elif metric_name == "context_recall":
            print("Measures the proportion of relevant documents that are successfully retrieved.")
            print(f"Score: {metric_value:.4f}")
            # Interpretation: Higher score indicates better recall (finding all relevant documents).
        elif metric_name == "context_entity_recall":
            print("Measures the proportion of relevant entities mentioned in the question that are also found in the retrieved documents.")
            print(f"Score: {metric_value:.4f}")
            # Interpretation: Higher score indicates better recall of relevant entities.
        elif metric_name == "answer_similarity":
            print("Measures the semantic similarity between the generated answer and the ground truth answer.")
            print(f"Score: {metric_value:.4f}")
            # Interpretation: Higher score indicates closer semantic meaning between the answers.
        elif metric_name == "answer_correctness":
            print("Measures whether the generated answer is factually correct.")
            print(f"Score: {metric_value:.4f}")
            # Interpretation: Higher score indicates better correctness.



import dill

def save_object(obj, filename):
    """
    Save a Python object to a file using dill.
    
    Args:
    - obj: The Python object to save.
    - filename: The name of the file where the object will be saved.
    """
    with open(filename, 'wb') as file:
        dill.dump(obj, file)
    print(f"Object has been saved to '{filename}'.")

def load_object(filename):
    """
    Load a Python object from a file using dill.
    
    Args:
    - filename: The name of the file from which the object will be loaded.
    
    Returns:
    - The loaded Python object.
    """
    with open(filename, 'rb') as file:
        obj = dill.load(file)
    print(f"Object has been loaded from '{filename}'.")
    return obj

# Example usage:
# save_object(plan_and_execute_app, 'plan_and_execute_app.pkl')
# plan_and_execute_app = load_object('plan_and_execute_app.pkl')

