# 가중치 격자 최단경로 탐색 비교

2026-2 고급알고리즘 개인프로젝트. 같은 가중치 격자에서 Dijkstra, A*, 양방향 Dijkstra의 최적 경로와 탐색 비용을 비교한다.

현재는 **5단계: 비교용 지도 만들기**까지 진행했다. 세 탐색 방법과 핵심 72개 입력 사례를 준비했으며, 실행 시간 측정과 성능 비교는 아직 진행하지 않았다.

## 실행 환경

Python 3.10 이상과 표준 라이브러리만 사용한다. 이 저장소는 교수님의 `algorithm-env`를 `Use this template`으로 복제해 만들었다. 기존 `src/`와 정렬 테스트는 실습 환경 확인용 예제로 그대로 보존한다. 프로젝트 구현은 `pathfinding/`에, 프로젝트 테스트와 독립 검증기는 `tests/`에 둔다.

전체 테스트:

```sh
make test
```

프로젝트 테스트만 실행:

```sh
python3 -m unittest tests.test_grid tests.test_dijkstra tests.test_astar tests.test_bidirectional tests.test_maps -v
```

세 탐색 방법의 예제 실행:

```sh
python3 -m pathfinding
```

예제에서 세 방법의 최적 비용은 모두 `6`이고, 출발점 `(0, 0)`에서 아래쪽 통로를 거쳐 목표점 `(0, 2)`에 도달한다. A*는 목표까지의 맨해튼 거리와 지도의 최소 진입 비용으로 남은 비용의 하한을 계산한다. 양방향 Dijkstra는 반대쪽에서의 거리도 계산하고, 첫 접촉이 아닌 안전한 종료 조건을 사용한다. 작은 격자 324개를 빠짐없이, 무작위 가중치 격자 300개를 별도로 검사해 세 방식의 최적 비용과 경로 유효성을 확인했다. 방식별 성능은 6단계에서 측정 규칙을 고정한 뒤 7~8단계에서 평가한다.

핵심 사례 목록을 출력해 저장된 [CSV](data/core_manifest.csv)와 대조:

```sh
python3 -m experiments.maps manifest
```

세 유형의 작은 대표 지도를 출력:

```sh
python3 -m experiments.maps sample --size 21 --seed 0 --distance far
```

핵심 사례는 101×101, 세 지도 유형, 가까운/먼 목표, 시드 0~11의 조합이다. 같은 유형·시드의 목표 거리 두 조건은 동일한 벽과 가중치를 공유한다. 5단계 테스트는 72개 사례의 재생성과 도달 가능성, 세 방식의 최적 비용·경로 일치, 51·101·201 크기 생성, 체크인된 사례 목록의 일치를 확인한다. 측정 도구와 실험 설정의 최종 고정은 6단계에서 진행한다.

## 문서

- [문제 정의와 공정 비교 규칙](docs/PROJECT_SPEC.md)
- [지도 생성 규칙과 대표 지도](docs/MAP_DESIGN.md)
- [단계별 작업 계획](docs/WORK_PLAN.md)

## 제출 예정물

세 알고리즘의 실행 코드와 테스트, 입력 생성 설정·시드·원시 CSV, 분석용 표와 그래프, 5~20쪽 PDF 보고서, 이 공개 저장소 URL과 ZIP을 제출한다. 실제 제출물은 각 단계가 끝날 때 추가한다.

## 출처

- [고급알고리즘 개인프로젝트 안내](https://lec-algorithm.github.io/lecture/article/project-2026/)
- [강의 실습 환경 템플릿](https://github.com/lec-algorithm/algorithm-env)
