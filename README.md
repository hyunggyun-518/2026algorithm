# 가중치 격자 최단경로 탐색 비교

2026-2 고급알고리즘 개인프로젝트. 같은 가중치 격자에서 Dijkstra, A*, 양방향 Dijkstra의 최적 경로와 탐색 비용을 비교한다.

현재는 **3단계: A* 만들기**까지 진행했다. 양방향 Dijkstra와 성능 실험 결과는 아직 구현·생성하지 않았다.

## 실행 환경

Python 3와 표준 라이브러리만 사용한다. 이 저장소는 교수님의 `algorithm-env`를 `Use this template`으로 복제해 만들었다. 기존 `src/`와 정렬 테스트는 실습 환경 확인용 예제로 그대로 보존한다. 프로젝트 구현은 `pathfinding/`에, 프로젝트 테스트와 독립 검증기는 `tests/`에 둔다.

전체 테스트:

```sh
make test
```

프로젝트 테스트만 실행:

```sh
python3 -m unittest tests.test_grid tests.test_dijkstra tests.test_astar -v
```

Dijkstra와 A* 예제 실행:

```sh
python3 -m pathfinding
```

예제에서 두 방법의 최적 비용은 모두 `6`이고, 출발점 `(0, 0)`에서 아래쪽 통로를 거쳐 목표점 `(0, 2)`에 도달한다. A*는 목표까지의 맨해튼 거리와 지도의 최소 진입 비용으로 남은 비용의 하한을 계산한다. 작은 무작위 지도 120개에서 A* 비용을 Dijkstra 및 별도 Bellman–Ford 구현과 대조하고, 추가 지도 40개에서 휴리스틱의 허용성과 일관성을 검사한다. 4단계에서 양방향 탐색을 추가한다. 성능 실험 전에는 방식 간 우위를 주장하지 않는다.

## 문서

- [문제 정의와 공정 비교 규칙](docs/PROJECT_SPEC.md)
- [단계별 작업 계획](docs/WORK_PLAN.md)

## 제출 예정물

세 알고리즘의 실행 코드와 테스트, 입력 생성 설정·시드·원시 CSV, 분석용 표와 그래프, 5~20쪽 PDF 보고서, 이 공개 저장소 URL과 ZIP을 제출한다. 실제 제출물은 각 단계가 끝날 때 추가한다.

## 출처

- [고급알고리즘 개인프로젝트 안내](https://lec-algorithm.github.io/lecture/article/project-2026/)
- [강의 실습 환경 템플릿](https://github.com/lec-algorithm/algorithm-env)
