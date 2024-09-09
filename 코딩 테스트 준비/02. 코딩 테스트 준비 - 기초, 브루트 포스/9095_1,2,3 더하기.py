# 백준 문제 9095: 1, 2, 3 더하기

# 표준 입력을 사용하기 위한 sys 모듈 임포트
import sys
input = sys.stdin.read

# 입력을 한 번에 읽어오기
data = input().split()

# 첫 번째 값은 테스트 케이스의 수
T = int(data[0])

# 각 테스트 케이스의 값을 저장할 리스트 초기화
test_cases = [int(data[i]) for i in range(1, T + 1)]

# 결과를 저장할 리스트 초기화
results = []

# 가능한 모든 방법을 찾는 재귀 함수 정의
def count_ways(n):
    if n == 0: # n이 0일 때 하나의 방법으로 간주 (기저 사례)
        return 1
    elif n < 0: # n이 0보다 작으면 방법이 없음
        return 0
    # 1, 2, 3을 각각 더한 결과를 재귀적으로 호출하여 계산
    return count_ways(n - 1) + count_ways(n - 2) + count_ways(n - 3)

# 각 테스트 케이스에 대해 처리
for num in test_cases:
    results.append(count_ways(num))

# 결과 출력
for result in results:
    print(result)


# 동적 프로그래밍이 더 효율적임
# # 백준 문제 9095: 1, 2, 3 더하기

# # 표준 입력을 사용하기 위한 sys 모듈 임포트
# import sys
# input = sys.stdin.read

# # 입력을 한 번에 읽어오기
# data = input().split()

# # 첫 번째 값은 테스트 케이스의 수 T
# T = int(data[0])

# # 각 테스트 케이스의 값을 저장할 리스트 초기화
# test_cases = [int(data[i]) for i in range(1, T + 1)]

# # 결과를 저장할 리스트 초기화
# results = []

# # 최대값 구하기 (모든 입력 중 최대값을 알아야 동적 프로그래밍 테이블을 미리 계산할 수 있음)
# max_value = max(test_cases)

# # 동적 프로그래밍 테이블 초기화 (최대값 + 1 크기)
# dp = [0] * (max_value + 1)

# # 기본 값 설정
# dp[1] = 1  # 1을 만드는 경우의 수는 1가지: (1)
# if max_value > 1:
#     dp[2] = 2  # 2를 만드는 경우의 수는 2가지: (1+1), (2)
# if max_value > 2:
#     dp[3] = 4  # 3을 만드는 경우의 수는 4가지: (1+1+1), (1+2), (2+1), (3)

# # 동적 프로그래밍을 통해 값 계산
# for i in range(4, max_value + 1):
#     dp[i] = dp[i - 1] + dp[i - 2] + dp[i - 3]

# # 각 테스트 케이스에 대해 결과를 리스트에 저장
# for num in test_cases:
#     results.append(dp[num])

# # 결과 출력
# for result in results:
#     print(result)
