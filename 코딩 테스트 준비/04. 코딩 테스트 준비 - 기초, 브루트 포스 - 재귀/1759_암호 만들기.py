# 백준 문제 1659: 암호 만들기

# 표준 입력을 사용하기 위한 sys 모듈 임포트
import sys
input = sys.stdin.read

# 입력을 한 번에 읽어오기
data = input().strip().split()

# 주어진 숫자 L과 C
L = int(data[0])
C = int(data[1])

# 주어진 문자들
chars = data[2:]

# 문자를 오름차순으로 정렬
chars.sort()

# 모음 리스트
vowels = {'a', 'e', 'i', 'o', 'u'}

# 결과를 저장할 리스트 초기화
result = []

# 백트래킹 함수 정의
def backtrack(start, path):
    # 디버깅: 현재 함수 호출의 상태를 출력
    # print(f"backtrack(start={start}, path={path})")
    
    # 길이가 L인 조합을 찾은 경우
    if len(path) == L:
        # 모음과 자음 개수 체크
        num_vowels = sum(1 for char in path if char in vowels)
        num_consonants = L - num_vowels

        # 조건을 만족하는 경우 결과에 추가
        if num_vowels >= 1 and num_consonants >= 2:
            result.append(''.join(path))
        return
    
    # C개의 문자에 대해 반복
    for i in range(start, C):
        path.append(chars[i])
        backtrack(i + 1, path)
        path.pop()
        # 디버깅: 백트래킹 후 상태를 출력
        # print(f"backtrack after pop(start={start}, path={path})")

# 백트래킹 함수 호출 (빈 리스트와 0부터 시작)
backtrack(0, [])

# 결과출력
for password in result:
    print(password)