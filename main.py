# This python script will read in the arguments 
import csv, sys, getopt

def main(argv):
    # Initialize variables
    T = 0
    P = 0
    v = 0
    u = 0
    h = 0
    s = 0

    # Read arguments

    try:
        opts, args = getopt.getopt(argv, "T:P:v:u:h:s:")
    except getopt.GetoptError as err:
        print("Needs at least two intensive properties: main.py -P <pressure> -T <temp>")
        print(err)
        sys.exit(-1)
    for opt, arg in opts:
        if opt == "-P":
            P = float(arg)
        elif opt == "-T":
            T = float(arg)
        elif opt == "-v":
            v = float(arg)
        elif opt == "-u":
            u = float(arg)
        elif opt == "-h":
            h = float(arg)
        elif opt == "-s":
            s = float(arg)
        else:
            assert False, "unhandled option"

    # Search for values in table

    ## Read csv file
    table = []
    with open("tableA6.csv", 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            table.append(row)


    ## If P and T are known, interpolate to find table values
    tablevals = []
    if P > 0 and T > 0: 
         for index, row in enumerate(table):
             if float(table[index][0]) == P and float(table[index][1]) == T:
                tablevals = row


    # Print out the results

    output = "P = {}, T = {}, v = {}, u = {}, h = {}, s = {}"
    output = output.format(tablevals[0], tablevals[1], tablevals[2], tablevals[3], tablevals[4], tablevals[5])
    print(output)

def interpolate(x, x0, y0, x1, y1):
    return y0 + (x - x0) * (y1 - y0) / (x1 - x0)

if __name__ == "__main__":
    main(sys.argv[1:])
