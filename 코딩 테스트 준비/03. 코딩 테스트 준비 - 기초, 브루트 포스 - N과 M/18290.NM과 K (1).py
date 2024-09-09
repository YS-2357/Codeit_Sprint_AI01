# 백준 문제 18290: NM과 K (1)

# 표준 입력을 사용하기 위한 sys 모듈 임포트
import sys
input = sys.stdin.read

# 입력을 한 번에 읽어오기
data = input().strip().split()

# 주어진 숫자 N, M, K
N = int(data[0])
M = int(data[1])
K = int(data[2])

# 격자 입력받기
grid = []
index = 3
for i in range(N):
    row = list(map(int, data[index:index + M]))
    grid.append(row)
    index += M

# 방향 벡터 정의 (상, 하, 좌, 우)
directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# 최대 합을 저장할 변수 초기화
max_sum = -float('inf')

# 백트래킹 함수 정의
def backtrack(count, total_sum, visited):
    global max_sum
    
    # K개의 숫자를 모두 선택한 경우 최대 합 갱신
    if count == K:
        max_sum = max(max_sum, total_sum)
        return
    
    for x in range(N):
        for y in range(M):
            if visited[x][y]:
                continue
            # 인접한 위치가 이미 선택된 경우 패스
            can_select = True
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < N and 0 <= ny < M and visited[nx][ny]:
                    can_select = False
                    break
            if not can_select:
                continue
            
            # 숫자를 선택하고 백트래킹 호출
            visited[x][y] = True
            backtrack(count + 1, total_sum + grid[x][y], visited)
            visited[x][y] = False

# 초기 방문 여부 설정
visited = [[False] * M for _ in range(N)]

# 백트래킹 함수 호출
backtrack(0, 0, visited)

# 결과 출력
print(max_sum)
