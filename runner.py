#!/usr/bin/env python
"""
Based on https://gist.github.com/tinybike/410b7803bc7bcd69fb20 by
@author jack@tinybike.net
With help from http://stackoverflow.com/a/17245651
"""
import csv
import datetime
import pymssql
from decimal import Decimal
import sys
import os
import cStringIO
import codecs
import platform

# Connect to MSSQL Server
params = dict(server=os.environ.get('SERVER', "SERVER:PORT"),
                       user=os.environ.get('USER', "USERNAME"),
                       password=os.environ.get('PASSWORD', "PASSWORD"),
                       database=os.environ.get('DATABASE', "DATABASE"))
sys.stderr.write("Using params: %s\n" % repr(params))

conn = pymssql.connect(**params)

# Create a database cursor
cursor = conn.cursor()

# Replace this nonsense with your own query :)
with open('/query.sql', 'r') as f:
    query = f.read()

sys.stderr.write("query:\n%s\n\nExecuting query..." % query)

# Execute the query
cursor.execute(query)
sys.stderr.write("done.\n")

class UTF8Recoder:
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)
    def __iter__(self):
        return self
    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)
    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]
    def __iter__(self):
        return self

class UnicodeWriter:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()
    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") if type(s) == unicode else s for s in row])
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        data = self.encoder.encode(data)
        self.stream.write(data)
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# Go through the results row-by-row and write the output to a CSV file
# (QUOTE_NONNUMERIC applies quotes to non-numeric data; change this to
# QUOTE_NONE for no quotes.  See https://docs.python.org/2/library/csv.html
# for other settings options)
i = 0
output = "/output.csv"
    
with open(output, 'w') as out:
    writer = UnicodeWriter(out, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow([d[0] for d in cursor.description]) # write header
    for row in cursor:
        i += 1
        writer.writerow(row)

sys.stderr.write("done.\nWrote %d rows.\n" % i)
sys.stderr.write("You might want to do\ndocker cp %s:/output.csv .\n" % platform.node())

# Close the cursor and the database connection
cursor.close()
conn.close()

