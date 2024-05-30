from os import path
from os import listdir
from os.path import isfile, join

class UnexpectedToken(Exception):
    def __init__(self, token_expected, token_got):
        self.token_expected = token_expected
        self.token_got = token_got
        self.message = f"Expected token: {self.token_expected}, got: {self.token_got}"
        super().__init__(self.message)

class SymbolTable(object):
    def __init__(self):
        self.class_table = {}
        self.subroutine_table = {}
        self.static_index = 0
        self.field_index = 0
        self.arg_index = 0
        self.var_index = 0
    
    def reset(self):
        self.subroutine_table = {}
        self.static_index = 0
        self.field_index = 0
        self.arg_index = 0
        self.var_index = 0

    def define(self, name, _type, kind):
        if kind == "static":
            self.class_table.update({name: (_type, kind, self.static_index)})
            self.static_index += 1
        elif kind == "field":
            self.class_table.update({name: (_type, kind, self.field_index)})
            self.field_index += 1
        elif kind == "argument":
            self.subroutine_table.update({name: (_type, kind, self.arg_index)})
            self.arg_index += 1
        elif kind == "var":
            self.subroutine_table.update({name: (_type, kind, self.var_index)})
            self.var_index += 1
        

    def varCount(self, kind):
        if kind == "static":
            return self.static_index
        elif kind == "field":
            return self.field_index
        elif kind == "var":
            return self.var_index
        elif kind == "argument":
            return self.arg_index

    def kindOf(self, name):
        local_name = self.subroutine_table.get(name)
        if local_name == None:
            class_name = self.class_table.get(name) 
            if class_name != None:
                return class_name[1]
        else:
            return local_name[1]

    def typeOf(self, name):
        local_name = self.subroutine_table.get(name)
        if local_name == None:
            class_name = self.class_table.get(name) 
            if class_name != None:
                return class_name[0]
        else:
            return local_name[0]

    def indexOf(self, name):
        local_name = self.subroutine_table.get(name)
        if local_name == None:
            class_name = self.class_table.get(name) 
            if class_name != None:
                return class_name[2]
        else:
            return local_name[2]

class VMWriter(object):
    def __init__(self, out_stream):
        self.out_stream = out_stream
    
    def writePush(self, segment, index):
        self.out_stream.write("push " + segment + " " + str(index) + "\n") 

    def writePop(self, segment, index):
        self.out_stream.write("pop " + segment + " " + str(index) + "\n") 

    def writeArithmetic(self, command):
        self.out_stream.write(command + "\n")

    def writeLabel(self, label):
        self.out_stream.write("label " + label + "\n") 

    def writeGoto(self, label):
        self.out_stream.write("goto " + label + "\n")

    def writeIf(self, label):
        self.out_stream.write("if-goto " + label + "\n")

    def writeCall(self, name, nArgs):
        self.out_stream.write("call " + name + " " + str(nArgs) + "\n") 

    def writeFunction(self, name, nVars):
        self.out_stream.write("function " + name + " " + str(nVars) + "\n")

    def writeReturn(self):
        self.out_stream.write("return\n")

    def close(self):
        self.out_stream.close()

class Tokenizer(object):
    def __init__(self, input_file):
        self.keyWord = ["class", "constructor", "function", "method", "field", "static",
        "var", 'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this', 'let', 'do'
        'if', 'else', 'while', 'return']

        self.symbol = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+',
        '-', '*', '/', '&', '|', '<', '>', '=', '~']

        self.input_file = input_file
        self.tokens = []
        token = ''
        mul_comment = 0
        string = 0
        for line in self.input_file:
            line = line.strip()
            if line.startswith('//'):
                continue 
            if line.startswith('/*') and line.endswith('*/'):
                continue
            if line.startswith('/*'):
                mul_comment = 1
                continue
            if mul_comment == 1:
                if line.endswith('*/'):
                    mul_comment = 0
                    continue
                elif line.find('*/') != -1:
                    line = line[line.find('*/')+2:]
                else:
                    continue
            if (index := line.find('//')) != -1:
                line = line[:index]
            
            for c in line:
                if string == 1:
                    if c != '"':
                        token += c
                    else:
                        self.tokens.append('"' + token + '"')
                        token = ''
                        string = 0
                elif c == " " and token != '':
                    self.tokens.append(token)
                    token = ''
                elif c.isalnum():
                    token += c
                elif c.isspace():
                    if token != "":
                        self.tokens.append(token)
                        token = ''
                elif c in self.symbol:
                    if token != '':
                        self.tokens.append(token)
                    self.tokens.append(c)
                    token = ''
                elif c == '"':
                    if string == 0:
                        string = 1
                        if token != '':
                            self.tokens.append(token)
                            token = ''
                    elif string == 1:
                        string = 0
                        self.tokens.append('"' + token + '"')
                        token = ''
    
    def hasMoreTokens(self):
        return len(self.tokens) != 0

    def advance(self):
        self.tokens.pop(0)

#return the type of the current token
    def tokenType(self):
        if self.tokens[0] in self.keyWord:
            return 1
        elif self.tokens[0] in self.symbol:
            return 2
        elif self.tokens[0].isnumeric():
            return 4
        elif self.tokens[0].startswith('"') and self.tokens[0].endswith('"'):
            return 5
        else:
            return 3

#return the type of the token in index i
    def tokenType_at_i(self, i):
        if self.tokens[i] in self.keyWord:
            return 1
        elif self.tokens[i] in self.symbol:
            return 2
        elif self.tokens[i].isnumeric():
            return 4
        elif self.tokens[i].startswith('"') and self.tokens[0].endswith('"'):
            return 5
        else:
            return 3

    def keyWord(self): #type 1
        pass

    def symbol(self): #type 2
        pass

    def identifier(self): #type 3
        pass 

    def intVal(self): #type 4
        pass

    def stringVal(self): #type 5 
        pass


class CompilationEngine(object):
    def __init__(self, in_stream, table, out_vm, out_vm_name):
        self.in_stream = in_stream #Tokenizer object
        self.out_vm = out_vm
        self.indent = 0
        self.table = table
        self.out_vm_name = out_vm_name
        self.writer = VMWriter(out_vm)
        self.label = 0

    def compileClass(self):
        out = ""
        #out += '\t' * self.indent + "<class>" + "\n"
        self.indent += 1

        if self.in_stream.tokens[0] != "class":
            raise UnexpectedToken("class", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>" + "\n"
        self.in_stream.advance()

        if self.in_stream.tokenType() != 3:
            raise UnexpectedToken("indentifier type token", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>" + "\n"
        self.in_stream.advance()

        if self.in_stream.tokens[0] != "{":
            raise UnexpectedToken("{", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
        self.in_stream.advance()

        #self.out_stream.write(out)
        out = ""

        while self.in_stream.tokens[0] == "field" or self.in_stream.tokens[0] == "static":
            self.compileClassVarDec()

        while self.in_stream.tokenType() == 1:
            self.compileSubroutine()

        if self.in_stream.tokens[0] != "}":
            raise UnexpectedToken("}", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
        self.in_stream.advance()

        self.indent -= 1
        #out += '\t' * self.indent + "</class>" + "\n"

        #self.out_stream.write(out)


    def compileClassVarDec(self):
        out = ""
        #out += '\t' * self.indent + "<classVarDec>" + "\n"
        self.indent += 1
        var_type = ''
#get kind here ## done
        if self.in_stream.tokens[0] != "field" and self.in_stream.tokens[0] != "static":
            raise UnexpectedToken("field or static", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>" + "\n"
        kind = self.in_stream.tokens[0]
        self.in_stream.advance()

#get type for var in class_table here ##done
        if self.in_stream.tokenType() != 3 and self.in_stream.tokenType() != 1:
            raise UnexpectedToken("keyword type or identifier type", self.in_stream.tokens[0])
        var_type = self.in_stream.tokens[0]
        print(var_type)
        if self.in_stream.tokenType() == 3:
            #out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>" + "\n"
            self.in_stream.advance()
        else:
            #out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>" + "\n"
            self.in_stream.advance()

#get name here ##done
        if self.in_stream.tokenType() != 3:
            raise UnexpectedToken("identifier type", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>" + "\n"
        var_name = self.in_stream.tokens[0]
        self.in_stream.advance()

        self.table.define(var_name, var_type, kind)

#get 0 or more name of var of same type here ##done 
        while (self.in_stream.tokens[0] == ','):
            #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
            self.in_stream.advance()

            if self.in_stream.tokenType() != 3:
                raise UnexpectedToken("identifier type", self.in_stream.tokens[0])
            #out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>" + "\n"
            var_name = self.in_stream.tokens[0]
            self.table.define(var_name, var_type, kind)
            self.in_stream.advance()

        if self.in_stream.tokens[0] != ";":
            raise UnexpectedToken(";", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
        self.in_stream.advance()

        self.indent -= 1
        #out += '\t' * self.indent + "</classVarDec>" + "\n"

        #self.out_stream.write(out)

    def compileSubroutine(self): ##this shit is not done, need to call alloc n shite for constructor
#reset the subroutine table ##done
        self.table.reset()
        x = self.in_stream.tokens[0]
        out = ""
        #out += '\t' * self.indent + "<subroutineDec>" + "\n"
        self.indent += 1
        
        method = 0
#declare function(write to .vm file) ##done
        if x != 'constructor' and x != 'method' and x != 'function':
            raise UnexpectedToken("constructor or method or function", self.in_stream.tokens[0])
        if x == "method":
            method = 1
        #out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>" + "\n"
        self.in_stream.advance()

#if method, get type of function and push it to the table  ##done
        x = self.in_stream.tokens[0]
        if self.in_stream.tokenType() != 1 and self.in_stream.tokenType() != 3:
            raise UnexpectedToken("function type", self.in_stream.tokens[0])
        func_type = x
#        if self.in_stream.tokenType() == 1:
            #out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>" + "\n"
#        else:
            #out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>" + "\n"
        self.in_stream.advance()

#get name here ##done
        if self.in_stream.tokenType() != 3:
            raise UnexpectedToken("identifier type", self.in_stream.tokens[0])
        func_name = self.in_stream.tokens[0]
        #out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>" + "\n"
        self.in_stream.advance()
#need to write function declaration ##will be done in compile subroutine body
        if method == 1:
            self.table.define("this", func_type, "argument")

        if self.in_stream.tokens[0] != "(":
            raise UnexpectedToken("(", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>"+ "\n"
        self.in_stream.advance()

        #self.out_stream.write(out)
        out = ""

        self.compileParameterList()

        if self.in_stream.tokens[0] != ")":
            raise UnexpectedToken(")", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>"+ "\n"
        self.in_stream.advance()

        #self.out_stream.write(out)
        out = ''
        
        if (method == 1):
            self.compileSubroutineBody(func_name, method=1)
        else:
            self.compileSubroutineBody(func_name)

        self.indent -= 1
        #out += '\t' * self.indent + "</subroutineDec>" + "\n"

        #self.out_stream.write(out)

        
    def compileParameterList(self):
        out = ""
        #out += '\t' * self.indent + "<parameterList>" + "\n"
        self.indent += 1

        if self.in_stream.tokens[0] == ')':
            #out += '\t' * self.indent + "</parameterList>" + "\n"
            #self.out_stream.write(out)
            return

#begin to get type of argument here and put it into the table ##done
        if self.in_stream.tokenType() != 3 and self.in_stream.tokenType() != 1:
            raise UnexpectedToken("var or identifier type", self.in_stream.tokens[0])
        var_type = self.in_stream.tokens[0]
#        if self.in_stream.tokenType() == 3:
            #out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>" + "\n"
#        else:
            #out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>" + "\n"
        self.in_stream.advance()

#get var name here ##done
        if self.in_stream.tokenType() != 3:
            raise UnexpectedToken("identifier type", self.in_stream.tokens[0])
        var_name = self.in_stream.tokens[0]
        #out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>" + "\n"
        self.in_stream.advance()
        
        self.table.define(var_name, var_type, "argument")

#get more argument, var type and var name, push it to the table, rinse and repeat ##done
        while (self.in_stream.tokens[0] == ','):
            #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
            self.in_stream.advance()

            if self.in_stream.tokenType() != 3 and self.in_stream.tokenType() != 1:
                raise UnexpectedToken("var or identifier type", self.in_stream.tokens[0])
#            if self.in_stream.tokenType() == 3:
                #out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>" + "\n"
#            else:
                #out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>" + "\n"
            var_type = self.in_stream.tokens[0]
            self.in_stream.advance()

            if self.in_stream.tokenType() != 3:
                raise UnexpectedToken("identifier type", self.in_stream.tokens[0])
            #out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>" + "\n"
            var_name = self.in_stream.tokens[0]
            self.in_stream.advance()

            self.table.define(var_name, var_type, "argument")

        #self.out_stream.write(out)
        out = ''

        self.indent -= 1

        #out += '\t' * self.indent + "</parameterList>" + "\n"

        #self.out_stream.write(out)


    def compileSubroutineBody(self, func_name, method=0):
        out = ""
        #out += '\t' * self.indent + "<subroutineBody>" + "\n"
        self.indent += 1
        
        if self.in_stream.tokens[0] != "{":
            raise UnexpectedToken("{", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>"+ "\n"
        self.in_stream.advance()

        #self.out_stream.write(out)
        out = ""

#gonna write function declaration below
        sum = 0
        while not (self.in_stream.tokens[0] in ['let', 'if', 'while', 'do', 'return']):
            sum += self.compileVarDec()
        
        self.writer.writeFunction(self.out_vm_name + func_name, sum)
        if method == 0:
            if len(self.table.class_table) > 0:
                self.writer.writePush("constant", len(self.table.class_table))
                self.writer.writeCall("Memory.alloc", 1)
                self.writer.writePop("pointer", 0)
        else:
            self.writer.writePush("argument", 0)
            self.writer.writePop("pointer", 0)


        self.compileStatements()

        if self.in_stream.tokens[0] != "}":
            raise UnexpectedToken("}", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>"+ "\n"
        self.in_stream.advance()

        self.indent -= 1
        #out += '\t' * self.indent + "</subroutineBody>" + "\n"
        #self.out_stream.write(out)

    def compileVarDec(self):
        out = ""
        #out += '\t' * self.indent + "<varDec>" + "\n"
        self.indent += 1
        num_of_var = 1
#local var ##done
        if self.in_stream.tokens[0] != "var":
            raise UnexpectedToken("var", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>"+ "\n"
        self.in_stream.advance()

#var type ##done
        if self.in_stream.tokenType() != 3 and self.in_stream.tokenType() != 1:
            raise UnexpectedToken("var or identifier type", self.in_stream.tokens[0])
#        if self.in_stream.tokenType() == 3:
            #out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>" + "\n"
#        else:
            #out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>" + "\n"
        var_type = self.in_stream.tokens[0]
        self.in_stream.advance()


#get var name, push it to the table ##done
        if self.in_stream.tokenType() != 3:
            raise UnexpectedToken("identifier type", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>"+ "\n"
        var_name = self.in_stream.tokens[0]
        self.in_stream.advance()
        self.table.define(var_name, var_type, "var")

#maybe more var_name, repeatly push it to the table ##done
        while (self.in_stream.tokens[0] == ','):
            #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
            self.in_stream.advance()

            if self.in_stream.tokenType() != 3:
                raise UnexpectedToken("identifier type", self.in_stream.tokens[0])
            #out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>" + "\n"
            self.table.define(self.in_stream.tokens[0], var_type, "var")
            self.in_stream.advance()
            num_of_var += 1


        if self.in_stream.tokens[0] != ";":
            raise UnexpectedToken(";", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
        self.in_stream.advance()

        self.indent -= 1
        #out += '\t' * self.indent + "</varDec>" + "\n"

        #self.out_stream.write(out)
        return num_of_var

    def compileStatements(self):
        out = ""
        #out += '\t' * self.indent + "<statements>" + "\n"
        self.indent += 1
        #self.out_stream.write(out)
        out = ''

        while self.in_stream.tokens[0] in ['let', 'if', 'while', 'do', 'return']:
            if self.in_stream.tokens[0] == 'let':
                self.compileLet()
            elif self.in_stream.tokens[0] == 'if':
                self.compileIf()
            elif self.in_stream.tokens[0] == 'while':
                self.compileWhile()
            elif self.in_stream.tokens[0] == 'do':
                self.compileDo()
            elif self.in_stream.tokens[0] == 'return':
                self.compileReturn()

        self.indent -= 1
        #out += '\t' * self.indent + "</statements>" + "\n"
        #self.out_stream.write(out)


    def compileLet(self):
        out = ""
        #out += '\t' * self.indent + "<letStatement>" + "\n"
        self.indent += 1
        array = 0

        if self.in_stream.tokens[0] != "let":
            raise UnexpectedToken("let", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>"+ "\n"
        self.in_stream.advance()

#get the var from table ##done
        if self.in_stream.tokenType() != 3:
            raise UnexpectedToken("identifier type", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>"+ "\n"
        var_name = self.in_stream.tokens[0]
        self.in_stream.advance()

#check if needed to handle array ##done
        if self.in_stream.tokens[0] == '[':
            array = 1
            #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
            self.in_stream.advance()

            #self.out_stream.write(out)
            out = ''
##
            self.compileExpression()

            if self.table.kindOf(var_name) == "var":
                self.writer.writePush("local", self.table.indexOf(var_name))
            elif self.table.kindOf(var_name) == "argument":
                self.writer.writePush("argument", self.table.indexOf(var_name))
            elif self.table.kindOf(var_name) == "static":
                self.writer.writePush("static", self.table.indexOf(var_name))
            elif self.table.kindOf(var_name) == "field":
                self.writer.writePush("this", self.table.indexOf(var_name))

            self.writer.writeArithmetic("add")

            if self.in_stream.tokens[0] != "]":
                raise UnexpectedToken("]", self.in_stream.tokens[0])
            #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
            self.in_stream.advance()
        
        if self.in_stream.tokens[0] != "=":
            raise UnexpectedToken("=", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
        self.in_stream.advance()

        #self.out_stream.write(out)
        out = ''

#eval the expression ##done
        self.compileExpression()
        if array == 1:
            self.writer.writePop("temp", 0)
            self.writer.writePop("pointer", 1)
            self.writer.writePush("temp", 0)
            self.writer.writePop("that", 0)
        else:
            if self.table.kindOf(var_name) == "static":
                self.writer.writePop("static", self.table.indexOf(var_name))
            elif self.table.kindOf(var_name) == "field":
                self.writer.writePop("this", self.table.indexOf(var_name))
            elif self.table.kindOf(var_name) == "var":
                self.writer.writePop("local", self.table.indexOf(var_name))
            elif self.table.kindOf(var_name) == "argument":
                self.writer.writePop("argument", self.table.indexOf(var_name))


#pop to the var(will need to check if need to handle array) ##done in previous line ##done
        if self.in_stream.tokens[0] != ";":
            raise UnexpectedToken(";", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
        self.in_stream.advance()

        self.indent -= 1
        #out += '\t' * self.indent + "</letStatement>" + "\n"
        #self.out_stream.write(out)


    def compileIf(self):
        out = ""
        #out += '\t' * self.indent + "<ifStatement>" + "\n"
        self.indent += 1

        if self.in_stream.tokens[0] != "if":
            raise UnexpectedToken("if", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>"+ "\n"
        self.in_stream.advance()

        if self.in_stream.tokens[0] != "(":
            raise UnexpectedToken("(", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
        self.in_stream.advance()

        #self.out_stream.write(out)
        out = ''

#negate and branch ##done
        self.compileExpression()

        self.writer.writeArithmetic("not")
        label1 = f"LABEL{self.label}"
        self.writer.writeIf(label1)
        self.label += 1
        label2 = f"LABEL{self.label}"
        self.label += 1

        if self.in_stream.tokens[0] != ")":
            raise UnexpectedToken(")", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
        self.in_stream.advance()


        if self.in_stream.tokens[0] != "{":
            raise UnexpectedToken("{", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
        self.in_stream.advance()


        #self.out_stream.write(out)
        out = ''

#write label for endif ##done
        self.compileStatements()

        self.writer.writeGoto(label2)

        if self.in_stream.tokens[0] != "}":
            raise UnexpectedToken("}", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
        self.in_stream.advance()

#write for label for flow controlling ##done
        self.writer.writeLabel(label1)

        if self.in_stream.tokens[0] == 'else':
            #out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>" + "\n"
            self.in_stream.advance()

            if self.in_stream.tokens[0] != "{":
                raise UnexpectedToken("{", self.in_stream.tokens[0])
            #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
            self.in_stream.advance()
            #self.out_stream.write(out)
            out = ''
            self.compileStatements()

            if self.in_stream.tokens[0] != "}":
                raise UnexpectedToken("}", self.in_stream.tokens[0])
            #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
            self.in_stream.advance()
#write label2 ##done 
        self.writer.writeLabel(label2)
        
        self.indent -= 1
        #out += '\t' * self.indent + "</ifStatement>" + "\n"
        #self.out_stream.write(out)


    def compileWhile(self):
        out = ""
        #out += '\t' * self.indent + "<whileStatement>" + "\n"
        self.indent += 1

        if self.in_stream.tokens[0] != "while":
            raise UnexpectedToken("while", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>"+ "\n"
        self.in_stream.advance()

        if self.in_stream.tokens[0] != "(":
            raise UnexpectedToken("(", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
        self.in_stream.advance()

        #self.out_stream.write(out)
        out = ''
        #declare some label ##done
        label1 = f"LABEL{self.label}"
        self.label += 1
        label2 = f"LABEL{self.label}"
        self.label += 1

#write label1 for while loop ##done
        self.writer.writeLabel(label1)
        self.compileExpression()
        self.writer.writeArithmetic("not")
        self.writer.writeIf(label2)

        if self.in_stream.tokens[0] != ")":
            raise UnexpectedToken(")", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
        self.in_stream.advance()


        if self.in_stream.tokens[0] != "{":
            raise UnexpectedToken("{", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
        self.in_stream.advance()


        #self.out_stream.write(out)
        out = ''

#execute statements and return to the beginning of the loop or end loop ##done
        self.compileStatements()
        self.writer.writeGoto(label1)
        self.writer.writeLabel(label2)

        if self.in_stream.tokens[0] != "}":
            raise UnexpectedToken("}", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
        self.in_stream.advance()

        self.indent -= 1
        #out += '\t' * self.indent + "</whileStatement>" + "\n"
        #self.out_stream.write(out)


    def compileDo(self):
        out = ""
        #out += '\t' * self.indent + "<doStatement>" + "\n"
        self.indent += 1

        if self.in_stream.tokens[0] != "do":
            raise UnexpectedToken("do", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>"+ "\n"
        self.in_stream.advance()

        #self.out_stream.write(out)
        out = ''

        self.compileTerm(subroutinecall=True)
#get rid of the return value
        self.writer.writePop("temp", 0)
        if self.in_stream.tokens[0] != ";":
            raise UnexpectedToken(";", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>"+ "\n"
        self.in_stream.advance()

        self.indent -= 1
        #out += '\t' * self.indent + "</doStatement>" + "\n"
        #self.out_stream.write(out)

    def compileReturn(self):
        out = ""
        #out += '\t' * self.indent + "<returnStatement>" + "\n"
        self.indent += 1

        if self.in_stream.tokens[0] != "return":
            raise UnexpectedToken("return", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>"+ "\n"
        self.in_stream.advance()

        #self.out_stream.write(out)
        out = ''

#write return after evaluating expression, return 0 if void function
        if self.in_stream.tokens[0] != ';':
            #self.out_stream.write(out)
            out = ''
            self.compileExpression()
            self.writer.writeReturn()
        else:
            self.writer.writePush("constant", 0)
            self.writer.writeReturn()
        
        if self.in_stream.tokens[0] != ";":
            raise UnexpectedToken(";", self.in_stream.tokens[0])
        #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>"+ "\n"
        self.in_stream.advance()

        self.indent -= 1
        #out += '\t' * self.indent + "</returnStatement>" + "\n"
        #self.out_stream.write(out)

    def compileExpression(self):
        out = ""
        #out += '\t' * self.indent + "<expression>" + "\n"
        self.indent += 1

        #self.out_stream.write(out)
        out = ''
        self.compileTerm()

        while self.in_stream.tokens[0] in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
            op = self.in_stream.tokens[0]
#            if not(self.in_stream.tokens[0] in ['<', '>', '&']):
                #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
#            else:
#                if self.in_stream.tokens[0] == '<':
                    #out += '\t' * self.indent + f"<symbol> &lt; </symbol>" + "\n"
#                if self.in_stream.tokens[0] == '>':
                    #out += '\t' * self.indent + f"<symbol> &gt; </symbol>" + "\n"
#                if self.in_stream.tokens[0] == '&':
                    #out += '\t' * self.indent + f"<symbol> &amp; </symbol>" + "\n"
            self.in_stream.advance()

            #self.out_stream.write(out)
            out = ''
            self.compileTerm()
            if op == '+':
                self.writer.writeArithmetic("add")
            if op == '-':
                self.writer.writeArithmetic("sub")
            if op == '/':
                self.writer.writeCall("Math.divide", 2)
            elif op == '*':
                self.writer.writeCall("Math.multiply", 2)
            elif op == '&':
                self.writer.writeArithmetic("and")
            elif op == '|':
                self.writer.writeArithmetic("or")
            elif op == '>':
                self.writer.writeArithmetic("gt")
            elif op == '<':
                self.writer.writeArithmetic("lt")
            elif op == '=':
                self.writer.writeArithmetic("eq")
        
        self.indent -= 1
        #out += '\t' * self.indent + "</expression>" + "\n"
        #self.out_stream.write(out)
    
    def compileTerm(self, subroutinecall = False):
        out = ""
        if subroutinecall == False:
            #out += '\t' * self.indent + "<term>" + "\n"
            self.indent += 1

        x = self.in_stream.tokens[0]
        if x.isnumeric():
            #out += '\t' * self.indent + f"<integerConstant> {self.in_stream.tokens[0]} </integerConstant>" + "\n"
            self.writer.writePush("constant", self.in_stream.tokens[0])
            self.in_stream.advance()
    #handle string constant ##done(maybe)
        elif x.startswith('"') and x.endswith('"'):
            self.in_stream.tokens[0] = self.in_stream.tokens[0][1:-1]
            #out += '\t' * self.indent + f"<stringConstant> {self.in_stream.tokens[0]} </stringConstant>" + "\n"
            self.writer.writePush("constant", len(self.in_stream.tokens[0]))
            self.writer.writeCall("String.new", 1)
            for char in self.in_stream.tokens[0]:
                self.writer.writePush("constant", ord(char))
                self.writer.writeCall("String.appendChar", 2)
            self.in_stream.advance()
        elif x in ['true', 'false', 'null', 'this']:
            #out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>" + "\n"
            if x in ['false', 'null']:
                self.writer.writePush("constant", 0)
            elif x == "true":
                self.writer.writePush("constant", 1)
            elif x == "this":
                self.writer.writePush("pointer", 0)
            self.in_stream.advance()
        elif x == '(':
            #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
            self.in_stream.advance()
            
            #self.out_stream.write(out)
            out = ''
            self.compileExpression()

            if self.in_stream.tokens[0] != ")":
                raise UnexpectedToken(")", self.in_stream.tokens[0])
            #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
            self.in_stream.advance()
        
        #subroutine call
        ##TODO: need to resolve method call, e.g: p1.distance(p2)
        elif self.in_stream.tokenType() == 3 and self.in_stream.tokens[1] in ['(', '.']:
            #get name of subroutine
            name = self.in_stream.tokens[0]
            #out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>" + "\n"
            self.in_stream.advance()

            if self.in_stream.tokens[0] == '(':
                #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
                self.in_stream.advance()

                if self.in_stream.tokens[0] == ')':
                    #out += '\t' * self.indent + "<expressionList>" + "\n"
                    #out += '\t' * self.indent + "</expressionList>" + "\n"
                    #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
                    self.in_stream.advance()
                    self.indent -= 1
#                    if subroutinecall == False:
                        #out += '\t' * self.indent + "</term>" + "\n"
                    #self.out_stream.write(out)
                    self.writer.writePush("pointer", 0) #push this
                    self.writer.writeCall(self.out_vm_name + name, 1)
                    return

                #self.out_stream.write(out)
                out = ''
##after compling expression list(pushing in enough arg, call the method)
                self.writer.writePush("pointer", 0) #push this
                num_of_args = self.compileExpressionList()
                self.writer.writeCall(self.out_vm_name + name, num_of_args+1)

                if self.in_stream.tokens[0] != ")":
                    raise UnexpectedToken(")", self.in_stream.tokens[0])
                #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
                self.in_stream.advance()

            elif self.in_stream.tokens[0] == '.':
                #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
                self.in_stream.advance()

                if self.in_stream.tokenType() != 3:
                    raise UnexpectedToken("identifier type", self.in_stream.tokens[0])
                #out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>" + "\n"
                ##get the method name of class
                method_name = self.in_stream.tokens[0]
                self.in_stream.advance()

                if self.in_stream.tokens[0] == '(':
                    #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
                    self.in_stream.advance()

                if self.in_stream.tokens[0] == ')':
                    #out += '\t' * self.indent + "<expressionList>" + "\n"
                    #out += '\t' * self.indent + "</expressionList>" + "\n"
                    #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
                    self.in_stream.advance()
                    self.indent -= 1
#                    if subroutinecall == False:
                        #out += '\t' * self.indent + "</term>" + "\n"
                    #self.out_stream.write(out)
                    if self.table.indexOf(name) != None:
                        if self.table.kindOf(name) == "var":
                            self.writer.writePush("local", self.table.indexOf(name))
                        elif self.table.kindOf(name) == "argument":
                            self.writer.writePush("argument", self.table.indexOf(name))
                        elif self.table.kindOf(name) == "static":
                          self.writer.writePush("static", self.table.indexOf(name))
                        elif self.table.kindOf(name) == "field":
                            self.writer.writePush("this", self.table.indexOf(name))
                    if self.table.indexOf(name) != None:
                        self.writer.writeCall(self.table.typeOf(name) + "." + method_name, 1)
                    if self.table.indexOf(name) == None:
                        self.writer.writeCall(name + "." + method_name, 0)
                    return

                #self.out_stream.write(out)
                out = ''
                if self.table.indexOf(name) != None:
                    if self.table.kindOf(name) == "var":
                        self.writer.writePush("local", self.table.indexOf(name))
                    elif self.table.kindOf(name) == "argument":
                        self.writer.writePush("argument", self.table.indexOf(name))
                    elif self.table.kindOf(name) == "static":
                      self.writer.writePush("static", self.table.indexOf(name))
                    elif self.table.kindOf(name) == "field":
                        self.writer.writePush("this", self.table.indexOf(name))

#get numbers of args from compile expression list and call subroutine
                num_of_args = self.compileExpressionList()
                if self.table.indexOf(name) != None:
                    self.writer.writeCall(self.table.typeOf(name) + "." + method_name, num_of_args+1)
                if self.table.indexOf(name) == None:
                    self.writer.writeCall(name + "." + method_name, num_of_args)

                if self.in_stream.tokens[0] != ")":
                    raise UnexpectedToken(")", self.in_stream.tokens[0])
                #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
                self.in_stream.advance()


        elif self.in_stream.tokenType() == 3 and self.in_stream.tokens[1] != '(' and self.in_stream.tokens[0] != '.': #varname expression and varname
            #get the var name ##done
            var_name = self.in_stream.tokens[0]
            #out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>" + "\n"
            self.in_stream.advance()
#ah shjt, need to handle array ##done
            if self.in_stream.tokens[0] == "[":
                #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
                self.in_stream.advance()
            
                #self.out_stream.write(out)
                out = ''
                self.compileExpression()

                if self.table.kindOf(var_name) == "var":
                    self.writer.writePush("local", self.table.indexOf(var_name))
                elif self.table.kindOf(var_name) == "argument":
                    self.writer.writePush("argument", self.table.indexOf(var_name))
                elif self.table.kindOf(var_name) == "static":
                    self.writer.writePush("static", self.table.indexOf(var_name))
                elif self.table.kindOf(var_name) == "field":
                    self.writer.writePush("this", self.table.indexOf(var_name))

                self.writer.writeArithmetic("add")

                self.writer.writePop("pointer", 1)
                self.writer.writePush("that", 0)

                if self.in_stream.tokens[0] != "]":
                    raise UnexpectedToken("]", self.in_stream.tokens[0])
                #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
                self.in_stream.advance()
            else:
#if not an array, just push it on da stack ## done
                if self.table.kindOf(var_name) == "var":
                    self.writer.writePush("local", self.table.indexOf(var_name))
                elif self.table.kindOf(var_name) == "argument":
                    self.writer.writePush("argument", self.table.indexOf(var_name))
                elif self.table.kindOf(var_name) == "static":
                    self.writer.writePush("static", self.table.indexOf(var_name))
                elif self.table.kindOf(var_name) == "field":
                    self.writer.writePush("this", self.table.indexOf(var_name))

        elif self.in_stream.tokens[0] in ['~', '-']:
            #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
            op = self.in_stream.tokens[0]
            self.in_stream.advance()
            #self.out_stream.write(out)
            out = ''
            self.compileTerm()
            #write term then write op
            if op == "-":
                self.writer.writeArithmetic("not")
            if op == "~":
                self.writer.writeArithmetic("not")

        if subroutinecall == False:
            self.indent -= 1
            #out += '\t' * self.indent + "</term>" + "\n"
#        if out != '':
            #self.out_stream.write(out)


    def compileExpressionList(self):
        out = ""
        #out += '\t' * self.indent + "<expressionList>" + "\n"
        self.indent += 1
        count = 1
        #self.out_stream.write(out)
        out = ''
        self.compileExpression()

        while self.in_stream.tokens[0] == ',':
            count += 1
            #out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
            self.in_stream.advance()
        
            #self.out_stream.write(out)
            out = ''
            self.compileExpression()
        
        self.indent -= 1
        #out += '\t' * self.indent + "</expressionList>" + "\n"
        #self.out_stream.write(out)
        return count

class JackCompiler(object):
    def __init__(self, input_path):
        self.file_in = []
        for file in listdir(input_path):
            if isfile(join(input_path, file)) and file.endswith(".jack"):
                x = open(join(input_path, file), "r")
                y = open(join(input_path, file)[:-4] + "vm", "w")
                self.file_in.append((x, y, join('', file)[:-4]))

    def run(self):
        for file_in, file_out, file_out_name in self.file_in:
            tokens = Tokenizer(file_in)
            table = SymbolTable()
            compile_engine = CompilationEngine(tokens, table, file_out, file_out_name)
            compile_engine.compileClass()

file_in_path = input("dir in path: ")
compiler = JackCompiler(file_in_path)
compiler.run()