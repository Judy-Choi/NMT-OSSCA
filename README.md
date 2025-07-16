# 기술 문서 번역기 (OpenAI)

OpenAI API를 사용하여 영어 기술 문서를 한국어로 번역하는 도구입니다.

## 🚀 설치

```bash
# 의존성 설치
uv pip install -r requirements.txt
```

## 🔑 API 키 설정

OpenAI API 키가 필요합니다. [OpenAI](https://platform.openai.com/)에서 계정을 생성하고 API 키를 발급받으세요.

### 방법 1: .env 파일 사용 (권장)

1. `.env.example` 파일을 `.env`로 복사:
```bash
cp .env.example .env
```

2. `.env` 파일을 편집하여 API 키를 입력:
```bash
# .env 파일 내용
OPENAI_API_KEY=your_actual_api_key_here
```

### 방법 2: 환경변수로 설정

```bash
export OPENAI_API_KEY='your_api_key_here'
```

## 📖 사용법

### 기본 사용법

```bash
cd nmt_huggingface
streamlit run translator.py
```

기본적으로 다음 파일들을 사용합니다:
- 원본 문서: `source_docs/models.md`
- 프롬프트: `prompts/nmt.yaml`
- 용어 사전(glossary) : `glossary/glossary.json`
- 출력 파일: `output/models_ko.md`

### 고급 사용법

Streamlit UI를 통해 파일 경로와 모델을 설정할 수 있습니다.

## 📁 프로젝트 구조

```
nmt_huggingface/
├── translator.py          # 메인 번역기 스크립트
├── requirements.txt       # Python 의존성
├── README.md             # 문서
├── .env                  # 환경변수 설정 파일 (직접 생성)
├── glossary/            # 용어집 디렉토리 (따로 제공)
│   ├── glossary.csv     # 용어집 CSV 파일
│   ├── glossary.json    # 용어집 JSON 파일
│   └── csv2json.py      # CSV를 JSON으로 변환하는 스크립트
├── prompts/
│   └── nmt.yaml          # 번역 프롬프트 템플릿 (따로 제공)
├── source_docs/
│   └── models.md         # 번역할 원본 문서
└── output/
    └── models_ko.md      # 번역 결과 (생성됨)
```

## 🔧 프롬프트 템플릿 커스터마이징

`prompts/nmt.yaml` 파일을 수정하여 번역 스타일을 조정할 수 있습니다. 템플릿에서 `{source}` 플레이스홀더가 원본 문서 내용으로 자동 치환됩니다.

## ⚠️ 주의사항

1. **API 사용량**: 긴 문서의 경우 많은 토큰을 사용할 수 있습니다. OpenAI 계정의 사용량을 모니터링하세요.

2. **네트워크 연결**: 안정적인 인터넷 연결이 필요합니다. 긴 문서의 경우 처리 시간이 오래 걸릴 수 있습니다.

3. **파일 인코딩**: 모든 파일은 UTF-8 인코딩을 사용해야 합니다.

## 💡 팁

- 대용량 문서의 경우 문서를 섹션별로 나누어 번역하는 것을 권장합니다.
- 번역 품질을 높이려면 `gpt-4o` 모델 사용을 권장합니다.
- 네트워크 문제로 실패한 경우 재시도하면 됩니다.

## 🐛 문제 해결

### API 키 관련 오류
```
❌ OpenAI API 키가 필요합니다.
```
→ `.env` 파일에 `OPENAI_API_KEY`가 올바르게 설정되었는지 확인하세요.

### 파일을 찾을 수 없음
```
❌ 원본 문서를 찾을 수 없습니다
```
→ 파일 경로가 올바른지 확인하세요.

### 네트워크 오류
```
❌ 네트워크 오류
```
→ 인터넷 연결을 확인하고 재시도하세요.

## 🙋🏻‍♀️ 지원

문제가 있거나 개선 사항이 있다면 이슈를 생성해주세요. 