# 백준 문제 17425: 약수의 합

import sys
input = sys.stdin.read

# 최대값 설정 및 배열 초기화
MAX = 1000000
divisor_sum = [0] * (MAX + 1)        # 각 숫자의 약수의 합을 저장할 배열
cumulative_sum = [0] * (MAX + 1)     # 누적 합을 저장할 배열

# 각 숫자의 약수의 합 계산
for i in range(1, MAX + 1):
    for j in range(i, MAX + 1, i):
        divisor_sum[j] += i

# 누적 합 계산
for i in range(1, MAX + 1):
    cumulative_sum[i] = cumulative_sum[i - 1] + divisor_sum[i]

def main():
    # 입력된 데이터를 공백을 기준으로 나누어 리스트로 만듭니다
    data = input().strip().split()
    T = int(data[0])  # 첫 번째 입력은 테스트 케이스 수
    results = [cumulative_sum[int(data[i])] for i in range(1, T + 1)]
    # 각 테스트 케이스에 대해 결과를 출력
    for result in results:
        print(result)
1
# 프로그램의 시작점
if __name__ == "__main__":
    main()



# # 최대값 설정
# MAX = 1000000

# # 각 인덱스마다 약수의 합을 담아 놓을 배열 초기화
# dp = [0] * (MAX + 1)
# # 각 인덱스까지 누적합을 담을 배열 초기화
# s = [0] * (MAX + 1)

# for i in range(1, MAX + 1): #1부터 최대값까지
#     j = 1 # i에 곱할 j를 선언
#     while i * j <= MAX: # i * j 값이 최대값이 넘지 않을 때까지
#         # dp배열의 인덱스인 i의 배수에 i 값을 더해준다. 
#         dp[i * j] += i #예를들면 3*j의 해당하는 값들은 3을 무조건 약수로 가지기 때문에 3을 더해준다 
#         j += 1 #j값 증가
#     s[i] = s[i - 1] + dp[i] #해당 dp[i]의 값 까지 더한 누적합을 s배열에 넣어준다.

# t = int(input()) #테스트 케이스 개수 입력

# for _ in range(t):
#     a = int(sys.stdin.readline())
#     sys.stdout.write(str(s[a])+"\n")