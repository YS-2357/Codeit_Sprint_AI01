# 백준 문제 10430: 나머지
# 주어진 세 수 A, B, C에 대해 다음 연산을 수행합니다:
# (A + B) % C
# ((A % C) + (B % C)) % C
# (A * B) % C
# ((A % C) * (B % C)) % C

# 입력: A, B, C를 공백으로 구분하여 입력 받습니다.
A, B, C = map(int, input("A, B, C를 공백으로 구분하여 입력하세요: ").split())

# 첫 번째 연산: (A + B) % C
result1 = (A + B) % C

# 두 번째 연산: ((A % C) + (B % C)) % C
result2 = ((A % C) + (B % C)) % C

# 세 번째 연산: (A * B) % C
result3 = (A * B) % C

# 네 번째 연산: ((A % C) * (B % C)) % C
result4 = ((A % C) * (B % C)) % C

# 결과 출력
print("첫 번째 연산 결과: (A + B) % C =", result1)
print("두 번째 연산 결과: ((A % C) + (B % C)) % C =", result2)
print("세 번째 연산 결과: (A * B) % C =", result3)
print("네 번째 연산 결과: ((A % C) * (B % C)) % C =", result4)
