#!/usr/bin/env python3
"""
기술 문서 번역 스크립트 (LangChain & OpenAI)

사용법:
1. .env 파일에 OpenAI API 키를 설정합니다. (OPENAI_API_KEY=your_key)
2. pip install -r requirements.txt
3. python ./translator.py
"""
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

def initialize_llm(api_key: str, model_name: str) -> ChatOpenAI:
    """LLM 클라이언트를 초기화합니다."""
    return ChatOpenAI(model=model_name, temperature=0.1, openai_api_key=api_key)

def prepare_prompt_template(prompt_path: str, glossary_path: str) -> str:
    """번역 프롬프트와 단어사전을 결합하여 최종 프롬프트 템플릿을 생성합니다."""
    with open(prompt_path, 'r', encoding='utf-8') as f:
        nmt_prompt_template = f.read()
    with open(glossary_path, 'r', encoding='utf-8') as f:
        glossary_data = json.load(f)
        
    instructions = []
    for entry in glossary_data:
        source = entry["source"]
        target = entry["target"]
        if isinstance(target, list):
            target_str = json.dumps(target, ensure_ascii=False)
            instructions.append(f'- "{source}" → {target_str}')
        else:
            instructions.append(f'- "{source}" → "{target}"')
    glossary_instructions = "\n".join(instructions)
    
    return nmt_prompt_template.replace("{glossary_instructions}", glossary_instructions)

def split_markdown_by_headings(markdown_content: str) -> list[str]:
    """마크다운 콘텐츠를 제목(#) 기준으로 분할합니다."""
    chunks = []
    current_chunk_lines = []
    for line in markdown_content.splitlines():
        if line.startswith('#'):
            if current_chunk_lines:
                chunks.append("\n".join(current_chunk_lines))
            current_chunk_lines = [line]
        else:
            current_chunk_lines.append(line)
    if current_chunk_lines:
        chunks.append("\n".join(current_chunk_lines))
    return chunks

def translate_document(llm: ChatOpenAI, source_content: str, prompt_template: str) -> str:
    """문서를 청크로 나누고, 각 청크를 번역하여 최종 결과물을 반환합니다."""
    chunks = split_markdown_by_headings(source_content)
    print(f"🔪 문서를 {len(chunks)}개의 청크로 분할했습니다.")
    
    translated_chunks = []
    for i, chunk in enumerate(chunks):
        if not chunk.strip():
            translated_chunks.append(chunk)
            continue

        print(f"\n⏳ 청크 {i+1}/{len(chunks)} 번역 중...")
        prompt = prompt_template.replace("{source}", chunk)
        final_chunk = llm.invoke(prompt).content
        print(f"   => ✅ 완료")
        translated_chunks.append(final_chunk)
        
    return "\n".join(translated_chunks)

def save_result(content: str, output_path: str):
    """최종 번역 결과를 파일에 저장합니다."""
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    """스크립트의 메인 실행 함수"""
    load_dotenv(override=True)
    
    # --- 설정 ---
    source_path = "./source_docs/models.md"
    prompt_path = "./prompts/nmt.yaml"
    glossary_path = "./glossary/main.json"
    output_path = "./output/models_ko.md"
    model_name = "gpt-3.5-turbo"
    api_key = os.getenv("OPENAI_API_KEY")
    
    # --- 초기화 ---
    llm = initialize_llm(api_key, model_name)
    final_prompt_template = prepare_prompt_template(prompt_path, glossary_path)
    
    # --- 실행 ---
    with open(source_path, 'r', encoding='utf-8') as f:
        source_content = f.read()

    translated_content = translate_document(llm, source_content, final_prompt_template)

    # --- 결과 저장 ---
    save_result(translated_content, output_path)

    print(f"\n🎉 번역이 완료되었습니다!")
    print(f"   - 결과: {output_path}")


if __name__ == "__main__":
    main() 