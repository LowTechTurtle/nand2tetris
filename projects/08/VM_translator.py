from os import path
from os import listdir
from os.path import isfile, join

class VMTranslator(object):
    def __init__(self, path_file_in, file_out):
        self.file_in = []
        for file in listdir(path_file_in):
            if isfile(join(path_file_in, file)) and file.endswith(".vm"):
                if file.endswith("Sys.vm"):
                    self.file_in.insert(0, open(join(path_file_in, file), "r"))
                else:
                    self.file_in.append(open(join(path_file_in, file), "r"))
        
        self.file_out = file_out
        self.lines = []
        for file in self.file_in:
            for line in file:
                if line.startswith("//") or line == "" or line == "\n":
                    pass
                else:
                    x = line.find("//")
                    y = line[:x]
                    if y.split() != []:
                        self.lines.append(y)

        self.SP = 256
        self.LCL = 300
        self.ARG = []
        self.THIS = 3030
        self.THAT = 3040
        self.TEMP = 5
        self.eq_count = 0
        self.gt_count = 0
        self.lt_count = 0
        self.return_addr = 0
    
    def command_type(self, line):
        AL_operation = ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]
        Mem_operation = ["pop", "push"]
        Branching = ["label", 'goto', "if-goto"]
        Function = ["function", "call", "return"]
        l = line.split()
        if l[0] in Mem_operation:
            return "Mem"
        elif l[0] in AL_operation:
            return "AL"
        elif l[0] in Branching:
            return "Branching"
        elif l[0] in Function:
            return "Function"
    
    def translate_Mem(self, line):
        l = line.split()
        segment = l[1].strip()
        index = int(l[2])
        self.file_out.write(f"\n//{line}\n")
        if l[0] == "push":
            if segment == "local":
                x = 300 + index
#                self.file_out.write(f"@{x} \nD=M \n@0 \nA=M \nM=D \n@0 \nM=M+1")
                self.file_out.write(f"@1 \nD=M \n@{index} \nD=D+A \nA=D \nD=M \n@0 \nA=M \nM=D \n@0 \nM=M+1")
            elif segment == "argument":
                x = 400 + index
#                self.file_out.write(f"@{x} \nD=M \n@0 \nA=M \nM=D \n@0 \nM=M+1")
                self.file_out.write(f"@2 \nD=M \n@{index} \nD=D+A \nA=D \nD=M \n@0 \nA=M \nM=D \n@0 \nM=M+1")
            elif segment == "this":
                x = 3030 + index
#                self.file_out.write(f"@{x} \nD=M \n@0 \nA=M \nM=D \n@0 \nM=M+1")
                self.file_out.write(f"@3 \nD=M \n@{index} \nD=D+A \nA=D \nD=M \n@0 \nA=M \nM=D \n@0 \nM=M+1")
            elif segment == "that":
                x = 3040 + index
#                self.file_out.write(f"@{x} \nD=M \n@0 \nA=M \nM=D \n@0 \nM=M+1")
                self.file_out.write(f"@4 \nD=M \n@{index} \nD=D+A \nA=D \nD=M \n@0 \nA=M \nM=D \n@0 \nM=M+1")
            
            elif segment == "pointer":
                if index == 0:
                    self.file_out.write(f"@{3} \nD=M \n@0 \nA=M \nM=D \n@0 \nM=M+1")
                if index == 1:
                    self.file_out.write(f"@{4} \nD=M \n@0 \nA=M \nM=D \n@0 \nM=M+1")
            
            elif segment == "temp":
                x = 5 + index
                self.file_out.write(f"@{x} \nD=M \n@0 \nA=M \nM=D \n@0 \nM=M+1")

            elif segment == "constant":
                self.file_out.write(f"@{index} \nD=A \n@0 \nA=M \nM=D \n@0 \nM=M+1")
            
            elif segment == "static":
                x = 16 + index
                self.file_out.write(f"@{x} \nD=M \n@0 \nA=M \nM=D \n@0 \nM=M+1")
            self.SP += 1

        elif l[0] == "pop":
            if segment == "local":
                x = 300 + index
                y = self.SP - 1
#                self.file_out.write(f"@{y} \nD=M \n@{x} \nM=D \n@0 \nM=M-1")
                self.file_out.write(f"@1 \nD=M \n@{index} \nD=D+A \n@temp \nM=D \n@0 \nA=M-1 \nD=M \n@temp \nA=M \nM=D \n@0 \nM=M-1")
            elif segment == "argument":
                x = 400 + index
                y = self.SP - 1
#                self.file_out.write(f"@{y} \nD=M \n@{x} \nM=D \n@0 \nM=M-1")
                self.file_out.write(f"@2 \nD=M \n@{index} \nD=D+A \n@temp \nM=D \n@0 \nA=M-1 \nD=M \n@temp \nA=M \nM=D \n@0 \nM=M-1")
            elif segment == "this":
                x = 3030 + index
                y = self.SP - 1
#                self.file_out.write(f"@{y} \nD=M \n@{x} \nM=D \n@0 \nM=M-1")
                self.file_out.write(f"@3 \nD=M \n@{index} \nD=D+A \n@temp \nM=D \n@0 \nA=M-1 \nD=M \n@temp \nA=M \nM=D \n@0 \nM=M-1")
            elif segment == "that":
                x = 3040 + index
                y = self.SP - 1
#                self.file_out.write(f"@{y} \nD=M \n@{x} \nM=D \n@0 \nM=M-1")
                self.file_out.write(f"@4 \nD=M \n@{index} \nD=D+A \n@temp \nM=D \n@0 \nA=M-1 \nD=M \n@temp \nA=M \nM=D \n@0 \nM=M-1")
            
            elif segment == "pointer":
                if index == 0:
                    y = self.SP - 1
                    self.file_out.write(f"@0 \nA=M-1 \nD=M \n@{3} \nM=D \n@0 \nM=M-1")
                if index == 1:
                    y = self.SP - 1
                    self.file_out.write(f"@0 \nA=M-1 \nD=M \n@{4} \nM=D \n@0 \nM=M-1")
            
            elif segment == "temp":
                x = 5 + index
                y = self.SP - 1
                self.file_out.write(f"@0 \nA=M-1 \nD=M \n@{x} \nM=D \n@0 \nM=M-1")

            elif segment == "static":
                x = 16 + index
                y = self.SP - 1
                self.file_out.write(f"@0 \nA=M-1 \nD=M \n@{x} \nM=D \n@0 \nM=M-1")
            self.SP -= 1
    
    def translate_AL(self, line):
        l = line.split()
        command = line.strip()
        self.file_out.write(f"\n//{line}\n")
        if command == "add":
            self.file_out.write(f"@0 \nA=M-1 \nD=M \n@0 \nA=M-1 \nA=A-1 \nM=M+D \n@0 \nM=M-1")
        elif command == "sub":
            self.file_out.write(f"@0 \nA=M-1 \nD=M \n@0 \nA=M-1 \nA=A-1 \nM=M-D \n@0 \nM=M-1")
        elif command == "neg":
            self.file_out.write(f"@0 \nA=M-1 \nM=-M\n")
            self.SP += 1
        elif command == "eq":
            self.file_out.write(f"@0 \nA=M-1 \nD=M \n@0 \nA=M-1 \nA=A-1 \nD=M-D \n@EQJ{self.eq_count} \nD;JEQ \n@NEQJ{self.eq_count} \nD;JMP")
            self.file_out.write(f"\n(EQJ{self.eq_count}) \n@0 \nA=M-1 \nA=A-1 \nM=-1 \n@0 \nM=M-1 \n@SkipEQ{self.eq_count} \nD;JMP \n(NEQJ{self.eq_count}) \n@{self.SP-2} \nM=0 \n@0 \nM=M-1 \n(SkipEQ{self.eq_count})")
            self.eq_count += 1
        elif command == "gt":
            self.file_out.write(f"@0 \nA=M-1 \nD=M \n@0 \nA=M-1 \nA=A-1 \nD=M-D \n@GTJ{self.gt_count} \nD;JGT \n@NGTJ{self.gt_count} \nD;JMP")
            self.file_out.write(f"\n(GTJ{self.gt_count}) \n@0 \nA=M-1 \nA=A-1 \nM=-1 \n@0 \nM=M-1 \n@SkipGT{self.gt_count} \nD;JMP \n(NGTJ{self.gt_count}) \n@{self.SP-2} \nM=0 \n@0 \nM=M-1 \n(SkipGT{self.gt_count})")
            self.gt_count += 1
        elif command == "lt":
            self.file_out.write(f"@0 \nA=M-1 \nD=M \n@0 \nA=M-1 \nA=A-1 \nD=M-D \n@LTJ{self.lt_count} \nD;JLT \n@NLTJ{self.lt_count} \nD;JMP")
            self.file_out.write(f"\n(LTJ{self.lt_count}) \n@0 \nA=M-1 \nA=A-1 \nM=-1 \n@0 \nM=M-1 \n@SkipLT{self.lt_count} \nD; JMP \n(NLTJ{self.lt_count}) \n@{self.SP-2} \nM=0 \n@0 \nM=M-1 \n(SkipLT{self.lt_count})")
            self.lt_count += 1

        elif command == "and":
            self.file_out.write(f"@0 \nA=M-1 \nD=M \n@0 \nA=M-1 \nA=A-1 \nM=M&D \n@0 \nM=M-1")
        elif command == "or":
            self.file_out.write(f"@0 \nA=M-1 \nD=M \n@0 \nA=M-1 \nA=A-1 \nM=M|D \n@0 \nM=M-1")
        elif command == "not":
            self.file_out.write(f"@0 \nA=M-1 \nM=!M")
        self.SP -= 1
    

    def translate_Branching(self, line):
        l = line.strip().split()
        label = l[1]
        self.file_out.write(f"\n//{line}\n")

        if l[0] == 'label':
            self.file_out.write(f"\n({label})")

        elif l[0] == 'goto':
            self.file_out.write(f"\n@{label} \nD;JMP")

        elif l[0] == 'if-goto':
            self.file_out.write(f"\n@0 \nA=M-1 \nD=M \n@0 \nM=M-1 \n@{label} \nD;JNE \n")
            self.SP -= 1


    def translate_Function(self, line):
        l = line.strip().split()
        self.file_out.write(f"\n//{line}\n")

        if l[0] == "call":
            self.file_out.write(f"\n@return{self.return_addr} \nD=A \n@0 \nA=M \nM=D \n@0 \nM=M+1")
            self.SP += 1
            self.file_out.write(f"\n@1 \nD=M \n@0 \nA=M \nM=D \n@0 \nM=M+1\n")
            self.SP += 1
            self.file_out.write(f"\n@2 \nD=M \n@0 \nA=M \nM=D \n@0 \nM=M+1\n")
            self.SP += 1 
            self.file_out.write(f"\n@3 \nD=M \n@0 \nA=M \nM=D \n@0 \nM=M+1\n")
            self.SP += 1
            self.file_out.write(f"\n@4 \nD=M \n@0 \nA=M \nM=D \n@0 \nM=M+1\n")
            self.SP += 1
            
            self.ARG.append(self.SP - 5 - int(l[2]))
            self.file_out.write(f"\n@{self.ARG[len(self.ARG)-1]} \nD=A \n@2 \nM=D")
            self.file_out.write(f"\n@0 \nA=M \nD=A \n@1 \nM=D")
            self.file_out.write(f"\n@{l[1]} \nD;JMP")
            self.file_out.write(f"\n(return{self.return_addr})")
            self.return_addr += 1

        elif l[0] == "return":
            self.file_out.write(f"\n@1 \nD=M \n@frame \nM=D")
#            self.file_out.write(f"\n@frame \nD=M \n@5 \nD=D-A \nA=D \nD=M \n@retaddr \nM=D")
            self.file_out.write(f"\n@0 \nA=M-1 \nD=M \n@0 \nM=M-1 \n@2 \nA=M \nM=D")
            self.SP -= 1
            self.file_out.write(f"\n@2 \nD=M \n@1 \nD=D+A \n@0 \nM=D")
            self.SP = self.ARG.pop() + 1
            self.file_out.write(f"\n@frame \nD=M \n@1 \nD=D-A \nA=D \nD=M \n@4 \nM=D")
            self.file_out.write(f"\n@frame \nD=M \n@2 \nD=D-A \nA=D \nD=M \n@3 \nM=D")
            self.file_out.write(f"\n@frame \nD=M \n@3 \nD=D-A \nA=D \nD=M \n@2 \nM=D")
            self.file_out.write(f"\n@frame \nD=M \n@4 \nD=D-A \nA=D \nD=M \n@1 \nM=D")
            self.file_out.write(f"\n@return{self.return_addr-1} \nD;JMP")
#            self.file_out.write(f"\n@retaddr \nD;JMP")

        elif l[0] == "function":
            self.file_out.write(f"\n({l[1]})")
            for i in range(0, int(l[2])):
                self.file_out.write(f"\n@0 \nA=M \nM=0 \n@0 \nM=M+1")


    def translate(self):
        self.file_out.write("\n@256 \nD=A \n@0 \nM=D\n")
        self.file_out.write("\n@300 \nD=A \n@1 \nM=D\n")
        self.file_out.write("\n@400 \nD=A \n@2 \nM=D\n")
        self.file_out.write("\n@3030 \nD=A \n@3 \nM=D\n")
        self.file_out.write("\n@3040 \nD=A \n@4 \nM=D\n")
        for line in self.lines:
            if self.command_type(line) == "Mem":
                self.translate_Mem(line)
            elif self.command_type(line) == "AL":
                self.translate_AL(line)
            elif self.command_type(line) == "Branching":
                self.translate_Branching(line)
            elif self.command_type(line) == "Function":
                self.translate_Function(line)

        self.file_out.write("\n")
        for file in self.file_in:
            file.close()

file_in_path = input("dir in path: ")
file_out_name = path.basename(file_in_path) + ".asm"
file_out = open(join(file_in_path, file_out_name), "w")
translator = VMTranslator(file_in_path, file_out)
translator.translate()
#remember to set ram0 to 256
#ram1 300 ram2 400
#ram3 3030 ram4 3040