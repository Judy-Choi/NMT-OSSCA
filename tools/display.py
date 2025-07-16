import re
from pathlib import Path
import streamlit as st

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

def display_translation_results(source_chunks, target_chunks, source_terms, target_terms, result_title, save_path):
    """번역 결과를 표시하고 편집할 수 있는 공통 함수"""
    # 각 청크의 수정 상태 초기화
    for i in range(len(source_chunks)):
        if f"editing_chunk_{i}" not in st.session_state:
            st.session_state[f"editing_chunk_{i}"] = False
        # target_chunks에서 해당 청크를 edited_chunk로 초기화
        if f"edited_chunk_{i}" not in st.session_state and i < len(target_chunks):
            st.session_state[f"edited_chunk_{i}"] = target_chunks[i]

    for i, source_chunk in enumerate(source_chunks):
        st.subheader(f"문단 {i+1}/{len(source_chunks)}")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 원본")
            highlighted_source = highlight_terms(source_chunk, source_terms)
            with st.container(border=True):
                st.markdown(highlighted_source, unsafe_allow_html=True)
        
        with col2:
            is_editing = st.session_state.get(f"editing_chunk_{i}", False)
            
            title_col, button_col = st.columns([0.8, 0.2])

            with title_col:
                st.markdown(f"### {result_title}")

            if is_editing:
                # 수정 모드
                with button_col:
                    if st.button("완료", key=f"done_button_{i}", use_container_width=True):
                        # 수정된 내용을 저장하고 수정 모드 종료
                        edited_content = st.session_state.get(f"temp_edit_{i}", "")
                        st.session_state[f"edited_chunk_{i}"] = edited_content
                        st.session_state[f"editing_chunk_{i}"] = False
                        # 임시 수정 키 삭제
                        if f"temp_edit_{i}" in st.session_state:
                            del st.session_state[f"temp_edit_{i}"]
                        st.rerun()
                
                # 수정용 임시 키 초기화 (수정 모드 시작 시에만)
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
                    if st.button("수정", key=f"edit_button_{i}", use_container_width=True):
                        st.session_state[f"editing_chunk_{i}"] = True
                        st.rerun()

                with st.container(border=True):
                    translated_text = st.session_state.get(f"edited_chunk_{i}", "")
                    highlighted_target = highlight_terms(translated_text, target_terms)
                    st.markdown(highlighted_target, unsafe_allow_html=True)

    # Change the output path for the '수정된 내용 파일에 저장' button
    if st.button("수정된 내용 파일에 저장", type="primary"):
        final_chunks = []
        for i in range(len(source_chunks)):
            edited_content = st.session_state.get(f"edited_chunk_{i}", "")
            final_chunks.append(edited_content)
        
        final_content = "\n".join(final_chunks)
        
        output_dir = Path(save_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        st.success(f"✅ 수정된 내용이 다음 파일에 저장되었습니다: {save_path}") 