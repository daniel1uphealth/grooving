grooving.py is a grammar parser that reads Groovy snippets and produces something that resembles English.

# Usage:

   python3 grooving.py [filename]

For example:

   python3 grooving.py input.csv >output.csv 2>errors.csv

If a filename is given, grooving.py will read from that file. If no filename is given, grooving.py will read from stdin. The translations for successfully parsed rows from the source data will be output to stdout. Rows that cannot be parsed will be written to stderr (prepended with '!!!') with a short explanation. In both cases the output will include an additional column added to the start of each row that is the row number from the source file.

grooving.py requires the PLY library. Before you can use grooving.py, you'll have to pip install ply.

# Quirks
grooving.py has some intentional quirks:

* If a statement starts with '_.', the '_.' will be dropped in the translation to simplify the output, e.g. '_.CIP00781' will translate as 'CIP00781'.

There are several known cases that grooving.py cannot parse:

* Inline function definitions - probably could be parsed, but a function definition is too hard to translate usefully into English.
* Regular expressions - really hard to parse, and impossible to translate usefully into English
* Casts, e.g. 'x as Integer' - can be ignored in the translation and not that hard to parse
* Use of '|' for boolean comparison - I'm pretty sure that's a syntax error and should instead be '||'. If we want to support it, it's easy to parse.
* Assignments - some rules use assignments to simplify, like 'date = new Date();'. Translating to English would be too hard.
* Comments - some lines appear to be commented out, e.g. start with '//'. Not sure how to parse or even what to do with that.

# Debugging

If there's a line that cannot be parsed, the easiest way to debug why is to use the '-X' switch.  For example:

   python3 grooving.py -X '"TPL","Coverage","coverage[coverageSegment@segment:TPL00003]","subscriberId","// coverageSegment.TPL034coverageSegment.TPL032"'

Note that the error output of grooving.py will add the row number of the data as a first column, which you should remove before passing the data in via the -X switch.
