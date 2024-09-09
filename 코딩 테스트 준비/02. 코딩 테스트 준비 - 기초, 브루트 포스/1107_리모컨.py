# 백준 문제 1107: 리모컨

# 표준 입력을 사용하기 위해 sys 모듈을 임포트
import sys

# 목표 채널과 고장난 버튼의 개수와 리스트를 입력받음
target = int(sys.stdin.readline().strip())  # 목표 채널을 입력받음
n = int(sys.stdin.readline().strip())  # 고장난 버튼의 개수를 입력받음
broken_buttons = set(sys.stdin.readline().split()) if n > 0 else set()  # 고장난 버튼의 리스트를 입력받아 집합으로 변환

# 현재 채널에서 목표 채널까지 이동하기 위한 최솟값을 초기화 (현재 채널은 100번)
min_presses = abs(target - 100)

# 모든 가능한 채널(0부터 999999까지)에 대해 브루트포스 탐색
for num in range(1000000):
    num_str = str(num)  # 숫자를 문자열로 변환하여 각 자리를 검사
    for digit in num_str:
        if digit in broken_buttons:  # 만약 숫자가 고장난 버튼에 포함되면
            break  # 더 이상 검사할 필요 없이 루프를 탈출
    else:
        # 고장난 버튼이 없는 경우
        presses = len(num_str) + abs(num - target)  # 숫자를 누르는 횟수 + 목표 채널까지 이동하는 횟수
        min_presses = min(min_presses, presses)  # 최솟값을 업데이트

# 결과 출력
print(min_presses)
