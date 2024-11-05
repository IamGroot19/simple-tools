import argparse
from cProfile import Profile
from pstats import SortKey, Stats

def wc():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile", type=str, help="A positional argument specifying filename for the wordcount program" )

    parser.add_argument("-l", "--line",  action="store_true", help="A boolean flag specifing whether number of lines should be computed")
    parser.add_argument("-w", "--word",  action="store_true", help="A boolean flag specifing whether number of words should be computed")
    parser.add_argument("-c", "--character",  action="store_true", help="A boolean flag specifing whether number of characters should be computed")

    args = parser.parse_args()

    charct, wordct, linect = 0, 0, 0
    with open(args.inputfile, "r") as f:
        for x in f:
            linect += 1
            charct += len(x)
            wordct += len(x.split())
            # print(f"debug: linesplit: {linesplit}")

    output_str = ""

    if args.line:
        output_str += f"{linect}"
    if args.word:
        output_str += f" {wordct}"
    if args.character:
        output_str += f" {charct}"
    output_str += f" {args.inputfile}"
    print(output_str)

if __name__ == "__main__":
    # with Profile() as profile:
    #     wc()
    #     (
    #         Stats(profile)
    #         # .strip_dirs()
    #         .sort_stats(SortKey.CALLS)
    #         .print_stats()
    #     )
    wc()
    

