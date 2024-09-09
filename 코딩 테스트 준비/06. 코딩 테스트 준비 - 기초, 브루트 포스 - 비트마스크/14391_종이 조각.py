# 백준 문제 14391: 종이 조각

# 표준 입력을 사용하기 위한 sys 모듈 임포트
import sys
input = sys.stdin.read

# 입력을 한 번에 받아오기
data = input().split()

# 종이의 크기 N x M
N = int(data[0]) # 행의 수
M = int(data[1]) # 열의 수

# 종이의 숫자판
paper = []
for i in range(N):
    paper.append(list(map(int, data[2 + i])))

# 최댓값을 저장할 변수 초기화
max_sum = 0

# 2^(N*M)가지 경우를 모두 확인 (비트마스크를 사용)
for bit in range(1 << (N*M)):
    total = 0 # 현재 경우의 총 합을 저장할 변수

    # 가로 조각 합 계산
    for i in range(N):
        row_sum = 0 # 현재 행에서 가로로 자른 수의 합
        for j in range(M):
            # 1차원 배열로 변환했을 때의 인덱스 계산
            idx = i * M + j

            # bit & (1 << idx) == 0이면 가로로 자른 것
            if (bit & (1 << idx)) == 0:
                row_sum = row_sum * 10 + paper[i][j]
            else:
                # 세로로 자르는 경우 이전 가로 조각의 합을 total에 더함
                total += row_sum
                row_sum = 0
        # 마지막 가로 조각의 합을 total에 더함
        total += row_sum

    # 세로 조각 합 계산
    for j in range(M):
        col_sum = 0 # 현재 열에서 세로로 자른 수의 합
        for i in range(N):
            # 1차원 배열로 변환했을 때의 인덱스 계산
            idx = i * M + j

            # bit & (1 << idx) != 0 이면 세로로 자른 것
            if (bit & (1 << idx)) != 0:
                col_sum = col_sum * 10 + paper[i][j]
            else:
                # 가로로 자르는 경우 이전 세로 조각의 합을 total에 더함
                total += col_sum
                col_sum = 0
        # 마지막 세로 조각의 합을 total에 더함
        total += col_sum

    # 최대값 갱신
    if total > max_sum:
        max_sum = total

# 최댓값 출력
print(max_sum)