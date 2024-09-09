# 백준 문제 2309: 일곱 난쟁이

def find_seven_dwarfs(dwarfs):
    total_sum = sum(dwarfs)
    
    # 일곱 난쟁이를 찾기 위한 9명 중 2명을 제외하는 루프
    for i in range(9):
        for j in range(i + 1, 9):
            if total_sum - dwarfs[i] - dwarfs[j] == 100:
                # 제외할 두 난쟁이를 찾으면 리스트에서 제거
                excluded_dwarfs = [dwarfs[k] for k in range(9) if k != i and k != j]
                return sorted(excluded_dwarfs)  # 오름차순 정렬하여 반환

def main():
    # 9명의 난쟁이 키를 입력받음
    dwarfs = [int(input()) for _ in range(9)]
    
    # 일곱 난쟁이를 찾는 함수 호출
    result = find_seven_dwarfs(dwarfs)
    
    # 결과 출력
    for dwarf in result:
        print(dwarf)

# 프로그램의 시작점
if __name__ == "__main__":
    main()
