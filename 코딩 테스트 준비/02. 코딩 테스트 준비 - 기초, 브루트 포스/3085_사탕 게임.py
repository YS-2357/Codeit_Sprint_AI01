# 백준 문제 3085: 사탕 게임

def check_max_candies(board, N):
    # 보드에서 연속된 사탕의 최대 개수를 찾는 함수
    max_candies = 1  # 최대 개수를 저장하는 변수 초기화

    # 행을 기준으로 연속된 사탕의 최대 개수 찾기
    for i in range(N):
        count = 1  # 현재 행에서 연속된 사탕의 개수
        for j in range(1, N):
            if board[i][j] == board[i][j - 1]:
                count += 1  # 이전 사탕과 같으면 개수 증가
            else:
                max_candies = max(max_candies, count)  # 최대값 갱신
                count = 1  # 개수 초기화
        max_candies = max(max_candies, count)  # 마지막 연속 개수 확인

    # 열을 기준으로 연속된 사탕의 최대 개수 찾기
    for j in range(N):
        count = 1  # 현재 열에서 연속된 사탕의 개수
        for i in range(1, N):
            if board[i][j] == board[i - 1][j]:
                count += 1  # 이전 사탕과 같으면 개수 증가
            else:
                max_candies = max(max_candies, count)  # 최대값 갱신
                count = 1  # 개수 초기화
        max_candies = max(max_candies, count)  # 마지막 연속 개수 확인

    return max_candies  # 최대 연속 사탕 개수 반환

def swap_and_check(board, i, j, N):
    # 주어진 위치에서 사탕을 교환하고 최대 연속 사탕 개수를 찾는 함수
    max_candies = 0  # 최대 개수를 저장하는 변수 초기화

    # 오른쪽 사탕과 교환
    if j + 1 < N:
        board[i][j], board[i][j + 1] = board[i][j + 1], board[i][j]  # 사탕 교환
        max_candies = max(max_candies, check_max_candies(board, N))  # 최대값 갱신
        board[i][j], board[i][j + 1] = board[i][j + 1], board[i][j]  # 원래대로 되돌림

    # 아래쪽 사탕과 교환
    if i + 1 < N:
        board[i][j], board[i + 1][j] = board[i + 1][j], board[i][j]  # 사탕 교환
        max_candies = max(max_candies, check_max_candies(board, N))  # 최대값 갱신
        board[i][j], board[i + 1][j] = board[i + 1][j], board[i][j]  # 원래대로 되돌림

    return max_candies  # 최대 연속 사탕 개수 반환

def main():
    # 보드 크기 입력
    N = int(input())
    board = [list(input().strip()) for _ in range(N)]  # 보드 상태 입력

    max_candies = 0  # 최대 사탕 개수를 저장하는 변수 초기화

    # 모든 칸에 대해 교환 후 최대 사탕 개수 계산
    for i in range(N):
        for j in range(N):
            max_candies = max(max_candies, swap_and_check(board, i, j, N))  # 최대값 갱신

    print(max_candies)  # 결과 출력

# 프로그램의 시작점
if __name__ == "__main__":
    main()
