# 백준 문제 1037: 약수

# 입력받은 약수들로부터 원래 숫자를 찾는 함수
def find_original_number(divisors):
    # 가장 작은 약수와 가장 큰 약수를 곱하면 원래 숫자가 된다
    return min(divisors) * max(divisors)

# 입력 처리
import sys
input = sys.stdin.read

# 입력된 데이터를 공백을 기준으로 나누어 리스트로 만듭니다.
data = input().strip().split()

# 첫 번째 입력은 약수의 개수 N입니다.
N = int(data[0])

# 두 번째 입력은 N개의 약수입니다.
divisors = list(map(int, data[1:]))

# 원래 숫자를 찾습니다.
original_number = find_original_number(divisors)

# 결과를 출력합니다.
print(original_number)
