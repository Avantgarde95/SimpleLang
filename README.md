# SimpleLang

### Introduction
- "a SIMPLE LANGuage"
- Small toy language I made for studying some ideas about programming language.
- Procedural, Functional, Lazy language
- ~~I'm still writing the documentation; So if you are interested in this language,
please see the example codes. I'll upload the documentation soon.~~
This language is very slow and has many bugs (since this was originally for studying...);
My thought is that I'll not try to update the language and write the detail documentation...
so I just wrote a simple documentation about the syntax below.
For the built-in functions, please see `src/lib/builtin.py`.

### Syntax
I used the syntax similar to S-expression used in Scheme-like languages.
- `Regex [a-zA-Z_][a-zA-Z0-9_]*` - `int` object (ex. `34`, `-245`, `+33`)
- `Regex [-+]?\d+\.\d+` - `float` object (ex. `34.5`, `-23.40`, `+0.3`)
- `Regex [a-zA-Z_][a-zA-Z0-9_]*` - `name` object (ex. `myVar`, `_myVar`, `add_numbers`)
- `'<characters>' or "<characters>"` - `str` object (ex. `'abc\n'`, `"def\n"`)
(Escape sequences `\n`, `\t`, `\0`, `\r`, `\a`, `\b`, `\'`, `\'"`, `\\` are supported.) 
- `(<expr1> <expr2> ...)` - `list` object (of elements <expr1>, <expr2>, ...)
- `$<expr>` - An operator called 'evaluator'
  - `$<name>` - Return the value of the variable with such name.
  - `$(<expr1> <expr2> <expr3> ...)` - Call the function with name <expr1> and return the result.
  - `$<other expressions>` - Do nothing. (Just return itself.)

### Remarks
In this language, list object is 'lazy', which means that each element
in the list is not evaluated before request. For example, the code

```$(output ($(add 4 2) 3))```

returns

```(<Code eval : <Code list : [<Code name : add>, <Code int : 4>, <Code int : 2>]>> <Code int : 3>)```

You can use the function `early` to do eager evaluation. For example, the code

```$(output $(early ($(add 4 2) 3)))```

returns

```(6 3)```

For the function `output`, you can use `print` function to apply eager evaluation easily.
```$(print <expr>)``` is equivalent to ```$(output $(early <expr>))```, so you can
rewrite the code like the following:

```$(print ($(add 4 2) 3))```

### Requirement
Python 2.7 (Not tested on <= 2.6)

### Dependency
I used [PLY](http://www.dabeaz.com/ply/) to implement the parser. PLY is included in `src/lib/ply`.
