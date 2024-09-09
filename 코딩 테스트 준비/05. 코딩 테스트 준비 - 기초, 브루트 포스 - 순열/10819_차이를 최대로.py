# 백준 문제 10819: 차이를 최대로

# itertools 모듈의 permutations 함수를 사용하기 위해 임포트
from itertools import permutations

# 표준 입력을 사용하기 위한 sys 모듈 임포트
import sys
input = sys.stdin.read

# 입력을 한버에 받아오기
data = input().strip().split()

# 배열의 크기 N
N = int(data[0])

# 배열의 원소들 
arr = list(map(int, data[1:]))

# 배열의 최대 차이 합을 저장한 변수 초기화
max_diff = 0

# itertools.permutations 함수를 사용하여 arr 리스트의 모든 순열 생성
all_permutatios = permutations(arr)

# 생성된 모든 순열을 순회하며 차이의 합 계산
for perm in all_permutatios:
    # 현재 순열에서 차이의 합을 계산한 변수 초기화
    current_diff = 0

    # 순열의 인접한 원소의 차이의 합 계산
    for i in range(N - 1):
        # |A[i] - A[i + 1]|를 current_diff에 더하기
        current_diff += abs(perm[i] - perm[i + 1])

    # 최대 차이 합 갱신
    if current_diff > max_diff:
        max_diff = current_diff
        # 디버깅: max_difference가 갱신될 때 출력
        print(f"New max_difference: {max_diff}, with permutation: {perm}")


# 최종적으로 계산된 최대 차이 합 출력
print(max_diff)