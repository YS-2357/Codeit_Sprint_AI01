# 백준 문제 17427: 약수의 합 2

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
    data = input().split()
    T = int(data[0])  # 첫 번째 입력은 테스트 케이스 수
    results = [cumulative_sum[int(data[i])] for i in range(1, T + 1)]
    # 각 테스트 케이스에 대해 결과를 출력
    print('\n'.join(map(str, results)))

# 프로그램의 시작점
if __name__ == "__main__":
    main()
