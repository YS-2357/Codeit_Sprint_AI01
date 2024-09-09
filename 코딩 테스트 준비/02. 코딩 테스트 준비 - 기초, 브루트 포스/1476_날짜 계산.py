# 백준 문제 1476: 날짜 계산

# 지구, 태양, 달의 주기 최대값 설정
E_max, S_max, M_max = 15, 28, 19

# 사용자로부터 E, S, M 값을 입력 받음
E, S, M = map(int, input().split())

# 현재 연도를 나타내는 변수 초기화
year = 1

# 무한 루프를 사용하여 조건을 만족하는 연도를 찾음
while True:
    # 현재 연도의 지구, 태양, 달 주기 값을 계산
    if (year - E) % E_max == 0 and (year - S) % S_max == 0 and (year - M) % M_max == 0:
        break  # 조건을 만족하면 루프를 종료
    year += 1  # 조건을 만족하지 않으면 연도를 증가

# 조건을 만족하는 연도를 출력
print(year)



# 중국인의 나머지 정리를 사용한다면?
# # 백준 문제 1476: 날짜 계산

# def solve(E, S, M):
#     E_max, S_max, M_max = 15, 28, 19
    
#     year = E  # 시작 연도를 E로 설정

#     # E를 기준으로 S와 M에 대해 조건을 만족하는 연도를 찾음
#     while (year - S) % S_max != 0 or (year - M) % M_max != 0:
#         year += E_max

#     return year

# # 사용자로부터 E, S, M 값을 입력 받음
# E, S, M = map(int, input().split())

# # 조건을 만족하는 연도를 계산
# result = solve(E, S, M)

# # 결과 출력
# print(result)
