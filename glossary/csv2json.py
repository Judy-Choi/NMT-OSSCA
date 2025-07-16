import csv
import json

data = []

with open('glossary.csv', 'r', encoding='utf-8', newline='') as f:
    reader = csv.reader(f)  # 쉼표 구분자이므로 delimiter 생략
    rows = list(reader)

# 첫 행 제거 ([CLS] classification ...)
for row in rows[1:]:
    if not row:  # 빈 줄 방지
        continue
    source = row[0].strip()
    targets = [cell.strip() for cell in row[1:] if cell.strip() != ""]
    data.append({
        "source": source,
        "target": targets
    })

# JSON 파일로 저장
with open('glossary.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
