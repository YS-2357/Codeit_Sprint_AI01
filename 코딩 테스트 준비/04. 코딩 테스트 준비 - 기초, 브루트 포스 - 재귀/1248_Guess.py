# 백준 문제 1248: 맞춰봐

# 표준 입력을 사용하기 위한 sys 모듈 임포트
import sys
input = sys.stdin.read

# 입력을 한 번에 읽어오기
data = input().strip().split()

# 숫자 N
N = int(data[0])

# 부호 리스트
signs = data[1]

# 부호 행렬 초기화
sign_matrix = [[''] * N for _ in range(N)]
index = 0
for i in range(N):
    for j in range(i, N):
        sign_matrix[i][j] = signs[index]
        index += 1

# 결과를 저장할 리스트 초기화
result = []

# 숫자 배열을 찾기 위한 백트래킹 함수 정의
def backtrack(depth):
    if depth == N:
        print(' '.join(map(str, result)))
        exit(0)  # 정상 종료
    
    for num in range(-10, 11):
        result.append(num)
        if check_valid(depth):
            print(f"Valid at depth {depth}: {result}")  # 유효한 경우 디버깅 출력
            backtrack(depth + 1)
        result.pop()
        print(f"Backtracking at depth {depth}: {result}")  # 백트래킹 시 디버깅 출력

# 부분합이 부호 조건을 만족하는지 확인하는 함수 정의
def check_valid(depth):
    total = 0
    for i in range(depth, -1, -1):
        total += result[i]
        if sign_matrix[i][depth] == '+' and total <= 0:
            return False
        if sign_matrix[i][depth] == '-' and total >= 0:
            return False
        if sign_matrix[i][depth] == '0' and total != 0:
            return False
    return True

# 백트래킹 함수 호출 (0부터 시작)
backtrack(0)
