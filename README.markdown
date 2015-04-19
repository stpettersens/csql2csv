# csql2csv
Utility to convert a SQL dump to a CSV or TSV file.

Usage: `csql2csv -f data.sql -o data.csv|tsv`

Tested with:
* Python 2.7.9, PyPy 2.5.1 and IronPython 2.7.5 (works).
* Jython 2.5.3 (use Jython tweaked version): 
* `jython csql2csv.jy.py -f data.sql -o data.csv|tsv`
