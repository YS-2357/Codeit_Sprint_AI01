# 백준 문제 10972: 다음 순열

# 표준 입력을 사용하기 위한 sys 모듈 임포트
import sys
input = sys.stdin.read

# 입력을 한 번에 읽어오기
data = input().strip().split()

# 숫자 N (순열의 크기)
n = int(data[0])

# 순열 리스트
permutation = list(map(int, data[1:]))

# 다음 순열을 구하는 함수
def next_permutation(perm):
    # 뒤에서부터 탐색하여 처음으로 감소하는 부분 찾기
    i = len(perm) - 2
    while i >= 0 and perm[i] >= perm[i + 1]:
        print(f"Checking perm[{i}] ({perm[i]}) >= perm[{i + 1}] ({perm[i + 1]})")
        i -= 1
    
    # 디버깅: 감소하는 부분 찾기
    print(f"Index of first decreasing element: {i}")

    # 만약 감소하는 부분이 없으면 (가장 마지막 순열인 경우)
    if i == -1:
        return False
    
    # 뒤에서부터 탐색하여 perm[i]보다 큰 첫 번째 값을 찾기
    j = len(perm) - 1
    while perm[i] >= perm[j]:
        print(f"Checking perm[{i}] ({perm[i]}) >= perm[{j}] ({perm[j]})")
        j -= 1
    
    # 디버깅: 첫 번째 교환할 값 찾기
    print(f"Index of element to swap with perm[{i}]: {j}")

    # 두 값을 교환
    perm[i], perm[j] = perm[j], perm[i]
    
    # 디버깅: 교환 후의 순열
    print(f"Permutation after swapping: {perm}")

    # i 이후의 부분을 오름차순으로 정렬
    perm[i + 1:] = reversed(perm[i + 1:])
    
    # 디버깅: 최종 순열
    print(f"Next permutation: {perm}")

    return True

# 다음 순열을 구하고 출력
if next_permutation(permutation):
    print(' '.join(map(str, permutation)))
else:
    print(-1)
