# 백준 문제 1929: 소수 구하기

def sieve_of_eratosthenes(M, N):
    # 에라토스테네스의 체를 사용하여 소수를 구하는 함수
    is_prime = [True] * (N + 1)
    is_prime[0], is_prime[1] = False, False # 0과 1은 소수가 아님

    # 2부터 √N까지의 모든 수에 대해 배수들을 지움
    for i in range(2, int((N ** 0.5)+1)):
        if is_prime[i]:
            for j in range(i*i, N+1, i):
                is_prime[j] = False
    
    # M부터 N까지의 모든 소수를 출력
    for k in range(M, N+1):
        if is_prime[k]:
            print(k)

def main():
    # 두 정수를 입력받음
    M, N = map(int, input().split())

    # 소수를 구하는 함수를 호출
    sieve_of_eratosthenes(M, N)

# 프로그램의 시작점
if __name__ == "__main__":
    main()