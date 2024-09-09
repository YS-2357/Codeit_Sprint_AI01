# 백준 문제 2529: 부등호

# 표준 입력을 사용하기 위한 sys 모듈 임포트
import sys
input = sys.stdin.read

# 입력을 한 번에 읽어오기
data = input().strip().split()

# 부등호 개수 K
K = int(data[0])

# 부등호 리스트
signs = data[1:]

# 결과를 저장할 리스트 초기화
min_num = "9999999999"  # 임시 최대값으로 초기화
max_num = "0"           # 임시 최소값으로 초기화

# 사용된 숫자를 체크하기 위한 리스트 초기화
used = [False] * 10

# 숫자 조합을 찾기 위한 백트래킹 함수 정의
def backtrack(count, sequence):
    global min_num, max_num

    # K+1개의 숫자를 모두 사용한 경우
    if count == K + 1:
        # 현재 숫자 조합 문자열로 변환
        num = ''.join(map(str, sequence))
        
        # 최소값과 최대값 갱신
        if num < min_num:
            min_num = num
            print(f"New min_num: {min_num}")
        if num > max_num:
            max_num = num
            print(f"New max_num: {max_num}")
        return
    
    # 가능한 숫자를 순회하면서 백트래킹
    for i in range(10):
        if not used[i]:  # 사용되지 않은 숫자인 경우
            if count == 0 or (signs[count - 1] == '<' and sequence[-1] < i) or (signs[count - 1] == '>' and sequence[-1] > i):
                # 현재 숫자를 사용하여 시퀀스에 추가
                used[i] = True
                sequence.append(i)
                backtrack(count + 1, sequence)
                # 백트래킹을 위해 숫자 사용 표시 제거 및 시퀀스에서 제거
                used[i] = False
                sequence.pop()
                print(f"Backtracking by removing {i}, sequence: {sequence}")

# 백트래킹 함수 호출 (빈 시퀀스와 0부터 시작)
backtrack(0, [])

# 결과 출력
print(max_num)
print(min_num)
