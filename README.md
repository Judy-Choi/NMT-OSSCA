# 🤗 AI 기술 문서 번역기

> OpenAI API와 용어 사전(glossary)을 활용해 영어 AI 기술 문서를 정확하게 번역합니다.
> 
> Streamlit 기반 UI를 통해 번역 결과를 손쉽게 비교·수정할 수 있습니다.
<br>

<img width="1742" height="746" alt="image" src="https://github.com/user-attachments/assets/b9c28124-c878-4c7a-9195-58664d30f5e0" />



## 🚀 설치

```bash
# 의존성 설치
uv pip install -r requirements.txt
```

## 🔑 API 키 설정

OpenAI API 키가 필요합니다. [OpenAI](https://platform.openai.com/)에서 계정을 생성하고 API 키를 발급받으세요.

### 방법 1: .env 파일 사용 (권장)

`.env` 파일을 편집하여 API 키를 입력:
```bash
# .env 파일 내용
OPENAI_API_KEY=your_actual_api_key_here
```

### 방법 2: 환경변수로 설정

```bash
export OPENAI_API_KEY='your_api_key_here'
```

## 📖 사용법

### 1. Streamlit UI 실행

```bash
cd nmt_huggingface
streamlit run translator.py
```

<img width="1047" height="746" alt="image" src="https://github.com/user-attachments/assets/35e59a13-d9ed-4998-9f31-073244053ace" />


기본적으로 다음 파일들을 사용합니다:
- 원본 문서: `source_docs/models.md`
- 프롬프트: `prompts/nmt.yaml`
- 용어 사전(glossary) : `glossary/glossary.json`
- 기계번역 결과 저장 파일: `./mt/models_ko.md`
- 기계번역 사후교정 저장 파일: `./mtpe/models_ko.md`

### 2. 번역 시작
`번역 시작` 버튼을 클릭하면 원본 문서를 읽어 제목을 기준으로 문단 단위로 청킹하고, 각 문단을 순차적으로 번역합니다.

용어 사전(glossary) 에 존재하는 단어는 파란색과 bold 로 표시됩니다.

<img width="1742" height="746" alt="image" src="https://github.com/user-attachments/assets/1fe140ad-62e5-46f9-b6bd-c0934bca8268" />
<br>

번역이 모두 완료된 후 결과는 `./mt/models_ko.md` 파일에 저장됩니다.

### 3. 번역 수정
모든 문단의 번역이 완료되면 번역 결과 문단의 제목 우측마다 `수정` 버튼이 생성됩니다.

`수정` 버튼을 클릭하면 번역 결과를 수정할 수 있습니다.

<img width="1742" height="746" alt="image" src="https://github.com/user-attachments/assets/1d54832e-10e8-4530-a351-4181a43af32c" />
<br>
<br>

수정을 마치면 `완료` 버튼을 클릭해 수정한 결과를 임시 저장합니다.

<img width="1742" height="746" alt="image" src="https://github.com/user-attachments/assets/4cc42934-bf0b-42df-98a1-667f54b72c43" />



### 4. 번역 및 수정 결과 저장
번역 결과를 모두 확인하고 수정을 마쳤으면 페이지 맨 아래의 `수정된 내용 파일에 저장` 버튼을 클릭해 최종 결과물을 `./mtpe/models_ko.md` 파일에 저장합니다.

<img width="1742" height="746" alt="image" src="https://github.com/user-attachments/assets/10abd7ab-c4e4-45c1-bcb3-b5bee2abe2ed" />


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
├── mt/
│   └── models_ko.md      # 번역 결과 (생성됨)
└── mtpe/
    └── models_ko.md      # 번역 수정 결과 (생성됨)
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
