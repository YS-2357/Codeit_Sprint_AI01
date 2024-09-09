# 백준 문제 6064: 카잉 달력

# sys 모듈을 사용하여 입력을 빠르게 받기
import sys
input = sys.stdin.readline

# 테스트 케이스의 수 입력 받기
T = int(input().strip())

# 각 테스트 케이스에 대한 입력 값을 저장할 리스트 초기화
test_cases = []

# 각 테스트 케이스의 입력 값을 저장
for _ in range(T):
    M, N, x, y = map(int, input().strip().split())
    test_cases.append((M, N, x, y))

# 결과를 저장할 리스트 초기화
results = []

# 각 테스트 케이스에 대해 처리
for M, N, x, y in test_cases:
    # 변수 초기화: 답을 찾기 위해 x를 기준으로 이동
    k = x
    while k <= M * N:
        # 현재 k가 y와 같은지 확인
        if k % N == y % N:
            # y가 N과 동일한 경우 예외 처리
            if (y % N == 0 and k % N == 0) or (k % N == y % N):
                results.append(k)
                break
        # x를 기준으로 다음 값을 찾기 위해 M씩 증가
        k += M
    else:
        # 주어진 범위 내에서 답을 찾지 못한 경우
        results.append(-1)

# 결과 출력
for result in results:
    print(result)
