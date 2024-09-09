# 백준 문제 10971: 외판원 순회 2

# itertools 모듈의 permutations 함수를 사용하기 위해 임포트
from itertools import permutations

# 표준 입력을 사용하기 위한 sys 모듈 임포트
import sys
input = sys.stdin.read

# 입력을 한 번에 읽어오기
data = input().strip().split()

# 도시의 개수 N
N = int(data[0])

# 비용 행렬 초기화
cost = []
index = 1

# 비용 행렬 생성
for i in range(N):
    cost.append(list(map(int, data[index:index + N])))
    index += N

# 최소 비용을 저장할 변수 초기화 (매우 큰 값으로 초기화)
min_cost = float('inf')

# itertools.permutations 함수를 사용하여 도시의 모든 순열 생성
all_permutations = permutations(range(N))

# 생성된 모든 순열을 순회하며 경로의 비용 계산
for perm in all_permutations:
    # 현재 순열에서 비용을 계산할 변수 초기화
    current_cost = 0
    valid_path = True  # 현재 순열이 유효한 경로인지 체크하기 위한 변수
    
    # 순열의 인접한 도시 간의 비용을 계산
    for i in range(N - 1):
        # 현재 도시에서 다음 도시로 가는 비용
        travel_cost = cost[perm[i]][perm[i + 1]]
        if travel_cost == 0:  # 만약 비용이 0이라면 유효하지 않은 경로
            valid_path = False
            break
        current_cost += travel_cost
    
    # 마지막 도시에서 시작 도시로 돌아오는 비용 추가
    return_cost = cost[perm[-1]][perm[0]]
    if return_cost == 0:  # 만약 비용이 0이라면 유효하지 않은 경로
        valid_path = False
    
    # 만약 유효한 경로라면, 마지막 도시에서 시작 도시로 돌아오는 비용을 더함
    if valid_path:
        current_cost += return_cost
        # 최소 비용 갱신
        if current_cost < min_cost:
            min_cost = current_cost
            # 디버깅: min_cost가 갱신될 때 출력
            print(f"New min_cost: {min_cost}, with permutation: {perm}")

# 최종적으로 계산된 최소 비용 출력
print(min_cost)
