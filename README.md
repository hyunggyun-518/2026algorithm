# 가중치 격자 최단경로 탐색 비교

2026-2 고급알고리즘 개인프로젝트. 같은 가중치 격자에서 Dijkstra, A*, 양방향 Dijkstra의 최적 경로와 탐색 비용을 비교한다.

현재는 **2단계: Dijkstra 기준선 만들기**까지 진행했다. A*·양방향 Dijkstra와 성능 실험 결과는 아직 구현·생성하지 않았다.

## 실행 환경

Python 3와 표준 라이브러리만 사용한다. 이 저장소는 교수님의 `algorithm-env`를 `Use this template`으로 복제해 만들었다. 기존 `src/`와 정렬 테스트는 실습 환경 확인용 예제로 그대로 보존한다. 프로젝트 구현은 `pathfinding/`에, 프로젝트 테스트와 독립 검증기는 `tests/`에 둔다.

전체 테스트:

```sh
make test
```

2단계 프로젝트 테스트만 실행:

```sh
python3 -m unittest tests.test_grid tests.test_dijkstra -v
```

Dijkstra 예제 실행:

```sh
python3 -m pathfinding
```

예제의 최적 비용은 `6`이고, 출발점 `(0, 0)`에서 아래쪽 통로를 거쳐 목표점 `(0, 2)`에 도달한다. 구현은 진입 비용이 낮은 우회 경로를 복원한다. 작은 무작위 지도 100개는 별도 Bellman–Ford 구현으로 비용을 대조한다. 3~4단계에서 나머지 탐색 알고리즘을 추가한다. 성능 실험 전에는 방식 간 우위를 주장하지 않는다.

## 문서

- [문제 정의와 공정 비교 규칙](docs/PROJECT_SPEC.md)
- [단계별 작업 계획](docs/WORK_PLAN.md)

## 제출 예정물

세 알고리즘의 실행 코드와 테스트, 입력 생성 설정·시드·원시 CSV, 분석용 표와 그래프, 5~20쪽 PDF 보고서, 이 공개 저장소 URL과 ZIP을 제출한다. 실제 제출물은 각 단계가 끝날 때 추가한다.

## 출처

- [고급알고리즘 개인프로젝트 안내](https://lec-algorithm.github.io/lecture/article/project-2026/)
- [강의 실습 환경 템플릿](https://github.com/lec-algorithm/algorithm-env)
