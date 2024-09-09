# 백준 문제 6603: 로또

# itertools 모듈의 combinations 함수를 사용하기 위해 임포트
from itertools import combinations

# 표준 입력을 사용하기 위한 sys 모듈 임포트
import sys
input = sys.stdin.read

# 입력을 한 번에 읽어오기
data = input().strip().split("\n")

# 입력 데이터 처리
for line in data:
    # 각 라인을 공백으로 나누어 리스트로 변환
    numbers = list(map(int, line.split()))

    # 첫 번째 숫자는 숫자의 개수, 이를 제외한 나머지는 실제 숫자들
    k = numbers[0]  # 첫 번째 숫자는 k (주어진 숫자의 개수)
    s = numbers[1:] # 나머지 숫자들이 실제 선택 가능한 숫자들
    
    # k가 0이면 종료 (입력 종료 조건)
    if k == 0:
        break

    # itertools.combinations 함수를 사용하여 숫자들 중 6개를 선택하는 모든 조합 생성
    all_combinations = combinations(s, 6)

    # 생선된 모든 조합을 순회하며 출력
    for comb in all_combinations:
        # comb는 튜플 형태이므로, 이를 문자열로 변환하여 출력
        # map 함수는 comb의 각 요소를 문자열로 변환함
        print(' '.join(map(str, comb)))

    # 각 테스트 케이스 사이에 빈 줄 출력
    print()