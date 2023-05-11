# Echoclean

A utility to help apply expert rules to sonobat output. However, the program
is intended to be quite general, and can likely be applied to outputs from other
automatic classifiers that produce spreadsheet-like outputs.

## Dependencies:

-   openpyxl (version 2.5.14, not newer!)
-   click

## Installation

### MacOS / Linux installation instructions:

Install [Python](https://www.python.org/) on your computer.

Make sure to check box to add Python to Path.

Install echoclean:

```bash
pip install echoclean
```

Verify that `echoclean` installed correctly by typing the following in
your terminal of choice (CMD prompt on Windows):

```
echoclean
```

This should show:

```
Usage: echoclean [OPTIONS] COMMAND [ARGS]...
```

and not an error.

### Windows installation instructions:

Install [Python](https://www.python.org/) on your computer.

Make sure to:

-   Check box to add Python to Path
-   Use Customize Installation
-   Be sure that box to install Pip is checked
-   Advanced Options: be sure box to Add Python to Environment variables is checked
-   Specify the directory to which you want Python installed so that you can find it if needed
    (e.g., to `~\Programs\Python\Python310\`)

Run the CMD prompt by typing "CMD" from Windows search.

Verify that `Python` is installed correctly by typing the following in the CMD
prompt:

```
python --version
```

This should show the Python version and not an error.

Verify that `pip` installed correctly by typing the following in the CMD prompt:

```
pip --version
```

This should display the version number and not an error.

Retrive the list of places where python and packages are installed by typing
the following in the CMD prompt:

```
python -c "import site; print(site.getsitepackages())"
```

This will return a list of directories.

Update the System PATH environment variable to include the following directories. Follow the instructions [here](https://www.wikihow.com/Change-the-
PATH-Environment-Variable-on-Windows) to update environment variables.

-   add each of the directories above, separated by a semicolon
-   add the Scripts subdirectory of Python; if you installed Python to `~\Programs\Python\Python310` this will be `~\Programs\Python\Python310\Scripts`

Now install echoclean by typing the following in the CMD prompt:

```
pip install echoclean
```

Verify that `echoclean` installed correctly by typing the following in the CMD
prompt:

```
echoclean
```

This should show

```
Usage: echoclean [OPTIONS] COMMAND [ARGS]...
```

and not an error.

### Development installation

Download or clone this repository, then run:

`python setup.py install`

## Usage

From the command line, within your activated Python environment:

```
Usage: echoclean apply [OPTIONS] RULES DATA OUTPUT

  Apply the rules to the input data.

Options:
  -v, --verbose  Verbose output
  --help         Show this message and exit.

```

Verbose option can be doubled `-v -v` to provide even more verbose output.

### Applying echoclean to Sonobat output

Save your rules to a known location on your computer (e.g., `C:\Users\YourName\Desktop\Sonobat\Rules`)

Open your command window and navigate to that directory. On windows, open your
CMD prompt by typing "CMD" in the Windows search box, and then type "cd <directory>" to navigate to that directory (replace <directory> with the actual
name of your directory above).

Then type the following:

```
echoclean apply "<rules>.xlsx" "<dataset>.csv"
```

where `<rules>` and `<dataset>` are the names of your rule spreadsheet and
Sonobat outputs respectively.

You will be prompted to select the worksheet in your rules workbook that contains the rules you want to apply.

This will create a new file called "<dataset>\_out.xlsx" in the same
directory as your rules (basically, replaces `.csv` with `_out.xlsx`).

TIP: Make sure that all the columns are correctly lined up in the Sonobat output

## How it works

Echoclean works by applying expert rules from the RULES file to the DATA file.
The files can be XLSX, CSV, or Tab-delimited. If XLSX and more than one sheet
is found, you will be prompted to select to correct sheet.

The program first compares the columns between the DATA and RULES files. Any
column that is present in both is used to construct a rule. Any column that is
found only in the RULE file is used as the result set when that rule is applied
to a row in DATA. Any column in the DATA file that is not found in the rules
is copied to the OUTPUT. This flexibility allows you to develop rules for nearly
any simple data that can be represented as row / column format.

_Note:_ if you run the OUTPUT of this program back through as DATA, you **must**
rename the columns from the result set, or they will be used for criteria and
produce unexpected results.

This program does not care how you name your columns, but for a rule to apply to
a column in DATA, the names must be exactly the same (including capitalization).
This program does not expect any particular column, but if it finds one called
'Filename' it will use that to attempt to parse out a datestamp (using Sonobat
format). These datestamps are then used to determine the night on which the
file was recorded, and any time before noon is assumed to be part of the previous
night.

Rules are applied in sequence, in the order they are read in from the file.

The OUTPUT file is always an XLSX spreadsheet with multiple sheets. One sheet
includes the classification results, which are each row from the DATA file,
preceded by the result set from the RULES file for the rule that classified
that row. For each column in the result set, an additional sheet is created with
the count of rows for each unique value of that result which was found in the
classification results.

## Rules

A rule is a collection of criteria that must be met to apply that rule. As soon
as a rule is applied, no other rules are tested.

It is convenient to think of rules as forming a dichotomous key; as a row from
DATA fails a given rule, it is tested against the next one, and thus does not
qualify against **ANY** of the preceding rules. Thus your rules can be additive
because you can safely assume that the row did not meet any of the prior criteria,
and you should construct your rules from the most strict to the least strict.

Example:

Given the following rules:

Rule 1 `Consensus: 'ANPA'`
Rule 2 `Consensus: 'MYLU'`

These will be evaluated such that any row from DATA that is tested against Rule 2
is implicitly **NOT** any of the criteria in Rule 1. So in this case, it is
equivalent to:

`Consensus is 'MYLU' AND NOT 'ANPA'`.

We recommend that you number your rules to assist with debugging. Doing so
makes it easier to visually compare the values in a given row to the rule
applied or expected.

_Note:_ this program does not check your rules for validity. You are
responsible for making sure that your rules are logically correct and in the
correct order.

### Criteria

The criteria must be matched against the data type of the column. Range or
equality comparisons are only appropriate for numeric types.

**any**
If a column is left blank in for a given rule, it allows any value for that
column in the data to match. You can also provide the value 'any' but this is
unnecessary.

**blank**
If you specify 'blank' for a column in a given rule, then that column must be
blank in the data for it to match.

**numeric types**
You can specify equality comparisons like these:

```
> 10
< 12
>= 40
<= 20
= 2
4 - 10   (equivalent to >= 4 AND <= 10)
```

**text types**
You can specify a list of possible values to compare against. The row in the data
only needs to contain one of them.

Example:

Rule 1 `Consensus: LANO, COTO, TABR, LACI, or Blank`

would match `COTO` but would not match `EPFU`. This is also a special
case where a blank would match, but any value not in the list would fail.

You can also use a negatory condition, but only one value is allowed:

`Consensus: Not EPFU`

## Contact us for help

If you need assistance installing or running echoclean, please [contact us](mailto:bcward@astutespruce.com).
