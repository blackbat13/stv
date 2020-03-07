def parse():
    n = 1
    results_file = open(f"strat_dfs_bridge_results_{n}.txt", "r")
    result_sum = 0
    for _ in range(0, 50):
        for _ in range(0, 4):
            results_file.readline()

        str = results_file.readline()
        str = str.split(':')[1]
        str = str.rstrip(' seconds\n')
        result_sum += float(str)
        results_file.readline()
        str = results_file.readline()
        results_file.readline()
        results_file.readline()
        str = str.split(':')[1]
        str = str.rstrip(' seconds\n')
        result_sum += float(str)

    print(f'Average={result_sum / 50.0} seconds')
