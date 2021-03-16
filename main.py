# This python script will read in the arguments 
import csv, sys, getopt
import numpy as np

table = []

def main(argv):
    # Initialize variables
    P = 0
    T = 0
    v = 0
    u = 0
    h = 0
    s = 0
    tablevals = [P, T, v, u, h, s]
    
    print("tablevals (before): " + str(tablevals)) #testing

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
    
    print("known indices: " + str(knownIndices)) #testing
    
    
    # 1) P given, T given -> find out which one is already given in the table (if not P then T)
        # 1.1) Both found, no need for interpolation
        # 1.2) P found, interpolate using T
        # 1.3) T found, interpolate using P
        
    # 2) P given, other property given -> same thing (P is probably in the table)
        # 2.1) Both found, no need for interpolation
        # 2.2) P found, interpolate using other property
            # Gather rows where table[,0] = P, then find upper/lower rows of other property
        # 2.3) P not found, interpolate using P
            # Probably won't have to do since no two rows have the same values for other property, but there are multiple rows with the same P.
            # Just interpolate with P?
            
    # 3) T given, other property given -> same thing (T is probably in the table)
        # 3.1) Both found, no need for interpolation
        # 3.2) T found, interpolate using other property
            # Gather rows where table[,1] = T, then find upper/lower rows of other property
        # 3.3) T not found, interpolate using T
            # Probably won't have to do since no two rows have the same values for other property, but there are multiple rows with the same T.
            # Just interpolate with T?
    
    # As T increases (const. P): v, u, h, and s all increase 
    # As P increases (const. T): v and s decrease, u and h increase
            
    
    upperRow = []
    lowerRow = []
    
    ## Find rows to use for interpolation
    if i1 == 0: # P given
        if P_found(P):
            li = i2
            P_table = getPTable(P) # T in ascending order
            
            # look for upper and lower rows given another property
            for index, row in enumerate(P_table):
                if float(P_table[index][i2]) >= tablevals[i2]:
                    upperRow = row
                    lowerRow = P_table[index-1]
                    break
                
        else: # assume T is probably in the table -> get table with just T
            li = i1
            T_table = getTTable(T)
            
            # look for upper and lower rows given another property (P)
            for index, row in enumerate(T_table):
                if float(T_table[index][0]) >= tablevals[0]:
                    upperRow = row
                    lowerRow = T_table[index-1]
                    break
                
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
            # don't know what to do
    
    ## Convert upper/lower rows to float
    upperRowList = [float(item) for item in upperRow]
    lowerRowList = [float(item) for item in lowerRow]
    
    print("lower row: " + str(lowerRowList)) #testing
    print("upper row: " + str(upperRowList))
    print("li: " + str(li))
    
    ## Interpolate
    for i in range(len(tablevals)):
        if tablevals[i] == 0:
            tablevals[i] = round(interpolate(tablevals[li], lowerRowList[li], lowerRowList[i], upperRowList[li], upperRowList[i]), 5)
            
    print("tablevals (after): " + str(tablevals)) #testing      
    print("")
    
    ## Print out the results
    output = "P = {} MPa, T = {} °C, v = {} m^3/kg, u = {} kJ/kg, h = {} kJ/kg, s = {} kJ/(kg*K)"
    output = output.format(tablevals[0], tablevals[1], tablevals[2], tablevals[3], tablevals[4], tablevals[5])
    print(output)

    
    
def interpolate(x, x0, y0, x1, y1):
    return y0 + (x - x0) * (y1 - y0) / (x1 - x0)

def getPTable(p):
    a = [] # table that contains only rows that = P
    for index, row in enumerate(table):
        if float(table[index][0]) == p:
            a.append(row)
            
    return a

def getTTable(t):
    a = [] # table that contains only rows that = P
    for index, row in enumerate(table):
        if float(table[index][1]) == t:
            a.append(row)
            
    return a

def P_found(p): # returns True if P is in [1.0,1.2,1.4,1.6,1.8,2.0,2.5,3,3.5,4,4.5,5]
    for index, row in enumerate(table):
        if float(table[index][0]) == p:
            print("P found") #testing
            return True

def T_found(t): # returns True if T is in the table (225, 250, 300, 350, etc.)
    for index, row in enumerate(table):
        if float(table[index][1]) == t:
            print("T found") #testing
            return True
    

if __name__ == "__main__":
    main(sys.argv[1:])
