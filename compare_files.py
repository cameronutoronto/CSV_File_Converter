file1 = open("temp2.txt", 'r')
file2 = open("convert_csv - Working.py", 'r')
line1 = file1.readline()
line2 = file2.readline()
flag = True
percent = 0.0
number = 0.0
while (line1 != "" and line2 != ""):
    if line1 != line2:
        flag = False
        number += 1.0
    else:
        percent += 1.0
        number += 1.0
    line1 = file1.readline()
    line2 = file2.readline()
percent = percent / number
if flag:
    print "The files are identical"
else:
    print "The files are different"
    print "Percent Identical: ", percent * 100, "%"
