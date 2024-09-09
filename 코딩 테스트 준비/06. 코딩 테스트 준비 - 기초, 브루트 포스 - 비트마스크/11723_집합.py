# 백준 문제 11723: 집합

# 표준 입력을 사용하기 위한 sys 모듈 임포트
import sys
input = sys.stdin.read

# 입력을 한 번에 읽어오기
data = input().strip().split("\n")

# 숫자 1부터 20까지의 포함 여부를 관리할 리스트 (0으로 초기화)
bit_set = [0] * 21  # 인덱스 1부터 20까지 사용

# 주어진 명령을 하나씩 처리
for line in data:
    # 명령어를 공백으로 분리하여 리스트로 변환
    command = line.split()
    
    # 명령어가 'all' 또는 'empty'일 때
    if len(command) == 1:
        if command[0] == "all":
            # 모든 원소를 추가 (1부터 20까지 모두 1로 설정)
            bit_set = [1] * 21
        elif command[0] == "empty":
            # 모든 원소를 제거 (비어 있는 집합으로 초기화)
            bit_set = [0] * 21
    else:
        # 명령어가 'add', 'remove', 'check', 'toggle'일 때
        operation, x = command[0], int(command[1])
        if operation == "add":
            # 원소 x 추가 (x번째 요소를 1로 설정)
            bit_set[x] = 1
        elif operation == "remove":
            # 원소 x 제거 (x번째 요소를 0으로 설정)
            bit_set[x] = 0
        elif operation == "check":
            # 원소 x의 포함 여부 출력 (x번째 요소가 1인지 확인)
            print(1 if bit_set[x] == 1 else 0)
        elif operation == "toggle":
            # 원소 x 토글 (x번째 요소를 반전)
            bit_set[x] = 1 - bit_set[x]
