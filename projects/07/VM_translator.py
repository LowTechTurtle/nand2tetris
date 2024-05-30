class VMTranslator(object):
    def __init__(self, file_in, file_out):
        self.file_in = file_in
        self.file_out = file_out
        self.lines = []
        for line in file_in:
            if line.startswith("//") or line == "" or line == "\n":
                pass
            else:
                self.lines.append(line)

        self.SP = 256
        self.LCL = 300
        self.ARG = 400
        self.THIS = 3030
        self.THAT = 3040
        self.TEMP = 5
        self.eq_count = 0
        self.gt_count = 0
        self.lt_count = 0
    
    def AL_or_Mem(self, line):
        AL_operation = ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]
        Mem_operation = ["pop", "push"]
        l = line.split()
        if l[0] in Mem_operation:
            return "Mem"
        else:
            return "AL"
    
    def translate_Mem(self, line):
        l = line.split()
        segment = l[1].strip()
        index = int(l[2])
        self.file_out.write(f"\n//{line}")
        if l[0] == "push":
            if segment == "local":
                x = 300 + index
                self.file_out.write(f"@{x} \nD=M \n@{self.SP} \nM=D \n@0 \nM=M+1")
            elif segment == "argument":
                x = 400 + index
                self.file_out.write(f"@{x} \nD=M \n@{self.SP} \nM=D \n@0 \nM=M+1")
            elif segment == "this":
                x = 3030 + index
                self.file_out.write(f"@{x} \nD=M \n@{self.SP} \nM=D \n@0 \nM=M+1")
            elif segment == "that":
                x = 3040 + index
                self.file_out.write(f"@{x} \nD=M \n@{self.SP} \nM=D \n@0 \nM=M+1")
            
            elif segment == "pointer":
                if index == 0:
                    self.file_out.write(f"@{3} \nD=M \n@{self.SP}\n M=D \n@0 \nM=M+1")
                if index == 1:
                    self.file_out.write(f"@{4} \nD=M \n@{self.SP}\n M=D \n@0 \nM=M+1")
            
            elif segment == "temp":
                x = 5 + index
                self.file_out.write(f"@{x} \nD=M \n@{self.SP} \nM=D \n@0 \nM=M+1")

            elif segment == "constant":
                self.file_out.write(f"@{index} \nD=A \n@{self.SP} \nM=D \n@0 \nM=M+1")
            
            elif segment == "static":
                x = 16 + index
                self.file_out.write(f"@{x} \nD=M \n@{self.SP} \nM=D \n@0 \nM=M+1")
            self.SP += 1

        elif l[0] == "pop":
            if segment == "local":
                x = 300 + index
                y = self.SP - 1
                self.file_out.write(f"@{y} \nD=M \n@{x} \nM=D \n@0 \nM=M-1")
            elif segment == "argument":
                x = 400 + index
                y = self.SP - 1
                self.file_out.write(f"@{y} \nD=M \n@{x} \nM=D \n@0 \nM=M-1")
            elif segment == "this":
                x = 3030 + index
                y = self.SP - 1
                self.file_out.write(f"@{y} \nD=M \n@{x} \nM=D \n@0 \nM=M-1")
            elif segment == "that":
                x = 3040 + index
                y = self.SP - 1
                self.file_out.write(f"@{y} \nD=M \n@{x} \nM=D \n@0 \nM=M-1")
            
            elif segment == "pointer":
                if index == 0:
                    y = self.SP - 1
                    self.file_out.write(f"@{y} \nD=M \n@{3} \nM=D \n@0 \nM=M-1")
                if index == 1:
                    y = self.SP - 1
                    self.file_out.write(f"@{y} \nD=M \n@{4} \nM=D \n@0 \nM=M-1")
            
            elif segment == "temp":
                x = 5 + index
                y = self.SP - 1
                self.file_out.write(f"@{y} \nD=M \n@{x} \nM=D \n@0 \nM=M-1")

            elif segment == "static":
                x = 16 + index
                y = self.SP - 1
                self.file_out.write(f"@{y} \nD=M \n@{x} \nM=D \n@0 \nM=M-1")
            self.SP -= 1
    
    def translate_AL(self, line):
        l = line.split()
        command = line.strip()
        self.file_out.write(f"\n//{line}")
        if command == "add":
            self.file_out.write(f"@{self.SP-1} \nD=M \n@{self.SP-2} \nM=M+D \n@0 \nM=M-1")
        elif command == "sub":
            self.file_out.write(f"@{self.SP-1} \nD=M \n@{self.SP-2} \nM=M-D \n@0 \nM=M-1")
        elif command == "neg":
            self.file_out.write(f"@{self.SP-1} \nM=-M\n")
            self.SP += 1
        elif command == "eq":
            self.file_out.write(f"@{self.SP-1} \nD=M \n@{self.SP-2} \nD=M-D \n@EQJ{self.eq_count} \nD;JEQ \n@NEQJ{self.eq_count} \nD;JMP")
            self.file_out.write(f"\n(EQJ{self.eq_count}) \n@{self.SP-2} \nM=-1 \n@0 \nM=M-1 \n@SkipEQ{self.eq_count} \nD;JMP \n(NEQJ{self.eq_count}) \n@{self.SP-2} \nM=0 \n@0 \nM=M-1 \n(SkipEQ{self.eq_count})")
            self.eq_count += 1
        elif command == "gt":
            self.file_out.write(f"@{self.SP-1} \nD=M \n@{self.SP-2} \nD=M-D \n@GTJ{self.gt_count} \nD;JGT \n@NGTJ{self.gt_count} \nD;JMP")
            self.file_out.write(f"\n(GTJ{self.gt_count}) \n@{self.SP-2} \nM=-1 \n@0 \nM=M-1 \n@SkipGT{self.gt_count} \nD;JMP \n(NGTJ{self.gt_count}) \n@{self.SP-2} \nM=0 \n@0 \nM=M-1 \n(SkipGT{self.gt_count})")
            self.gt_count += 1
        elif command == "lt":
            self.file_out.write(f"@{self.SP-1} \nD=M \n@{self.SP-2} \nD=M-D \n@LTJ{self.lt_count} \nD;JLT \n@NLTJ{self.lt_count} \nD;JMP")
            self.file_out.write(f"\n(LTJ{self.lt_count}) \n@{self.SP-2} \nM=-1 \n@0 \nM=M-1 \n@SkipLT{self.lt_count} \nD; JMP \n(NLTJ{self.lt_count}) \n@{self.SP-2} \nM=0 \n@0 \nM=M-1 \n(SkipLT{self.lt_count})")
            self.lt_count += 1

        elif command == "and":
            self.file_out.write(f"@{self.SP-1} \nD=M \n@{self.SP-2} \nM=M&D \n@0 \nM=M-1")
        elif command == "or":
            self.file_out.write(f"@{self.SP-1} \nD=M \n@{self.SP-2} \nM=M|D \n@0 \nM=M-1")
        elif command == "not":
            self.file_out.write(f"@{self.SP-1} \nM=!M")
        self.SP -= 1
    
    def translate(self):
        for line in self.lines:
            if self.AL_or_Mem(line) == "Mem":
                self.translate_Mem(line)
            elif self.AL_or_Mem(line) == "AL":
                self.translate_AL(line)
        self.file_out.write("\n")
        self.file_out.close()
        self.file_in.close()

file_in_name = input(".vm file name:\n>")
file_in = open(file_in_name, "r")
file_out_name = file_in_name[:-3] + ".asm"
file_out = open(file_out_name, "w")
translator = VMTranslator(file_in, file_out)
translator.translate()
