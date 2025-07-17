#!/usr/bin/env python3
"""
Streamlit 기반의 대화형 문서 번역기
"""
import os
import time
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from langchain_litellm import ChatLiteLLM
from tools.utils import (
    load_prompt_template,
    load_glossary,
    get_glossary_terms,
    prepare_final_prompt,
    split_markdown_by_headings,
    load_and_display_existing_translation
)
from tools.display import highlight_terms

# --- Streamlit UI ---

st.set_page_config(layout="wide", page_title="AI 문서 번역기", page_icon="🤗")
st.title("🤗 AI 문서 번역기")

# --- Initialize session state ---
if "translation_done" not in st.session_state:
    st.session_state.translation_done = False
if "source_chunks" not in st.session_state:
    st.session_state.source_chunks = []
if "show_progress_view" not in st.session_state:
    st.session_state.show_progress_view = False
if "mtpe_exist" not in st.session_state:
    st.session_state.mtpe_exist = False
if "mt_exist" not in st.session_state:
    st.session_state.mt_exist = False

# --- Sidebar for Settings ---
with st.sidebar:
    st.header("⚙️ 번역 설정")
    
    load_dotenv()

    # claude-opus-4-20250514, gpt-4o 등 사용 가능
    # 추후 gemini 추가 예정
    model_name = st.text_input("모델 이름", value="claude-opus-4-20250514")
    
    # Load appropriate API key based on model name
    if 'gpt' in model_name:
        api_key = os.getenv("OPENAI_API_KEY", "")
    elif 'claude' in model_name:
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
    else:
        api_key = ""  # Default to empty if no matching model name

    api_key = st.text_input(
        "API Key", 
        value=api_key, 
        type="password",
        help="API 키가 없으면 해당 플랫폼에서 발급받으세요."
    )  

    st.subheader("파일 경로")
    source_path = st.text_input("원본 문서", value="./source_docs/models.md")
    prompt_path = st.text_input("프롬프트 템플릿", value="./prompts/nmt.yaml")
    glossary_path = st.text_input("단어사전", value="./glossary/glossary.json")
    mt_path = st.text_input("번역 결과 저장 경로", value="./mt/models_ko.md")
    mtpe_path = st.text_input("번역 수정 결과 저장 경로", value="./mtpe/models_ko.md")

    if st.button("번역 시작", type="primary"):
        st.session_state.show_progress_view = True
        st.session_state.translation_done = False
        st.rerun()

# --- Main App Logic ---
if st.session_state.show_progress_view:
    st.session_state.show_progress_view = False  # 한번만 실행되도록 재설정

    if not api_key:
        st.error("API 키를 입력해주세요.")
    elif not all([source_path, prompt_path, glossary_path, mt_path]):
        st.error("모든 파일 경로를 올바르게 입력해주세요.")
    else:
        if Path(mtpe_path).exists():
            st.success(f"✅ 기계번역 사후교정 파일이 이미 존재하여 불러옵니다: {mtpe_path}")
            st.session_state.mtpe_exist = True
            time.sleep(2)
            st.rerun()

        elif Path(mt_path).exists():
            st.success(f"✅ 기계번역 결과 파일이 이미 존재하여 불러옵니다: {mt_path}")
            st.session_state.mt_exist = True
            st.session_state.mtpe_exist = False
            time.sleep(2)
            st.rerun()

        else:
            # Proceed with LLM translation as before
            try:
                # 1. 초기화
                # llm = ChatOpenAI(model=model_name, temperature=0.1, openai_api_key=api_key)
                llm = ChatLiteLLM(
                    model=model_name,
                    temperature=0.1,
                    api_key=api_key
                )
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
                                    
                                    highlighted_final = highlight_terms(final_chunk, target_terms)
                                    placeholder.markdown(highlighted_final, unsafe_allow_html=True)
                                except Exception as e:
                                    st.error(f"스트리밍 중 오류 발생: {e}")
                                    final_chunk = f"오류: {e}"

                            st.session_state[f"edited_chunk_{i}"] = final_chunk

                st.session_state.translation_done = True
                # st.success("🎉 번역이 완료되었습니다! 잠시 후 수정 모드로 전환됩니다.")

                # Save the completed translation result to mt_path
                final_chunks = []
                for i in range(len(source_chunks)):
                    edited_content = st.session_state.get(f"edited_chunk_{i}", "")
                    final_chunks.append(edited_content)
                
                final_content = "\n".join(final_chunks)
                
                output_dir = Path(mt_path).parent
                output_dir.mkdir(parents=True, exist_ok=True)
                with open(mt_path, 'w', encoding='utf-8') as f:
                    f.write(final_content)
                
                st.success(f"✅ 번역이 완료되어 다음 파일에 저장되었습니다: {mt_path}")
                st.session_state.mt_exist = True

                time.sleep(2)
                st.rerun()

            except FileNotFoundError as e:
                st.error(f"파일을 찾을 수 없습니다: {e.filename}")
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")

if st.session_state.mtpe_exist:
    load_and_display_existing_translation(source_path, mtpe_path, glossary_path, "기계번역 사후교정 결과", mtpe_path)

elif st.session_state.mt_exist:
    load_and_display_existing_translation(source_path, mt_path, glossary_path, "기계번역 결과", mtpe_path) 