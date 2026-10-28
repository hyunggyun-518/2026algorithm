# 가중치 격자 최단경로 탐색 비교

2026-2 고급알고리즘 개인프로젝트. 같은 가중치 격자에서 Dijkstra, A*, 양방향 Dijkstra의 최적 경로와 탐색 비용을 비교한다.

현재는 **4단계: 양방향 탐색 만들기**까지 진행했다. 세 탐색 방법의 정확성 검사를 마쳤고, 비교용 지도 생성과 성능 실험은 아직 진행하지 않았다.

## 실행 환경

Python 3와 표준 라이브러리만 사용한다. 이 저장소는 교수님의 `algorithm-env`를 `Use this template`으로 복제해 만들었다. 기존 `src/`와 정렬 테스트는 실습 환경 확인용 예제로 그대로 보존한다. 프로젝트 구현은 `pathfinding/`에, 프로젝트 테스트와 독립 검증기는 `tests/`에 둔다.

전체 테스트:

```sh
make test
```

프로젝트 테스트만 실행:

```sh
python3 -m unittest tests.test_grid tests.test_dijkstra tests.test_astar tests.test_bidirectional -v
```

세 탐색 방법의 예제 실행:

```sh
python3 -m pathfinding
```

예제에서 세 방법의 최적 비용은 모두 `6`이고, 출발점 `(0, 0)`에서 아래쪽 통로를 거쳐 목표점 `(0, 2)`에 도달한다. A*는 목표까지의 맨해튼 거리와 지도의 최소 진입 비용으로 남은 비용의 하한을 계산한다. 양방향 Dijkstra는 반대쪽에서의 거리도 계산하고, 첫 접촉이 아닌 안전한 종료 조건을 사용한다. 작은 격자 324개를 빠짐없이, 무작위 가중치 격자 300개를 별도로 검사해 세 방식의 최적 비용과 경로 유효성을 확인했다. 각 방식의 성능 우위는 다음 단계에서 지도와 측정 규칙을 고정한 뒤 평가한다.

## 문서

- [문제 정의와 공정 비교 규칙](docs/PROJECT_SPEC.md)
- [단계별 작업 계획](docs/WORK_PLAN.md)

## 제출 예정물

세 알고리즘의 실행 코드와 테스트, 입력 생성 설정·시드·원시 CSV, 분석용 표와 그래프, 5~20쪽 PDF 보고서, 이 공개 저장소 URL과 ZIP을 제출한다. 실제 제출물은 각 단계가 끝날 때 추가한다.

## 출처

- [고급알고리즘 개인프로젝트 안내](https://lec-algorithm.github.io/lecture/article/project-2026/)
- [강의 실습 환경 템플릿](https://github.com/lec-algorithm/algorithm-env)
