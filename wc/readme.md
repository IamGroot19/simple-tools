Akin to the uniq `wc` (wordcount) tool. Will try to resemble the features and fucntionalities as close to unix wc as possible.

```
python wc.py [-w] [-c] [-l]  <filename>
<l> <w> <c>
```

# python

## within 30minutes

was able to build the tool iself and it was giing reasonably accurate value when compared to a text file. Came with a argparse based CLI app. 

yet to 
- compare with a big textfile like moby.txt
- compare perforance of uniq wc and my program
  - todo: profiling of the progam (both cpu & memory)

## within 30-60 min

```
bsr@aspire:~/Documents/side-projects/simple-tools/wc$ time wc mobydick.txt 
  22316  215838 1276290 mobydick.txt

real    0m0.046s
user    0m0.041s
sys     0m0.005s

bsr@aspire:~/Documents/side-projects/simple-tools/wc$ time python3 py/main.py -w -c -l mobydick.txt 
22316 215838 1233905 mobydick.txt

real    0m0.151s
user    0m0.138s
sys     0m0.013s

/// After adding __name__="__main__"
bsr@aspire:~/Documents/side-projects/simple-tools/wc$ time python3 py/main.py -w -c -l mobydick.txt 
22316 215838 1233905 mobydick.txt

real    0m0.151s
user    0m0.138s
sys     0m0.013s
```

- there are slight difference in character count. I am writing it off as some miss in some other character count - willl need to read `wc` manpage/spec/source code to find out.

Now, actual issue boils down to performace. Python code is 3x slower compared to uniq one.

## optimisation

I moved the  entire logic of wc into a separate function (`wc()`) and am calling that from the main function.

NOTE: till this point, i was printing the execution times of a single run, which in hindsight is not an optimal move. We will need to run the command multiple times and get an average. For simplicity, I am going to use `hyperfine <cmd>` which will run the cmd 10times by default and print the stat

```
bsr@aspire:~/Documents/side-projects/simple-tools/wc$ hyperfine --runs 10 'wc mobydick.txt'
Benchmark 1: wc mobydick.txt
  Time (mean ± σ):      13.2 ms ±   2.9 ms    [User: 13.0 ms, System: 0.5 ms]
  Range (min … max):    10.4 ms …  19.3 ms    10 runs
 
bsr@aspire:~/Documents/side-projects/simple-tools/wc$ hyperfine  --warmup 2 --runs 10 'python3 py/main.py -w -c -l mobydick.txt' 
Benchmark 1: python3 py/main.py -w -c -l mobydick.txt
  Time (mean ± σ):     102.6 ms ±   4.8 ms    [User: 92.0 ms, System: 10.6 ms]
  Range (min … max):    97.7 ms … 114.6 ms    10 runs
```

**Currently, Unix wc is 8x faster than my python code**

### Intuition 

Removing the if conditional to check if `-w` flag is enabled should cut down time since we are removign that check for every iteratio in the loop
- Indeed. Removing the if check on every iteration cut down the time. Instead, cmpute it anyways and just print it in end depending on whether the conditional was enabled

```
bsr@aspire:~/Documents/side-projects/simple-tools/wc$ hyperfine  --warmup 2 --runs 10 'python3 py/main.py -w -c -l mobydick.txt' 
Benchmark 1: python3 py/main.py -w -c -l mobydick.txt
  Time (mean ± σ):     101.8 ms ±   4.4 ms    [User: 91.7 ms, System: 10.0 ms]
  Range (min … max):    99.1 ms … 114.0 ms    10 runs
 
  Warning: Statistical outliers were detected. Consider re-running this benchmark on a quiet PC without any interferences from other programs. It might help to use the '--warmup' or '--prepare' options.
```

Another dumstuff i was doing was that, i read each line, split them into words, then: a) incremented word count b) calculated len of each word & added it to the character counter. Instead, i could have just addd length of line in the first place to get character count.
- code change
```
# Before
    with open(args.inputfile, "r") as f:
        for x in f:
            linect += 1
            linesplit = x.split()
            wordct += len(linesplit)
            for word in linesplit:
                charct += len(word)
        charct += wordct - 1 ## accounting for whitespaces

# After 
    with open(args.inputfile, "r") as f:
        for x in f:
            linect += 1
            charct += len(x)
            wordct += len(x.split())
```

- perf change: 20% improvement! Now, we are only 7x slower (compared to 8x to 9x slowness earlier)
```
bsr@aspire:~/Documents/side-projects/simple-tools/wc$ hyperfine  --warmup 2 --runs 10 'python3 py/main.py -w -c -l mobydick.txt' 
Benchmark 1: python3 py/main.py -w -c -l mobydick.txt
  Time (mean ± σ):      83.5 ms ±   1.8 ms    [User: 71.4 ms, System: 12.0 ms]
  Range (min … max):    80.9 ms …  85.9 ms    10 runs
```

### Basic googling

Faster way to calculate string lengths
- ref https://stackoverflow.com/a/21501588
- nothing for us here since we are already calling `len()` which is a native method

Faster way to read files
- > `open()` is already the fastest way to read files apparently: https://stackoverflow.com/questions/14944183/python-fastest-way-to-read-a-large-text-file-several-gb

What abt multi-processing / multi-threading?
- refer to all answers of this: https://stackoverflow.com/questions/30294146/fastest-way-to-process-a-large-file and see what all you can pick from it

- intuition: check the file size and have a certain param for parallel processing. For eg, break down the fie into 4 parts and make 4 separate threads read the 4 parts paralllely. But ensure that the bounds you pass to each thread iis such that it's demarcated at the line ending (i.e a `/n` character)

  - my intuition says that might help only if you have bigger files. Say above 200MB (even this size, i am not sure what would be the critical size and figuring that out for a given value of parallelism requires some kind of binary search based approach of benchmarking)


### Basic cProfiling

code change
```
from cProfile import Profile
from pstats import SortKey, Stats

if __name__ == "__main__":
    with Profile() as profile:
        wc()
        (
            Stats(profile)
            # .strip_dirs()
            .sort_stats(SortKey.CALLS)
            .print_stats()
        )
```


Results
```

```

This doesnt show much except for the fact that the loop runs a lot of times and certain functions are called a lot of times. 

I dont know how to make use of the above profiling data and optimise the code


# TODO

- find out most efficient file handling methods for python
  - not just reading line by line, but in general, read abt all best practices and write them down

- find out best (&fastest) cli framework (apart from the simple argparse)

- find out how to do profiling for cpu & memory here

- todo: find out how to perform multi-processing and multi-threading here

- todo findout how to use `perf` (the linux utility) toidentify syscalls and optimise 
  - learn to use perf instead of hyperfine: https://stackoverflow.com/questions/17601539/calculate-the-average-of-several-time-commands-in-linux