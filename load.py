import glob, sys, os
import re, time
import MySQLdb


numeric_pattern = '[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?'
numeric_regex = re.compile(numeric_pattern)

def processHeaderLine(line):
    #print (line.strip("\"").split("=", 1))
    pass

def processResultLine(fields, columns, conn):
    if len(fields) != len(columns):
        print("field count does not match column count. aborting")

    columns = [(column.strip().strip("\"")) for column in columns]

    sql = "insert into results ("
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
    #print(sql)
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()
    conn.commit()

def processFile(file):
    resultCount = 0
    start = time.time()
    conn = None
    try:
        conn = MySQLdb.connect (host = "localhost",
                                user = "root",
                                passwd = "",
                                db = "gpr")
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit (1)

    columns = None
    global data

    # Parse the first 2 lines of the file to get the number
    # of header rows and the number of data columns
    atf_version_line = file.readline() # not used
    headers_columns = file.readline().split()
    header_rows = headers_columns[0]
    data_columns = headers_columns[1]

    # Process the header lines
    header_data = []
    for x in range(int(header_rows)):
        header = file.readline()
        header_data.append(header.split("="))
        print (header_data)
        #print (header.split("="))

    # Build a list of coumns
    columns = file.readline().split("\t")
    print (columns)

    # Process the data rows
    while 1:
        line = file.readline()
        if not line:
            break
        processResultLine(line.split("\t"), columns, conn)
        resultCount = resultCount + 1
        #print("line: " + line)
        if resultCount > 10:
            break

    elapsed = (time.time() - start)
    print ("processed " + str(resultCount) + " results in " + str(elapsed))
    conn.close()
    
def main(argv):
    arg = argv[0]
    if os.path.isfile(arg):
        processFile(open(arg, 'r'))
    elif os.path.isdir(arg):
        for p in glob.iglob(arg + '/*'):
            processFile(open(p, 'r'))


if __name__ == "__main__":
   sys.exit(main(sys.argv[1:]))
