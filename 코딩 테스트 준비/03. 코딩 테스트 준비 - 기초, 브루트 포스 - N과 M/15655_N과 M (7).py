# 백준 문제 15656: N과 M (7)

# 표준 입력을 사용하기 위한 sys 모듈 임포트
import sys
input = sys.stdin.read

# 입력을 한 번에 읽어오기
data = input().strip().split()

# 주어진 숫자 N과 M
N = int(data[0])
M = int(data[1])

# N개의 숫자를 입력받기
numbers = list(map(int, data[2:2 + N]))

# 숫자 리스트를 오름차순으로 정렬
numbers.sort()

# 결과를 저장할 리스트 초기화
result = []

# 백트래킹 함수 정의
def backtrack(depth):
    # 디버깅: 현재 함수 호출의 상태를 출력
    # print(f"backtrack(depth={depth}, result={result})")
    
    # M개의 숫자를 모두 선택한 경우 결과에 추가
    if depth == M:
        print(' '.join(map(str, result)))
        return
    
    # N개의 숫자에 대해 반복
    for i in range(N):
        # 현재 숫자를 결과에 추가
        result.append(numbers[i])
        # 다음 깊이로 이동
        backtrack(depth + 1)
        # 백트래킹을 위해 숫자 제거
        result.pop()
        # 디버깅: 백트래킹 후 상태를 출력
        # print(f"backtrack after pop(depth={depth}, result={result})")

# 백트래킹 함수 호출 (깊이 0부터 시작)
backtrack(0)
