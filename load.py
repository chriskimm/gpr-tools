"""
load.py
Given a file or directory path as a command-line parameter, this script
loads data from gpr data into a database schema.  This db schema is created
by executing the create_scheme.sql script.
"""
import glob, sys, os
import re, time
import MySQLdb
import gprconfig as config

numeric_pattern = '[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?'
numeric_regex = re.compile(numeric_pattern)

def processResultLine(fields, columns, cursor, file_id):
    """
    Loads a row of gpr data into the results table
    """
    if len(fields) != len(columns):
        sys.exit("Field count does not match column count. Aborting")

    fields.insert(0, str(file_id))
    columns = [(column.strip().strip("\"")) for column in columns]

    sql = "insert into results (file_id, "
    sql += ", ".join([("`" + column.strip() + "`") for column in columns])
    sql += ") values ("

    for x in range(len(fields)):
        val = fields[x]
        if val.strip() == "":
            fields[x] = "null"
        elif val[0] != '"' and not numeric_regex.match(val):
            fields[x] = '"' + val + '"'

    sql += ", ".join(fields)
    sql += ")"
    cursor.execute(sql)

def processFile(file):
    """
    Load a gpr file into the database unless it has already
    been loaded.  Filename is used for the unique constraint.
    """
    start = time.time()
    conn = None
    try:
        conn = MySQLdb.connect (host = config.host,
                                user = config.user,
                                passwd = config.password,
                                db = "gpr")
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit (1)

    #columns = None

    fname = os.path.basename(file.name)
    print ("Loading data from file: %s" % (fname))

    # Parse the first 2 lines of the file to get the number
    # of header rows and the number of data columns
    atf_version_line = file.readline() # not used
    headers_columns = file.readline().split()
    header_rows = headers_columns[0]
    data_columns = headers_columns[1]

    # Process the header lines
    header_data = {}
    for x in range(int(header_rows)):
        header = file.readline().strip("\r\n\t\"")
        h_val = header.split("=")
        header_data[h_val[0]] = h_val[1]
    
    # Check to see if the current file has already been load
    select_sql = "select id from files where filename=\"%s\"" % (fname,)
    cursor = conn.cursor()
    cursor.execute(select_sql)
    data = cursor.fetchone()
    if data:
        print "--File %s has already been loaded.  Skipping it" % (fname,)
        return
    cursor.close()

    insert_sql = "insert into files (filename) values (\"%s\")" % (fname,) 
    cursor = conn.cursor()
    cursor.execute(insert_sql)
    file_id = cursor.lastrowid
    cursor.close()
    conn.commit()

    # Build a list of coumns names to be used when constructing
    # the sql insert statements
    columns = file.readline().split("\t")

    # Process the data rows
    cursor = conn.cursor()
    count = 0
    while 1:
        line = file.readline()
        if not line:
            break
        processResultLine(line.split("\t"), columns, cursor, file_id)
        count += 1
    cursor.close()
    conn.commit()
    elapsed = (time.time() - start)
    print ("--loaded %d rows in %d seconds" % (count, elapsed))

    # Filter data and load filtered data into the filtered_results table
    # From Charlie:
    # (('B532' <= 350) AND ('B635' <= 350)) AND
    # (('F532 % Sat.' <= 60) AND ('F635 % Sat.' <= 60)) AND
    # (('F532 CV' <= 80) AND ('F635 CV' <= 80)) AND
    # ('Flags' >= 0) AND
    # (('Dia.' >= 50) AND ('Dia.' <= 80)) AND
    # (('% > B532+2SD' >= 70) OR ('% > B635+2SD' >= 70)) AND
    # ('Substance Name' begins with 'f'))
    start = time.time()
    filter_sql = """
        INSERT INTO filtered_results (name, file_id, `Ratio of Medians (635/532)`, `F635 Median - B635`, description)
        SELECT ID, file_id, `Ratio of Medians (635/532)`, `F635 Median - B635`, Description FROM results 
        WHERE `B532` <= 350 AND `B635` <= 350 AND `F532 % Sat.` <= 60 
        AND `F635 % Sat.` <= 60 AND `F532 CV` <= 80 AND `F635 CV` <= 80
        AND FLAGS >= 0 AND `Dia.` >= 50 AND `Dia.` <= 80 
        AND (`% > B532+2SD` >= 70 OR `% > B635+2SD` >= 70)
        AND ID like 'f%'
        AND file_id =
        """
    filter_sql += str(file_id)
    cursor = conn.cursor()
    cursor.execute(filter_sql)
    elapsed = (time.time() - start)
    conn.commit()
    print ("--loaded filtered rows in %d seconds" % (elapsed,))
    cursor.close()

    # Clean-up
    conn.close()
    
def main(argv):
    arg = argv[0]
    if os.path.isfile(arg):
        processFile(open(arg, 'r'))
    elif os.path.isdir(arg):
        for p in glob.iglob(arg + '/*.gpr'):
            processFile(open(p, 'r'))


if __name__ == "__main__":
   sys.exit(main(sys.argv[1:]))
