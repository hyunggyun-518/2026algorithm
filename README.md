# 가중치 격자 최단경로 탐색 비교

2026-2 고급알고리즘 개인프로젝트. 같은 가중치 격자에서 Dijkstra, A*, 양방향 Dijkstra의 최적 경로와 탐색 비용을 비교한다.

현재는 **1단계: 저장소와 문제 규칙 정하기**까지 진행했다. 세 탐색 알고리즘과 실험 결과는 아직 구현·생성하지 않았다.

## 실행 환경

Python 3와 표준 라이브러리만 사용한다. 이 저장소는 교수님의 `algorithm-env`를 `Use this template`으로 복제해 만들었다. 기존 `src/`와 정렬 테스트는 실습 환경 확인용 예제로 그대로 보존한다. 프로젝트 구현은 `pathfinding/`에, 프로젝트 테스트는 `tests/test_grid.py`부터 둔다.

전체 테스트:

```sh
make test
```

1단계 프로젝트 테스트만 실행:

```sh
python3 -m unittest tests.test_grid -v
```

2~4단계에서 탐색 알고리즘을 추가한 뒤 실행 명령을 확정한다. 실험 결과를 만들기 전에는 성능 우위를 주장하지 않는다.

## 문서

- [문제 정의와 공정 비교 규칙](docs/PROJECT_SPEC.md)
- [단계별 작업 계획](docs/WORK_PLAN.md)

## 제출 예정물

세 알고리즘의 실행 코드와 테스트, 입력 생성 설정·시드·원시 CSV, 분석용 표와 그래프, 5~20쪽 PDF 보고서, 이 공개 저장소 URL과 ZIP을 제출한다. 실제 제출물은 각 단계가 끝날 때 추가한다.

## 출처

- [고급알고리즘 개인프로젝트 안내](https://lec-algorithm.github.io/lecture/article/project-2026/)
- [강의 실습 환경 템플릿](https://github.com/lec-algorithm/algorithm-env)
