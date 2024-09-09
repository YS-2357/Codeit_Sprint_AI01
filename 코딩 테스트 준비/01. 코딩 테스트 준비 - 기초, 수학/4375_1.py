# # 백준 문제 4375: 1

# # 함수 정의: 주어진 수 n의 배수 중 1로만 이루어진 가장 작은 수의 자릿수를 찾습니다.
# def find_smallest_multiple(n):
#     number = 1  # 1로 시작하는 숫자
#     count = 1   # 자릿수를 세는 변수
#     while number % n != 0:
#         number = number * 10 + 1  # 다음 1로만 이루어진 수를 생성
#         count += 1  # 자릿수 증가
#     return count  # 자릿수를 반환

# # 반복적으로 입력을 받아 처리합니다.
# while True:
#     try:
#         n = int(input("숫자를 입력하세요 (종료하려면 0 입력): "))
#         if n == 0:
#             break
#         print(f"1로만 이루어진 {n}의 배수의 자릿수: {find_smallest_multiple(n)}")
#     except ValueError:
#         print("유효한 숫자를 입력하세요.")


21
# 백준 문제 4375: 1

# 함수 정의: 주어진 수 n의 배수 중 1로만 이루어진 가장 작은 수의 자릿수를 찾습니다.
def find_smallest_multiple(n):
    number = 1  # 1로 시작하는 숫자
    count = 1   # 자릿수를 세는 변수
    while number % n != 0:
        number = number * 10 + 1  # 다음 1로만 이루어진 수를 생성
        count += 1  # 자릿수 증가
    return count  # 자릿수를 반환

# 표준 입력에서 모든 입력을 읽어옵니다.
import sys
input = sys.stdin.read

# 입력된 데이터를 공백을 기준으로 나누어 리스트로 만듭니다.
data = input().strip().split()

# 각 입력된 수에 대해 결과를 출력합니다.
for line in data:
    if line:  # 빈 문자열이 아닌 경우에만 처리
        n = int(line)  # 문자열을 정수로 변환
        if n == 0:
            break
        print(find_smallest_multiple(n))  # 함수 호출 후 결과 출력
