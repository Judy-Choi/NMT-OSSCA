#!/usr/bin/env python3
"""
Streamlit 기반의 대화형 문서 번역기
"""
import json
import os
import re
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# --- Core Logic Functions ---

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

def highlight_terms(text: str, terms: list) -> str:
    """주어진 텍스트에서 용어들을 찾아 볼드 처리하고 파란색으로 강조하되, 코드 블록과 인라인 코드는 제외합니다."""
    if not terms:
        return text

    # 긴 용어를 먼저 처리하기 위해 길이를 기준으로 내림차순 정렬
    sorted_terms = sorted(terms, key=len, reverse=True)
    
    # 코드 블록, 인라인 코드, 또는 강조할 용어를 찾는 정규식
    # 1. 코드 블록 (```...```)
    # 2. 인라인 코드 (`...`)
    # 3. 강조할 용어들
    term_pattern = '|'.join(re.escape(term) for term in sorted_terms)
    pattern = re.compile(
        rf"(```.*?```|`.*?`|{term_pattern})", 
        re.DOTALL | re.IGNORECASE
    )

    def replace_match(match):
        matched_text = match.group(0)
        # 코드 블록이나 인라인 코드인 경우, 그대로 반환
        if matched_text.startswith('`'):
            return matched_text
        # 용어인 경우, 볼드 처리하고 파란색으로 강조하여 반환
        return f'<span style="color: blue; font-weight: bold;">{matched_text}</span>'

    return pattern.sub(replace_match, text)

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

# --- Streamlit UI ---

st.set_page_config(layout="wide", page_title="AI 문서 번역기")
st.title("🤗 AI 문서 번역기")

# --- Initialize session state ---
if "translation_done" not in st.session_state:
    st.session_state.translation_done = False
if "source_chunks" not in st.session_state:
    st.session_state.source_chunks = []
if "show_progress_view" not in st.session_state:
    st.session_state.show_progress_view = False

# --- Sidebar for Settings ---
with st.sidebar:
    st.header("⚙️ 번역 설정")
    
    # .env 파일 로드
    load_dotenv()
    
    api_key = st.text_input(
        "OpenAI API Key", 
        value=os.getenv("OPENAI_API_KEY", ""), 
        type="password",
        help="API 키가 없으면 https://platform.openai.com/api-keys 에서 발급받으세요."
    )
    
    model_name = st.text_input("모델 이름", value="gpt-4o")
    
    st.subheader("파일 경로")
    source_path = st.text_input("원본 문서", value="./source_docs/models.md")
    prompt_path = st.text_input("프롬프트 템플릿", value="./prompts/nmt.yaml")
    glossary_path = st.text_input("단어사전", value="./glossary/glossary.json")
    output_path = st.text_input("번역 결과 저장 경로", value="./output/models_ko.md")

    if st.button("번역 시작", type="primary"):
        st.session_state.show_progress_view = True
        st.session_state.translation_done = False
        st.rerun()

# --- Main App Logic ---
if st.session_state.show_progress_view:
    st.session_state.show_progress_view = False  # 한번만 실행되도록 재설정

    if not api_key:
        st.error("OpenAI API 키를 입력해주세요.")
    elif not all([source_path, prompt_path, glossary_path, output_path]):
        st.error("모든 파일 경로를 올바르게 입력해주세요.")
    else:
        try:
            # 1. 초기화
            llm = ChatOpenAI(model=model_name, temperature=0.1, openai_api_key=api_key)
            base_prompt = load_prompt_template(prompt_path)
            glossary_data = load_glossary(glossary_path)
            final_prompt_template = prepare_final_prompt(base_prompt, glossary_data)
            source_terms, target_terms = get_glossary_terms(glossary_data)

            # 2. 원본 문서 로드 및 분할
            with open(source_path, 'r', encoding='utf-8') as f:
                source_content = f.read()
            
            source_chunks = split_markdown_by_headings(source_content)
            st.session_state.source_chunks = source_chunks
            
            st.info(f"✅ 총 {len(source_chunks)}개의 문단으로 나누어 번역을 시작합니다.")

            # 3. 실시간 스트리밍 번역 및 결과 표시
            for i, chunk in enumerate(source_chunks):
                st.subheader(f"문단 {i+1}/{len(source_chunks)}")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 원본")
                    highlighted_source = highlight_terms(chunk, source_terms)
                    with st.container(border=True):
                        st.markdown(highlighted_source, unsafe_allow_html=True)

                with col2:
                    st.markdown("### 번역 결과")
                    with st.container(border=True):
                        if not chunk.strip():
                            final_chunk = chunk
                            st.markdown(final_chunk)
                        else:
                            prompt = final_prompt_template.replace("{source}", chunk)
                            
                            placeholder = st.empty()
                            final_chunk = ""
                            try:
                                for response in llm.stream(prompt):
                                    content = response.content
                                    if content:
                                        final_chunk += content
                                        placeholder.markdown(final_chunk + "▌") # 실시간 커서 효과
                                
                                # 후처리: 한 줄짜리 코드 블록을 인라인 코드로 변경
                                stripped_chunk = final_chunk.strip()
                                lines = stripped_chunk.splitlines()
                                if (
                                    stripped_chunk.startswith('```') and
                                    stripped_chunk.endswith('```') and
                                    lines[0].strip() == '```' and
                                    '\n' not in stripped_chunk[3:-3].strip()
                                ):
                                    inner_content = stripped_chunk[3:-3].strip()
                                    final_chunk = f"`{inner_content}`"
                                
                                # 최종 결과에 용어 강조 적용하여 표시
                                highlighted_final = highlight_terms(final_chunk, target_terms)
                                placeholder.markdown(highlighted_final, unsafe_allow_html=True)
                            except Exception as e:
                                st.error(f"스트리밍 중 오류 발생: {e}")
                                final_chunk = f"오류: {e}"

                        # 후처리: 한 줄짜리 코드 블록을 인라인 코드로 변경
                        stripped_chunk = final_chunk.strip()
                        lines = stripped_chunk.splitlines()
                        if (
                            stripped_chunk.startswith('```') and
                            stripped_chunk.endswith('```') and
                            lines[0].strip() == '```' and
                            '\n' not in stripped_chunk[3:-3].strip()
                        ):
                            inner_content = stripped_chunk[3:-3].strip()
                            final_chunk = f"`{inner_content}`"

                        st.session_state[f"edited_chunk_{i}"] = final_chunk

            st.session_state.translation_done = True
            st.success("🎉 번역이 완료되었습니다! 잠시 후 편집 모드로 전환됩니다.")
            import time
            time.sleep(2)
            st.rerun()

        except FileNotFoundError as e:
            st.error(f"파일을 찾을 수 없습니다: {e.filename}")
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

# --- Display, Edit, and Save UI ---
if st.session_state.translation_done:
    try:
        source_chunks = st.session_state.source_chunks
        glossary_data = load_glossary(glossary_path)
        source_terms, target_terms = get_glossary_terms(glossary_data)

        # 각 청크의 편집 상태 초기화
        for i in range(len(source_chunks)):
            if f"editing_chunk_{i}" not in st.session_state:
                st.session_state[f"editing_chunk_{i}"] = False

        for i, chunk in enumerate(source_chunks):
            st.subheader(f"문단 {i+1}/{len(source_chunks)}")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 원본")
                highlighted_source = highlight_terms(chunk, source_terms)
                with st.container(border=True):
                    st.markdown(highlighted_source, unsafe_allow_html=True)
            
            with col2:
                is_editing = st.session_state.get(f"editing_chunk_{i}", False)
                
                title_col, button_col = st.columns([0.8, 0.2])

                with title_col:
                    st.markdown("### 번역 결과")

                if is_editing:
                    # 편집 모드
                    with button_col:
                        if st.button("완료", key=f"done_button_{i}", use_container_width=True):
                            # 편집된 내용을 저장하고 편집 모드 종료
                            edited_content = st.session_state.get(f"temp_edit_{i}", "")
                            st.session_state[f"edited_chunk_{i}"] = edited_content
                            st.session_state[f"editing_chunk_{i}"] = False
                            # 임시 편집 키 삭제
                            if f"temp_edit_{i}" in st.session_state:
                                del st.session_state[f"temp_edit_{i}"]
                            st.rerun()
                    
                    # 편집용 임시 키 초기화 (편집 모드 시작 시에만)
                    if f"temp_edit_{i}" not in st.session_state:
                        st.session_state[f"temp_edit_{i}"] = st.session_state.get(f"edited_chunk_{i}", "")
                    
                    current_text = st.session_state.get(f"temp_edit_{i}", "")
                    height = len(current_text.splitlines()) * 25
                    st.text_area(
                        label="번역 수정",
                        value=current_text,
                        key=f"temp_edit_{i}",
                        height=max(height, 100),
                        label_visibility="collapsed"
                    )
                else:
                    # 읽기 전용 모드
                    with button_col:
                        if st.button("편집", key=f"edit_button_{i}", use_container_width=True):
                            st.session_state[f"editing_chunk_{i}"] = True
                            st.rerun()

                    with st.container(border=True):
                        translated_text = st.session_state.get(f"edited_chunk_{i}", "")
                        highlighted_target = highlight_terms(translated_text, target_terms)
                        st.markdown(highlighted_target, unsafe_allow_html=True)

        st.markdown("---")
        if st.button("수정된 내용 파일에 저장", type="primary"):
            final_chunks = []
            for i in range(len(source_chunks)):
                edited_content = st.session_state.get(f"edited_chunk_{i}", "")
                final_chunks.append(edited_content)
            
            final_content = "\n".join(final_chunks)
            
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            st.success(f"✅ 수정된 내용이 다음 파일에 저장되었습니다: {output_path}")

    except Exception as e:
        st.error(f"결과를 표시하는 중 오류가 발생했습니다: {e}") 