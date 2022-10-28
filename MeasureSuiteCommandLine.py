from subprocess import Popen, PIPE, STDOUT
import argparse
import os
import pathlib
import json


BUILD_FOLDER = "/build"
DEBUG = False


def build():
    """
    simply builds the needed C project.
    """
    # first create the build folder
    path = str(pathlib.Path().resolve())
    path += BUILD_FOLDER
    os.mkdir(path)

    if DEBUG:
        print(path)

    # next run the cmake command
    cmd = ["cmake", ".."]
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
              preexec_fn=os.setsid, cwd=path)
    p.wait()
    if p.returncode != 0:
        print("ERROR cmake")
        return 1

    # next run make
    cmd = ["make"]
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
              preexec_fn=os.setsid, cwd=path)
    p.wait()
    if p.returncode != 0:
        print("ERROR make")
        return 2

    return 0


def check_if_already_build():
    """
    checks wether `build` was called or not.
    """
    path = str(pathlib.Path().resolve()) + BUILD_FOLDER
    return os.path.exists(path)


def main():
    parser = argparse.ArgumentParser(description='MeasureSuiteCommandLine')
    parser.add_argument('-c', required=True, type=str, help='c code')
    parser.add_argument('-a', required=True, type=str, help='asm code')
    args = parser.parse_args()

    # check wether the c project was build or not
    if not check_if_already_build():
        if build() != 0:
            print("could not build the c projext")

    # run the c code
    cmd = ["./main", args.c, args.a]
    path = str(pathlib.Path().resolve()) + BUILD_FOLDER
    if DEBUG:
        print(cmd, path)
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
              preexec_fn=os.setsid, cwd=path)
    p.wait()

    # read the output
    data = p.stdout.read()
    data = data.decode("ascii")
    if DEBUG:
        print(data)

    # example output of the programm
    # {
    #   "stats":
    #  {
    #   "countA": 1,
    #   "countB": 1,
    #   "chunksA": 0,
    #   "chunksB": 0,
    #   "batchSize": 1,
    #   "numBatches": 1,
    #   "runtime": 0,
    #   "runOrder": "ba",
    #   "checkResult": true
    #   },
    #  "times": [[-1,4792,1196],[798,-1,771]]
    #  }
    jdata = json.loads(data)
    print(jdata)


if __name__ == "__main__":
    """
    test command:

python MeasureSuiteCommandLine.py -c "#include <stdint.h>
void add_two_numbers(uint64_t *o, const uint64_t *i0, const uint64_t *i1) {
        *o = *i0 + *i1;
}"-a "mov rax, [rsi]
add rax, [rdx]
mov [rdi], rax
ret"
    """
    main()
