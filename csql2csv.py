#!/usr/bin/env python
"""
csql2csv
Utility to convert a SQL dump to a CSV file.

Copyright 2015 Sam Saint-Pettersen.
Licensed under the MIT/X11 License.

Use -h switch for usage information.
"""
import sys
import os
import re
import argparse

signature = 'csql2csv 1.0 (https://github.com/stpettersens/csql2csv)'

def displayVersion():
	print('\n' + signature);

def displayInfo():
	print(__doc__)

def csql2csv(file, out, separator, tz, verbose, version, info):

	if len(sys.argv) == 1:
		displayInfo()
		sys.exit(0)

	if file == None and out == None:
		if verbose == False and version == True and info == False:
			displayVersion()

		elif verbose == False and version == False and info == True:
			displayInfo()

		sys.exit(0)

	if out == None: out = re.sub('.sql', '.csv', file)

	if file.endswith('.sql') == False:
		print('Input file is not a SQL dump.')
		sys.exit(1)

	if out.endswith('.csv') == False and out.endswith('.tsv') == False:
		print('Output file is not a CSV or TSV file.')
		sys.exit(1)

	if separator == None: separator = ','

	if out.endswith('.tsv'): separator = '\t'

	head, tail = os.path.split(file)
	collection = re.sub('.sql', '', tail)

	f = open(file, 'r')
	lines = f.readlines()
	f.close()

	# Preprocess SQL dump so that it is compatible for conversion.
	processed_lines = []
	for line in lines:
		l = line.lstrip()
		if l.startswith('--') or l.startswith('/*'): continue # Strip out comments.
		l = re.sub('VALUES \(', 'VALUES (\n', l)
                l = re.sub(',', ',\n', l)
                l = re.sub('\),', ')\nINSERT INTO `null` VALUES (\n', l)
		l = re.sub('\n\n', '\n', l)
		processed_lines.append(l);
	processed_lines = ''.join(processed_lines).split('\n')
	if lines[0].startswith('--!'): processed_lines = lines
	lines = []
	x = 0
	while x < len(processed_lines):
		processed_lines[x] = processed_lines[x].lstrip('(')
		x = x + 1

	fields = []
	inserts = []
	headers = False
	for line in processed_lines:

		pattern = re.compile('CREATE TABLE|UNLOCK TABLES')
		if pattern.match(line):
			headers = True

		m = re.search('(^[\`a-zA-Z0-9_]+)', line)
		if m and headers:
			f = m.group(1)
			f = re.sub('\`', '', f)
			f = re.sub('CREATE|ENGINE|INSERT', '', f)
			if len(f) > 0: fields.append(f)

		pattern = re.compile('INSERT INTO')
		if pattern.match(line):
			headers = False

		value = ''
		m = re.search('(^[\d.]+)', line)
		if m and headers == False:
			value = m.group(1)

		m = re.search('(\'[\w\s]+\')', line, re.IGNORECASE)
		if m and headers == False:
			value = m.group(1)

		m = re.search('(^[\d\"\'\w\_\.][^(DROP)][^(INSERT)][^\n|,|)]+)', line)
		if m and headers == False:
			value = m.group(1)

			pattern = re.compile('\'[\d\w]{24}\'')
			if pattern.match(value):
				value = 'ObjectId(' + value + ')'

			pattern = re.compile('\'\d{4}\-\d{2}\-\d{2}')
			if pattern.match(value):
				value = re.sub('\s', 'T', value)
				value = value[:-1]
				value += '.000'
				if tz: value += 'Z\''
				else: value += '+0000\''

		if len(value) > 0: inserts.append(value)
	
	fn = len(fields)
	x = 0
	rrecords = []
	inserts = ['@@'.join(inserts[i:i+fn]) for i in range(0, len(inserts), fn)]

	for insert in inserts:
		records = insert.split('@@')
		x = 0
		for record in records:
			r = re.sub('\'', '', record)
			r = re.sub('\"', '', r)
			rrecords.append(r)
			x = x + 1

	rrecords = ['@@'.join(rrecords[i:i+fn]) for i in range(0, len(rrecords), fn)]

	if verbose:
		print('\nGenerating CSV file: \'{0}\' from\nSQL dump file: \'{1}\''
		.format(out, file))

	f = open(out, 'w')
	f.write(separator.join(fields) + '\n')
	for record in rrecords:
		record = re.sub('@@', separator, record)
		f.write(record + '\n')

	f.close()


# Handle any command line arguments.
parser = argparse.ArgumentParser(description='Utility to convert a SQL dump to a CSV file.')
parser.add_argument('-f', '--file', action='store', dest='file', metavar="FILE")
parser.add_argument('-o', '--out', action='store', dest='out', metavar="OUT")
parser.add_argument('-s', '--separator', action='store', dest='separator', metavar="SEPARATOR")
parser.add_argument('-t', '--tz', action='store_true', dest='tz')
parser.add_argument('-l', '--verbose', action='store_true', dest='verbose')
parser.add_argument('-v', '--version', action='store_true', dest='version')
parser.add_argument('-i', '--info', action='store_true', dest='info')
argv = parser.parse_args()

csql2csv(argv.file, argv.out, argv.separator, argv.tz, argv.verbose, argv.version, argv.info)
