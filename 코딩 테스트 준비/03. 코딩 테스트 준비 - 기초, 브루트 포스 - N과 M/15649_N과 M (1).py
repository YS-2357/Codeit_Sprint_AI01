# 백준 문제 1550: N과 M (2)

# 표준 입력을 사용하기 위한 sys 모듈 임포트
import sys
input = sys.stdin.read

# itertools 모듈에서 permutations 함수 임포트
from itertools import permutations

# 입력을 한 번에 받아오기
data = input().split()

# 주어진 숫자 N과 M
N = int(data[0])
M = int(data[1])

# 1부터 N까지의 숫자 리스트 생성
numbers = list(range(1, N+1))

# permutations 함수를 사용애 길이가 M인 순열 생성
perms = permutations(numbers, M)

# 각 순열을 출력
for perm in perms:
    print(' '.join(map(str, perm)))