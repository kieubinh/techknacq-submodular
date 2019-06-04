import time


def main():
    count = 0
    for i in range(0, 2*1000*1000*100):
        count += 1
    return count


if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
