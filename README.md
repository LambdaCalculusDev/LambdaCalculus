# λ-Calculus Interpreter v0.0.1

λ-calculus is the simplest functional programming language.

In λ-calculus, "function" means "abstraction from something". For example, instead of `2 + 1`, you can write `\X. X + 1`, and then substitute an arbitrary object for `X`.

This concept of "function" (or, more correctly, "abstraction") is so fundamental, [every](https://en.wikipedia.org/wiki/Abstraction_principle_(computer_programming)) programming language implements it more or less explicitely, as it's necessary to avoid code duplication and allow code reuse. So, in some sense, λ-calculus directly follows from [DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself) itself.

At the same time, you can express any computation or idea by solely using "functions". This is the only mechanism λ-calculus relies on. No built-in numbers or strings, no control flow statements.

So, "abstraction from something" is not only necessary, but it's also sufficient. This is what makes λ-calculus so important and beautiful.

## Usage Example

To run λ-program you can use this command in your terminal:
```sh
python3 main.py code.lambda
```

Then your λ-expression will be fully evaluated and the program will print the result.

## Program Example

This is an example of a λ-program:
```
three := \f. \x. f (f (f x));
square := \num. \f. num (num f);
square three
```

You can find more examples here: https://en.wikipedia.org/wiki/Church_encoding

## Language Overview

In general, a λ-program consists of several definitions followed by a main expression that is the target for evaluation.

In fact, definitions (:=) are just syntactic sugar over λ-expressions, and they are not required at all.

Their main purpose is to simplify the beginner experience.

### λ-expression

So, the real basis of λ-calculus is λ-expression.

And you're probably already familliar with it.

Take a look at this example:
```
\f. \x. f (f (f x))
```

It can be roughly translated into Python like this:
```
lambda f: lambda x: f(f(f(x)))
```

`f x y z` can be interpreted as `f(x, y, z)`.
But actually it is `f(x)(y)(z)`, since this is how argument passing works in λ-calculus. We don't need the concept of multiple arguments.

So, we only use:
* λ-function (`\argument_name. body_term`)
* variable (`variable_name`)
* application (`applied_term argument_term`)

And that gives us a Turing-complete language.

### Evaluation Order

λ-calculus also supports unusual evaluation order.

For example, if you type `(\x. \y. y) (...)`, the contents of `(...)` never matter or being touched. It's like an "if" statement with condition being false.

Thus, only the necessary calculations occur, allowing us to work with infinite constructions that in other languages ​like Python would result in an endless loop.
