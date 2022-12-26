#!/usr/bin/env python3

import pathlib as _pathlib
import resource as _resource
import sys as _sys

import lambda_language as _lambda_language


def main():
    args = _sys.argv[1:]

    if not args:
        code_to_evaluate = _sys.stdin.read()
    elif len(args) == 1:
        lambda_program_path = _pathlib.Path(args[0])
        code_to_evaluate = lambda_program_path.read_text()
    else:
        print('ERROR: Too many arguments passed', file=_sys.stderr)
        return 1

    lang = _lambda_language.LambdaLanguage()

    _weaken_recursion_limits()

    term = lang.term_from_code(code_to_evaluate)
    term.normalize()
    output = lang.represent_term(term)

    print(output)

    return 0


def _weaken_recursion_limits():
    _resource.setrlimit(_resource.RLIMIT_STACK, [0x10000000, _resource.RLIM_INFINITY])
    _sys.setrecursionlimit(0x100000)


if __name__ == '__main__':
    _sys.exit(main())
