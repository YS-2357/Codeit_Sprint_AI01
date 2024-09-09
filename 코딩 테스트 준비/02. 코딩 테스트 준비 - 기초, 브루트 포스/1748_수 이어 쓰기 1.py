# 백준 문제 1748: 수 이어 쓰기 1

# 표준 입력을 사용하기 위한 sys 모듈 임포트
import sys
input = sys.stdin.read

# 입력을 한 번에 읽어오기
data = input().strip()

# 주어진 숫자 N
N = int(data)

# 자릿수 합을 저장할 변수 초기화
total_digits = 0

# 1자리부터 시작하여 자릿수 별로 계산
length = 1 # 현재 자릿수
start = 1  # 해당 자릿수의 시작 숫자
end = 9    # 해당 자릿수의 끝 숫자

# N이 속하는 자릿수를 찾을 때 까지 반복
while start <= N:
    # 현재 자릿수의 시작 숫자가 N보다 작거나 같은 경우
    if N >= end:
        # 해당 자릿수의 모든 숫자를 포함
        total_digits += (end - start + 1) * length
    else:
        # N이 중간에 속하는 경우
        total_digits += (N - start + 1) * length
    # 다음 자릿수로 이동
    length += 1
    start *= 10
    end = end * 10 + 9

# 결과 출력
print(total_digits)