# This python script will read in the arguments 
import csv, sys, getopt
import numpy as np

table = []

def main(argv):
    # Initialize variables
    P = 1.6
    T = 400
    v = 0
    u = 0
    h = 0
    s = 0
    tablevals = [P, T, v, u, h, s]

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

    ## Read csv file
    #table = []
    with open("tableA6.csv", 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            table.append(row)
    
    ## See which properties are given
    knownIndices = [i for i,v in enumerate(tablevals) if v > 0] # array that contains column indices of known values
    i1 = knownIndices[0] # [0,1] <- 0=P, 1=T
    i2 = knownIndices[1] # [1,2,3,4,5] <- 1=T, 2=v, 3=u, 4=h, 5=s
    li = 0 # index of the property that linear interpolation will be based on (x)
    
    # As T increases (const. P): v, u, h, and s all increase 
    # As P increases (const. T): v and s decrease, u and h increase
            
    upperRow = []
    lowerRow = []
    uniqueP = [1.0,1.2,1.4,1.6,1.8,2.0,2.5,3,3.5,4,4.5,5]
    
    if P != 0: # P given; double interpolation
        pMin = 0
        pMax = 0
        
        for i in range(len(uniqueP)): # find upper and lower P
            if uniqueP[i] > P:
                pMax = uniqueP[i]
                pMin = uniqueP[i-1]
                break
            elif P == 5:
                pMax = 5
                pMin = 4.5
                break
                
        # using P_tables, find upper and lower rows for other value
        upperP_Table = getPTable(pMax)
        lowerP_Table = getPTable(pMin)
        
        finalUpper = [pMax, T, v, u, h, s]
        finalLower = [pMin, T, v, u, h, s]
        
        upperRow = SearchP(upperP_Table, tablevals[i2], i2, finalUpper)
        lowerRow = SearchP(lowerP_Table, tablevals[i2], i2, finalLower)
                
    else: # T given, but not P
        if T_found(T):
            li = i2
            T_table = getTTable(T) # P in ascending order
            
            # look for upper and lower rows given another property (v, u, h, or s)
            for index, row in enumerate(T_table):
                if i2 == 3 or i2 == 4: # the other property is u or h (increases with P)
                    if float(T_table[index][i2]) >= tablevals[i2]:
                        upperRow = row
                        lowerRow = T_table[index-1]
                        break
                else: # the other property is v or s (decreases with P)
                    if float(T_table[index][i2]) <= tablevals[i2]:
                        upperRow = row
                        lowerRow = T_table[index-1]
                        break
        #else:
    
    ## Convert upper/lower rows to float
    upperRowList = [float(item) for item in upperRow]
    lowerRowList = [float(item) for item in lowerRow]
    
    ## Final Interpolation
    for i in range(len(tablevals)):
        if tablevals[i] == 0:
            tablevals[i] = round(interpolate(tablevals[li], lowerRowList[li], lowerRowList[i], upperRowList[li], upperRowList[i]), 5)
    
    ## Print out the results
    output = "P = {}, T = {}, v = {}, u = {}, h = {}, s = {}"
    output = output.format(tablevals[0], tablevals[1], tablevals[2], tablevals[3], tablevals[4], tablevals[5])
    print(output)
    print("")
    print("Units: [P, T, v, u, h, s] = [MPa, m^3/kg, kJ/kg, kJ/kg, kJ/(kg*K)]")

    
    
def interpolate(x, x0, y0, x1, y1):
    return y0 + (x - x0) * (y1 - y0) / (x1 - x0)

def getPTable(p):
    a = [] # table that contains only rows that = P
    for index, row in enumerate(table):
        if float(table[index][0]) == p:
            a.append(row)
            
    return a

def getTTable(t):
    a = [] # table that contains only rows that = T
    for index, row in enumerate(table):
        if float(table[index][1]) == t:
            a.append(row)
            
    return a

def P_found(p): # returns True if P is in [1.0,1.2,1.4,1.6,1.8,2.0,2.5,3,3.5,4,4.5,5]
    for index, row in enumerate(table):
        if float(table[index][0]) == p:
            return True

def T_found(t): # returns True if T is in the table (225, 250, 300, 350, etc.)
    for index, row in enumerate(table):
        if float(table[index][1]) == t:
            return True
        
# searches table for upper and lower rows of other value; interpolates
# returns one row where [p,T,..,..,..,..], or [p,..,u,..,..,..], etc.
def SearchP(pt, val, col, finalRow): # pt: p table; val: other given value; col: index of column given
    upperRow_temp = []
    lowerRow_temp = []
    
    for index, row in enumerate(pt):
        if pt[index][col] == "":
            pass
        elif float(pt[index][col]) >= val:
            upperRow_temp = row
            lowerRow_temp = pt[index-1]
            break
    
    # convert upper/lower rows to float
    upperRow = [float(item) for item in upperRow_temp]
    lowerRow = [float(item) for item in lowerRow_temp]
    
    # interpolate
    for i in range(len(finalRow)):
        if finalRow[i] == 0:
            finalRow[i] = round(interpolate(finalRow[col], lowerRow[col], lowerRow[i], upperRow[col], upperRow[i]), 5)
    
    return finalRow
    

if __name__ == "__main__":
    main(sys.argv[1:])
