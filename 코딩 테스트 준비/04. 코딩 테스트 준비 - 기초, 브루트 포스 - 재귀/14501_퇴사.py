# 백준 문제 14501: 퇴사

# 표준 입력을 사용하기 위한 sys 모듈 임포트
import sys
input = sys.stdin.read

# 입력을 한 번에 읽어오기
data = input().strip().split()

# 주어진 숫자 N
N = int(data[0])

# 상담 일정 및 보수 리스트 초기화
T = []
P = []

# N개의 상담 일정 및 보수를 입력받기
index = 1
for i in range(N):
    T.append(int(data[index]))
    P.append(int(data[index + 1]))
    index += 2

# 최대 이익을 저장할 리스트 초기화
dp = [0] * (N + 1)

# 뒤에서부터 거꾸로 DP 테이블 채우기
print("Initial dp:", dp)
for i in range(N - 1, -1, -1):
    if i + T[i] <= N:
        dp[i] = max(P[i] + dp[i + T[i]], dp[i + 1])
        print(f"dp[{i}] (including P[{i}]): max(P[{i}] + dp[{i + T[i]}], dp[{i + 1}]) -> {dp[i]}")
    else:
        dp[i] = dp[i + 1]
        print(f"dp[{i}] (excluding P[{i}]): dp[{i + 1}] -> {dp[i]}")

print("Final dp:", dp)
print(dp[0])
