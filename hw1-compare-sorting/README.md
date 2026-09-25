# 과제 1. Compare sorting

김형균 · 2022193003

배운 정렬: 삽입·병합 / 배우지 않은 정렬: 힙.

## 실행
C17 컴파일러와 make가 필요하다. 외부 C 라이브러리는 사용하지 않는다.

```sh
make test
make sanitize
make bench
```

- `make test`: 정확성·원소 보존·안정성 및 카운터 검사
- `make sanitize`: ASan/UBSan 검사 (지원 컴파일러 필요)
- `make bench`: 실제 실험, `data/raw.csv` 갱신
- 보고서: `output/pdf/compare-sorting.pdf`
- AI 학습 자료: `report/AI_LEARNING.md`
- 측정 조건: `report/METHOD.md`
- 실행 결과: `data/summary.csv`, `data/environment.txt`

요약 CSV·그래프·`report/RESULTS.md`는 `python3 tools/analyze.py`로 다시 만든다(표준 모듈만 사용).
`report/REPORT.md`와 `report/AI_LEARNING.md`는 직접 편집하는 원본으로, 분석 실행 시 덮어쓰지 않는다.
PDF는 `tools/render_pdf.cjs`로 Markdown과 Mermaid를 렌더링한다.
PDF 제작만을 위한 별도 환경에는 Node.js의 marked/playwright와 Mermaid 10.9.3,
Chromium 계열 브라우저가 필요하다. 정렬·테스트·측정에는 필요하지 않다.
`MERMAID_JS`에 렌더러 경로, 필요하면 `CHROME_PATH`에 브라우저 경로를 지정한다.

## 출처 및 AI 사용
교수자 예시 https://github.com/lec-algorithm/hw1-sample-2026 의 구현/측정/테스트 분리,
Record의 key/tag 안정성 검사, 실험 원본 보관 방식을 참고했다. 소스와 측정값은 새로 작성·생성했다.
AI(Codex)가 코드, 학습 설명, 테스트, 실험 분석 및 보고서 초안을 작성했다.
사용자는 최종 검수와 제출을 담당한다. 학습 자료는 실제 대화 전문을 위조하지 않는다.

## 제출
GitHub: https://github.com/hyunggyun-518/2026algorithm
최종 반영 후 GitHub의 Code > Download ZIP으로 받은 ZIP과 2~10쪽 PDF를 제출한다.
