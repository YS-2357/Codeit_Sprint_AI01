# 백준 문제 1978: 소수 찾기

def is_prime(num):
    # 소수 여부를 판별하는 함수
    if num <= 1:
        return False
    for i in range(2, int(num ** 0.5) + 1):  # 제곱근까지 반복
        if num % i == 0:
            return False
    return True

def main():
    # 첫 번째 줄에 입력된 수의 개수 N을 입력받음
    n = int(input())
    # 두 번째 줄에 N개의 수를 입력받아 리스트로 변환
    numbers = list(map(int, input().split()))

    # 소수의 개수를 세기 위한 변수
    prime_count = 0

    # 입력받은 각 수에 대해 소수인지 판별
    for number in numbers:
        if is_prime(number):
            prime_count += 1

    # 소수의 개수를 출력
    print(prime_count)

# 프로그램의 시작점
if __name__ == "__main__":
    main()
