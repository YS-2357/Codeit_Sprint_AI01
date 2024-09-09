# 백준 문제 15661: 링크와 스타트

# 표준 입력을 사용하기 위한 sys 모듈 임포트
import sys
input = sys.stdin.read

# 입력을 한 번에 읽어오기
data = input().strip().split()

# 주어진 숫자 N
N = int(data[0])

# 능력치 표 초기화
abilities = []
index = 1
for i in range(N):
    row = list(map(int, data[index:index + N]))
    abilities.append(row)
    index += N

# 최소 차이를 저장할 변수 초기화
min_diff = float('inf')

# 팀 나누기 백트래킹 함수 정의
def backtrack(start, team):
    global min_diff
    
    # 팀이 나누어진 경우
    if len(team) > 0 and len(team) < N:
        other_team = [i for i in range(N) if i not in team]
        team_score = sum(abilities[i][j] for i in team for j in team)
        other_team_score = sum(abilities[i][j] for i in other_team for j in other_team)
        current_diff = abs(team_score - other_team_score)
        if current_diff < min_diff:
            min_diff = current_diff
            # 핵심 디버깅 출력
            print(f"New min_diff: {min_diff} (Team: {team}, Other Team: {other_team})")
        # if 구문을 없앤 경우 아래처럼 바로 입력
        # min_diff = min(min_diff, abs(team_score - other_team_score))

    
    # 가능한 팀 조합을 찾기 위한 백트래킹
    for i in range(start, N):
        if i not in team:
            team.append(i)
            backtrack(i + 1, team)
            team.pop()

# 백트래킹 함수 호출 (빈 팀과 0부터 시작)
backtrack(0, [])

# 결과 출력
print(min_diff)
