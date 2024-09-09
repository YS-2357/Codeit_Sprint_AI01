# 백준 문제 10974: 모든 순열

# itertools 모듈의 permutations 함수를 사용하기 위해 임포트
from itertools import permutations

# 표준 입력으로부터 자연수 N을 입력받음
import sys
input = sys.stdin.read

# 입력 값을 읽어서 정수형으로 변환
N = int(input().strip())

# 1부터 N까지의 숫자 리스트 생성
numbers = list(range(1, N + 1))

# itertools.permutations 함수를 사용하여 numbers 리스트의 모든 순열 생성
# permutations(numbers)는 모든 원소를 포함하는 순열을 튜플 형태로 반환
all_permutations = permutations(numbers)

# 생성된 모든 순열을 하나씩 출력
for perm in all_permutations:
    # perm은 튜플 형태이므로, 이를 문자열로 변환하여 출력
    # map 함수는 perm의 각 요소를 문자열로 변환함
    print(' '.join(map(str, perm)))