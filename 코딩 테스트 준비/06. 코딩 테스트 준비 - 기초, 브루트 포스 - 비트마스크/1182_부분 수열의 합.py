# 백준 문제 1182: 부분수열의 합

# 표준 입력을 사용하기 위한 sys 모듈 임포트
import sys
input = sys.stdin.read

# 입력을 한 번에 읽어오기
data = input().split()

# 정수 N과 S
N = int(data[0]) # 수열의 크기
S = int(data[1]) # 목표 합

# 수열 리스트
numbers = list(map(int, data[2:]))

# 부분수열의 합이 S가 되는 경우의 수를 저장할 변수
count = 0

# 백트래킹 함수 정의
def backtrack(index, current_sum):
    global count

    # 마지막 인덱스를 초과한 경우
    if index == N:
        return
    
    # 현재 위치의 숫자를 포함한 합 계산
    current_sum += numbers[index]

    # 현재 합이 S와 같은 경우, count 증가
    if current_sum == S:
        count += 1

    # 현재 위치의 숫자를 포함하는 경우와 포함하지 않는 경우로 분기
    # 포함하는 경우
    backtrack(index + 1, current_sum)

    # 포함하지 않는 경우
    backtrack(index + 1, current_sum - numbers[index])

# 백트래킹 시작 (0번 인덱스부터 시작)
backtrack(0, 0)

# 결과 출력
print(count)