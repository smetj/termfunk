<p align="center">
<img src="https://raw.githubusercontent.com/smetj/termfunk/master/docs/_static/logo-readme.png">
</p>
<h2 align="center">Python functions from the terminal.</h2>


TermFunk is a lightweight framework to organize, access and execute your
Python functions from the terminal.

TermFunk is a convenience wrapper to bring Python closer to your terminal so
you can develop script logic in Python whilst keep using your favorite
terminal as you know it.  Python function parameters are automatically mapped
to command parameters which can be provided on the command line, through
environment variables or interactively.

The docstring of each version is exposed by issuing `--help`.

---

## Installation and usage

### Installation

*TermFunk* needs Python3 and can be installed by running:

  `pip install termfunk`

### Configuring Bash autocompletion

TermFunk has support builtin to configure Bash autocompletion.

Assuming you have saved your script to `/usr/local/bin/fnc`, add the following
command to your `.bashrc` file:

  `eval "$(/usr/share/bin/fnc complete)"`

The `complete` command prints a Bash script to STDOUT which can be eval'ed to
fully configure Bash completion for your defined functions and their
parameters.

### Usage

TermFunk is a baseclass for the class you write containing your functions:

```Python
#!/usr/bin/env python

from termfunk import TermFunk
from termfunk import Ask
from termfunk import Choice
from termfunk import File


class MyFunctions(TermFunk):
    def function_greet(self):
        """
        Just say hello!
        """

        for _ in range(10):
            print("Hello World!")

    def function_parameterdemo(
        self,
        url=Ask(),
        username=Ask(),
        password=Ask(secret=True),
        value=Choice(["a_one", "a_two", "b_three"]),
    ):
        """
        Demo access to parameters
        """
        print(
            "I will request url '%s' with username '%s' and password '%s' using values '%s'."
            % (url, username, password, value)
        )

    def function_validate(
        self,
        file=File(),
    ):
        """
        Validates file
        """
        print("I will validate file %s" % (file))


def main():

    MyFunctions()


if __name__ == "__main__":
    main()
```
---

After the script has been saved as "demo" and made executable is can be executed as such:

```bash
$ ./demo --help
usage: demo [-h] {list,greet,parameterdemo} ...

TermFunk

positional arguments:
  {list,greet,parameterdemo}

optional arguments:
  -h, --help            show this help message and exit

```

---

Executing the function from your terminal is simple as:

```bash
$ ./demo greet
Hello World!
Hello World!
Hello World!
Hello World!
Hello World!
Hello World!
Hello World!
Hello World!
Hello World!
Hello World!
```

---

Accessing help with information about the function and its parameters can be done using `--help`.
Each parameter shows how it can retrieve information.

```bash
./demo parameterdemo --help
usage: demo parameterdemo [-h] [--url URL] [--username USERNAME]
                          [--password PASSWORD]

Demo access to parameters

optional arguments:
  -h, --help           show this help message and exit
  --url URL            : <$DEMO_URL> or <Interactive>
  --username USERNAME  : <$DEMO_USERNAME> or <Interactive>
  --password PASSWORD  : <$DEMO_PASSWORD> or <Interactive>
```

---

Parameters values can be provided during execution:

```bash
$ ./demo parameterdemo --url http://hello --username john --password doe
I will request url 'http://hello' with username 'john' and password 'doe'.
```

---

Parameter values can be set by environment variables.
Each variable is in uppercase and is prefixed with the name of the script:

```bash
$ export DEMO_URL="http://some-place-in-the-clouds"
$ ./demo parameterdemo --username john --password doe
I will request url 'http://some-place-in-the-clouds' with username 'john' and password 'doe'.
```

---

If a parameter value is retrieved from an environment variable `--help` will tell you that:

```bash
$ ./demo parameterdemo --help
usage: demo parameterdemo [-h] [--url URL] [--username USERNAME]
                          [--password PASSWORD]

Demo access to parameters

optional arguments:
  -h, --help           show this help message and exit
  --url URL            : <$DEMO_URL http://some-place-in-the-clouds>
  --username USERNAME  : <$DEMO_USERNAME> or <Interactive>
  --password PASSWORD  : <$DEMO_PASSWORD> or <Interactive>
```

---

If you define ```Ask(secret=True)``` TermFunk will obfuscate that value in the
`--help` output:

```bash
$ export DEMO_PASSWORD="some secret value"
$ ./demo parameterdemo --help
usage: demo parameterdemo [-h] [--url URL] [--username USERNAME]
                          [--password PASSWORD]

Demo access to parameters

optional arguments:
  -h, --help           show this help message and exit
  --url URL            : <$DEMO_URL http://some-place-in-the-clouds>
  --username USERNAME  : <$DEMO_USERNAME> or <Interactive>
  --password PASSWORD  : <$DEMO_PASSWORD **********>
```

---

If you don't define a parameter value on CLI then you can provide them
interactively. Since all other parameters are know at this stage, only the
unknown ones are asked for.

```bash
$ ./demo parameterdemo
Value for username: Happy Cat
I will request url 'http://some-place-in-the-clouds' with username 'Happy Cat' and password 'some secret value'.
```

---

You can define a set of predefined parameter values which can be auto-
completed using the `Choice()` type:

```bash
$ ./demo parameterdemo --value a_<tab>
a_one a_two
```

---

File completion can be triggerd by assigning the `File()` to the desired parameter.

```bash
$ ./demo validate --name <tab>
demo .git .gitignore setup.py
```

---

## Change Log

### 0.3.0

* Added type `File()` offering file completion.

### 0.2.0

* Removed `list` command in favor of `complete`
* Added `complete` command which returns a Bash completion config which can
  be eval'ed.
* Fixed bug where functions without a doc-string would break the script.
* Added `Choice` type allowing you to auto-complete predetermined values.

### 0.1.0

* Initial commit.
