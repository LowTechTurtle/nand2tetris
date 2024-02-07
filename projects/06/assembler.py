import sys
import re
C_instruction_list = {"0": "0101010", "1": "0111111", "-1": "0111010", "D": "0001100", "A": "0110000",
    "!D": "0001100", "!A": "0110001", "-D": "0001111", "-A": "0110011", "D+1": "0011111", "A+1": "0110111",
    "D-1": "0001110", "A-1": "0110010", "D+A": "0000010", "D-A": "0010011", "A-D": "0000111", "D&A": "0000000",
    "D|A": "0010101", "M": "1110000", "!M": "1110001", "-M": "1110011", "M+1": "1110111", "M-1": "1110010",
    "D+M": "1000010", "D-M": "1010011", "M-D": "1000111", "D&M": "1000000", "D|M": "1010101"}

symbol = {"R0": 0, "R1": 1, "R2": 2, "R3": 3, "R4": 4, "R5": 5, "R6": 6, "R7": 7, "R8": 8, "R9": 9,
    "R10": 10, "R11": 11, "R12": 12, "R13": 13, "R14": 14, "R15": 15, "SCREEN": 16384, "KBD": 24576,
    "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4}

file_in = open(sys.argv[1], mode='r')
# if user specify name of file out then we will use it, otherwise use default name
if len(sys.argv) == 2: 
    file_out = open(sys.argv[1].replace("asm", "hack"), "w")
else:
    file_out = open(sys.argv[2], "w")

#Get commands from file, strip all comment, remove white space and save it in lines variable
lines = []
for line in file_in:
    if re.match("^//.*", line.strip()):
        pass
    elif line.strip() == "":
        pass
    else:
        x = line.find("//")
        y = list(line)
        z = "".join(y[:x])
        lines.append(z.replace(" ", ""))

#Get all lable and add it to C symbol list
i = 0
to_be_deleted = []
for line in lines:
    if re.match("^\(.*\)$", line):
        x = list(line)
        x.pop(0)
        x.pop()
        symbol["".join(x)] = i
#        lines.remove(line)
        to_be_deleted.append(line) 
    else:
        i += 1
for line in to_be_deleted:
    lines.remove(line)
# n is the place where we start putting variable in memory
n = 16 
i = 0
for line in lines:
    if line[0] == "@" and (not line[1:].isnumeric()):
        x = symbol.get(line[1:])
        if x != None:
            lines[i] = "@" + str(x)
        else:
            symbol[line[1:]] = n
            n += 1
    i += 1



out_bin = []
for line in lines:
#first 2 if get A instruction and turn it to binary, make sure its 16 bits output
    if line[0] == "@" and line[1:].isnumeric():
        x = str(bin(int(line[1:]))[2:])
        out_bin.append(('0' * (16 - len(x))) + x)
    elif line[0] == "@" and (not line[1:].isnumeric()):
        x = str(bin(symbol.get(line[1:]))[2:])
        out_bin.append(('0' * (16 - len(x))) + x)
#now this deal with C instruction
    else:
        out_bit = "111"
        x = line.find("=")
        y = line.find(";")
        if x != -1 and y != -1:
            z = line[x+1:y]
        elif x != -1 and y == -1:
            z = line[x+1:]
        elif x == -1 and y != -1:
            z = line[:y] 
        elif x == -1 and y == -1:
            z = line

        out_bit = out_bit + C_instruction_list.get(z)

        if x != -1:
            z = line[:x]
            if "A" in z:
                out_bit = out_bit + "1"
            else:
                out_bit = out_bit + "0"
            if "D" in z:
                out_bit = out_bit + "1"
            else:
                out_bit = out_bit + "0"
            if "M" in z:
                out_bit = out_bit + "1"
            else:
                out_bit = out_bit + "0"
        else:
            out_bit = out_bit + "000"

        if y == -1:
            out_bit = out_bit + "000"
        else:
            if "JGT" in line:
                out_bit = out_bit + "001"
            elif "JEQ" in line:
                out_bit = out_bit + "010"
            elif "JGE" in line:
                out_bit = out_bit + "011"
            elif "JLT" in line:
                out_bit = out_bit + "100"
            elif "JNE" in line:
                out_bit = out_bit + "101"
            elif "JLE" in line:
                out_bit = out_bit + "110"
            elif "JMP" in line:
                out_bit = out_bit + "111"
        out_bin.append(out_bit)

for b in out_bin:
    file_out.write(b + "\n")

file_in.close()
file_out.close()