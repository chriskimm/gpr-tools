"""
filter.py 
Runs a 2-parameter filter data stored in the filtered_results table
loaded by load.py
"""
import sys, os
import re, time
import MySQLdb
import gprconfig as config
import math

# Global
DELIMITER = "\t"
out = sys.stdout

def usage():
    print "Usage:  %s <MIN_NET_RED> <MIN_ARRAYS> [<OUTPUT_FILE>]" % os.path.basename(sys.argv[0])
    print "<MIN_NET_RED> is an integer    [required]"
    print "<MIN_ARRAYS> is an integer > 0 [required]"
    print "<OUTPUT_FILE> is a filename    [optional]"

def filter(argv):
    if len(argv) < 2:
        usage()
        sys.exit(2)

    min_val = int(argv[0])
    limit = int(argv[1])

    conn = None
    try:
        conn = MySQLdb.connect (host = config.host,
                                user = config.user,
                                passwd = config.password,
                                db = "gpr")
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit (1)
        
    # Get the list of experiments (files)
    sql = "SELECT filename FROM files"
    cursor = conn.cursor()
    cursor.execute(sql)    
    result = cursor.fetchall()
    files = []
    for record in result:
        files.append(record[0])

    # compare the number of loaded files to the "limit" argument
    lf = len(files)
    if limit > lf:
        print "Limit argument exceeds the number of loaded files, using: %d" % (lf,)
        limit = lf

    # write header row
    columns = ["UNIQID", "NAME", "GWEIGHT"]
    trimmed_files = [file.replace(".gpr","") for file in files]
    columns.extend(trimmed_files) 
    write (DELIMITER.join(columns)) 
    
    # write dummy "EWEIGHT" row
    columns = ["EWEIGHT", "", ""]
    columns.extend(["1" for x in range(len(files))])
    write (DELIMITER.join(columns)) 
    
    sql = "SELECT r.name, f.filename, r.`Ratio of Medians (635/532)`, r.`F635 Median - B635`, description "\
        "FROM filtered_results r, files f "\
        "WHERE r.file_id = f.id "\
        "AND r.`F635 Median - B635` >= %d "\
        "ORDER BY name;" % (min_val,)
    cursor = conn.cursor()
    cursor.execute(sql)

    # get the number of rows in the resultset
    numrows = int(cursor.rowcount)
    name = None
    values = {}
    for x in range(0, numrows):
        record = cursor.fetchone()
        if (record[0] != name or x == numrows-1) and len(values) >= limit:
            writeDataRow(files, name, values, record[4])
            values = {}
        if record[2] > 0:
            values[record[1]] = math.log(record[2]) / math.log(2)
        else:
            values[record[1]] = ""
        name = record[0]

    conn.close()

def writeDataRow(files, name, values, description):
    if not description:
        description = ""
    vals = [name, description, "1"]
    vals.extend([toStr(values.get(f)) for f in files])
    write (DELIMITER.join(vals))

def write(s):
    out.write(s)
    out.write("\n")
    out.flush()

def toStr(s):
    if s:
        return str(s)
    else:
        return ""

def main(argv):
    if (len(argv) > 2):
        try:
            global out
            out = open(argv[2], "w")
        except:
            sys.exit("error opening output file")
    filter(argv)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
