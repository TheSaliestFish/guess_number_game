import random


def main():
    answer = random.randint(1, 100)
    attempts = 0

    print("猜数字游戏：我想好了一个 1 到 100 之间的数字。")
    while True:
        try:
            guess = int(input("请输入你的猜测："))
        except ValueError:
            print("请输入有效的整数。")
            continue

        attempts += 1
        if guess < answer:
            print("太小了，再试一次！")
        elif guess > answer:
            print("太大了，再试一次！")
        else:
            print(f"恭喜你，猜对了！你一共猜了 {attempts} 次。")
            break


if __name__ == "__main__":
    main()
