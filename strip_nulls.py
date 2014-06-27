#Replace all instances of NULL from strip_file with an empty string
#strip_file is assumed to be CSV!
import os
strip_file = "temp2.txt"
temp_file = "temp_for_strip_70034534-63460-36982346344745754747.txt"
in_file = open(strip_file, "r")
out_file = open(temp_file, "w")
temp = in_file.readline()
while temp != '':
    temp = temp.split(',')
    temp2 = ''
    for x in range(len(temp)):
        if temp[x] == "NULL":
            temp[x] = ''
        temp2 += temp[x]
        if x < len(temp) - 1:
            temp2 += ','
    out_file.write(temp2)
    temp = in_file.readline()
in_file.close()
out_file.close()
in_file = open(temp_file, "r")
out_file = open(strip_file, "w")
temp = in_file.readline()
while temp != '':
    out_file.write(temp)
    temp = in_file.readline()
in_file.close()
out_file.close()
os.remove(temp_file)
