import json
from pathlib import Path
import streamlit as st
from tools.display import display_translation_results

@st.cache_data
def load_prompt_template(prompt_path: str) -> str:
    """프롬프트 템플릿을 로드하고 캐시합니다."""
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()

@st.cache_data
def load_glossary(_glossary_path: str) -> list:
    """단어사전 파일을 로드하고 캐시합니다."""
    with open(_glossary_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_glossary_terms(glossary_data: list) -> tuple[list, list]:
    """단어사전에서 원문/번역문 용어 리스트를 추출합니다."""
    source_terms = [entry["source"] for entry in glossary_data]
    target_terms = []
    for entry in glossary_data:
        target = entry["target"]  # 항상 리스트
        target_terms.extend(target)
    return source_terms, target_terms

def prepare_final_prompt(base_prompt: str, glossary_data: list) -> str:
    """프롬프트 템플릿에 단어사전 규칙을 결합합니다."""
    instructions = []
    for entry in glossary_data:
        source = entry["source"]
        target = entry["target"]  # 항상 리스트
        target_str = json.dumps(target, ensure_ascii=False)
        instructions.append(f'- "{source}" → {target_str}')
    glossary_instructions = "\n".join(instructions)
    return base_prompt.replace("{glossary_instructions}", glossary_instructions)

def split_markdown_by_headings(markdown_content: str) -> list[str]:
    """마크다운 콘텐츠를 제목(#) 기준으로 분할하되, 코드 블록 내의 주석은 제외합니다."""
    chunks = []
    current_chunk_lines = []
    in_code_block = False
    for line in markdown_content.splitlines():
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
        
        if line.startswith('#') and not in_code_block:
            if current_chunk_lines:
                chunks.append("\n".join(current_chunk_lines))
            current_chunk_lines = [line]
        else:
            current_chunk_lines.append(line)
    if current_chunk_lines:
        chunks.append("\n".join(current_chunk_lines))
    return chunks

def load_and_display_existing_translation(file_path, source_path, glossary_path, result_title, save_path):
    """기존 번역 파일을 로드하고 표시하는 공통 함수"""
    try:
        # 원본 문서 로드 및 분할
        with open(source_path, 'r', encoding='utf-8') as f:
            source_content = f.read()
        
        source_chunks = split_markdown_by_headings(source_content)
        st.session_state.source_chunks = source_chunks
        
        # 번역 파일 로드 및 분할
        with open(file_path, 'r', encoding='utf-8') as f:
            target_content = f.read()
        
        target_chunks = split_markdown_by_headings(target_content)
        st.session_state.target_chunks = target_chunks
        
        st.info(f"✅ 총 {len(source_chunks)}개의 문단으로 나누어 번역했습니다.")

        source_chunks = st.session_state.source_chunks
        target_chunks = st.session_state.target_chunks
        glossary_data = load_glossary(glossary_path)
        source_terms, target_terms = get_glossary_terms(glossary_data)

        display_translation_results(source_chunks, target_chunks, source_terms, target_terms, result_title, save_path)

    except Exception as e:
        st.error(f"결과를 표시하는 중 오류가 발생했습니다: {e}") 