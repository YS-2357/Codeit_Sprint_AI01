# 백준 문제 14889: 스타트와 링크

# 표준 입력을 사용하기 위한 sys 모듈 임포트
import sys
input = sys.stdin.read

# 입력을 한 번에 읽어오기
data = input().strip().split()

# 주어진 숫자 N (사람의 수)
N = int(data[0])

# 능력치 표 초기화
abilities = []
index = 1
for i in range(N):
    row = list(map(int, data[index:index + N]))
    abilities.append(row)
    index += N

# 팀 나누기 백트래킹 함수 정의
def backtrack(start, team):
    # 디버깅: 현재 함수 호출의 상태를 출력
    # print(f"backtrack(start={start}, team={team})")
    
    # 팀이 절반으로 나누어진 경우
    if len(team) == N // 2:
        # 나머지 팀 구성
        other_team = [i for i in range(N) if i not in team]
        
        # 팀의 능력치 계산
        team_score = sum(abilities[i][j] for i in team for j in team)
        other_team_score = sum(abilities[i][j] for i in other_team for j in other_team)
        
        # 능력치 차이 갱신
        global min_diff
        min_diff = min(min_diff, abs(team_score - other_team_score))
        
        # 디버깅: 현재 팀, 다른 팀, 각 팀의 능력치, 최소 차이 출력
        # print(f"Team: {team}, Other Team: {other_team}, Team Score: {team_score}, Other Team Score: {other_team_score}, Min Diff: {min_diff}")
        return
    
    # 가능한 팀 조합을 찾기 위한 백트래킹
    for i in range(start, N):
        if i not in team:
            # 현재 사람을 팀에 추가
            team.append(i)
            # print(f"Backtracking with team: {team}")
            
            # 다음 사람으로 이동하여 재귀 호출
            backtrack(i + 1, team)
            
            # 백트래킹을 위해 현재 사람을 팀에서 제거
            team.pop()
            # print(f"Backtracking by removing {i}, team: {team}")

# 초기값 설정
min_diff = float('inf')

# 백트래킹 함수 호출 (빈 팀과 0부터 시작)
backtrack(0, [])

# 결과 출력
print(min_diff)
