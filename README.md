# λ-Calculus Interpreter

λ-calculus is the simplest functional programming language.

It turns out that you can express any idea by starting with the "function" concept as the only base.

"function" means "abstraction on something" in λ-calculus.

## Usage Example

To run λ-program you can use this command:
```
$ python3 main.py lambda-program-source.lambda
```

Alternatively, you can run `main.py` and pass the source code as standard input.

Then your λ-expression will be fully evaluated and the program will print the result.

## Program Example

This is an example of a λ-program:

```
three := \f. \x. f (f (f x));
square := \num. \f. num (num f);
square three
```

You can find more examples on https://en.wikipedia.org/wiki/Church_encoding

## Language Overview

In general, a λ-program consists of several definitions followed by a main expression that is the target for evaluation.

In fact, definitions are just syntactic sugar over λ-expressions, and they are not required at all.
Their main purpose is to simplify the beginner experience.

So, the real basis of λ-calculus is λ-expression.

And you're probably already familliar with it.
This:
```
\f. \x. f (f (f x))
```
Is literally equivalent to this in python:
```
lambda f: lambda x: f(f(f(x)))
```

`f x y z` can be interpreted as `f(x, y, z)`.
But actually it is `f(x)(y)(z)`, since that's how arguments passing work in λ-calculus - we don't need the concept of multiple arguments.

And that's all!

So, we only use:
* λ-function (`\argument_name. body_term`)
* variable (`variable_name`)
* application (`applied_term argument_term`)

And that gives us a Turing-complete language.

The only thing left to mention is that expressions can be evaluated in any order, and in our case, the order of evaluation is as lazy as possible.
e. g. when evaluating `(\x. \y. y) (...)`, the `...` term will not be evaluated at all as it is not used.
Thus, only the necessary calculations occur, which is sometimes necessary to avoid endless calculations.
