from os import path
from os import listdir
from os.path import isfile, join

class UnexpectedToken(Exception):
    def __init__(self, token_expected, token_got):
        self.token_expected = token_expected
        self.token_got = token_got
        self.message = f"Expected token: {self.token_expected}, got: {self.token_got}"
        super().__init__(self.message)

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
    def __init__(self, in_stream, out_stream):
        self.in_stream = in_stream #Tokenizer object
        self.out_stream = out_stream #file object
        self.indent = 0

    def compileClass(self):
        out = ""
        out += '\t' * self.indent + "<class>" + "\n"
        self.indent += 1

        if self.in_stream.tokens[0] != "class":
            raise UnexpectedToken("class", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>" + "\n"
        self.in_stream.advance()

        if self.in_stream.tokenType() != 3:
            raise UnexpectedToken("indentifier type token", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>" + "\n"
        self.in_stream.advance()

        if self.in_stream.tokens[0] != "{":
            raise UnexpectedToken("{", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
        self.in_stream.advance()

        self.out_stream.write(out)
        out = ""

        while self.in_stream.tokens[0] == "field" or self.in_stream.tokens[0] == "static":
            self.compileClassVarDec()

        while self.in_stream.tokenType() == 1:
            self.compileSubroutine()

        if self.in_stream.tokens[0] != "}":
            raise UnexpectedToken("}", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
        self.in_stream.advance()

        self.indent -= 1
        out += '\t' * self.indent + "</class>" + "\n"

        self.out_stream.write(out)


    def compileClassVarDec(self):
        out = ""
        out += '\t' * self.indent + "<classVarDec>" + "\n"
        self.indent += 1

        if self.in_stream.tokens[0] != "field" and self.in_stream.tokens[0] != "static":
            raise UnexpectedToken("field or static", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>" + "\n"
        self.in_stream.advance()

        if self.in_stream.tokenType() != 3 and self.in_stream.tokenType() != 1:
            raise UnexpectedToken("keyword type or identifier type", self.in_stream.tokens[0])
        if self.in_stream.tokenType() == 3:
            out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>" + "\n"
            self.in_stream.advance()
        else:
            out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>" + "\n"
            self.in_stream.advance()

        if self.in_stream.tokenType() != 3:
            raise UnexpectedToken("identifier type", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>" + "\n"
        self.in_stream.advance()

        while (self.in_stream.tokens[0] == ','):
            out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
            self.in_stream.advance()

            if self.in_stream.tokenType() != 3:
                raise UnexpectedToken("identifier type", self.in_stream.tokens[0])
            out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>" + "\n"
            self.in_stream.advance()
        
        if self.in_stream.tokens[0] != ";":
            raise UnexpectedToken(";", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
        self.in_stream.advance()

        self.indent -= 1
        out += '\t' * self.indent + "</classVarDec>" + "\n"

        self.out_stream.write(out)

    def compileSubroutine(self):
        x = self.in_stream.tokens[0]
        out = ""
        out += '\t' * self.indent + "<subroutineDec>" + "\n"
        self.indent += 1
        
        if x != 'constructor' and x != 'method' and x != 'function':
            raise UnexpectedToken("constructor or method or function", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>" + "\n"
        self.in_stream.advance()

        x = self.in_stream.tokens[0]
        if self.in_stream.tokenType() != 1 and self.in_stream.tokenType() != 3:
            raise UnexpectedToken("function type", self.in_stream.tokens[0])
        if self.in_stream.tokenType() == 1:
            out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>" + "\n"
        else:
            out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>" + "\n"
        self.in_stream.advance()

        if self.in_stream.tokenType() != 3:
            raise UnexpectedToken("identifier type", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>" + "\n"
        self.in_stream.advance()

        if self.in_stream.tokens[0] != "(":
            raise UnexpectedToken("(", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>"+ "\n"
        self.in_stream.advance()

        self.out_stream.write(out)
        out = ""

        self.compileParameterList()

        if self.in_stream.tokens[0] != ")":
            raise UnexpectedToken(")", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>"+ "\n"
        self.in_stream.advance()

        self.out_stream.write(out)
        out = ''

        self.compileSubroutineBody()

        self.indent -= 1
        out += '\t' * self.indent + "</subroutineDec>" + "\n"

        self.out_stream.write(out)

        
    def compileParameterList(self):
        out = ""
        out += '\t' * self.indent + "<parameterList>" + "\n"
        self.indent += 1

        if self.in_stream.tokens[0] == ')':
            out += '\t' * self.indent + "</parameterList>" + "\n"
            self.out_stream.write(out)
            return

        if self.in_stream.tokenType() != 3 and self.in_stream.tokenType() != 1:
            raise UnexpectedToken("var or identifier type", self.in_stream.tokens[0])
        if self.in_stream.tokenType() == 3:
            out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>" + "\n"
        else:
            out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>" + "\n"
        self.in_stream.advance()

        if self.in_stream.tokenType() != 3:
            raise UnexpectedToken("identifier type", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>" + "\n"
        self.in_stream.advance()

        while (self.in_stream.tokens[0] == ','):
            out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
            self.in_stream.advance()

            if self.in_stream.tokenType() != 3 and self.in_stream.tokenType() != 1:
                raise UnexpectedToken("var or identifier type", self.in_stream.tokens[0])
            if self.in_stream.tokenType() == 3:
                out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>" + "\n"
            else:
                out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>" + "\n"
            self.in_stream.advance()

            if self.in_stream.tokenType() != 3:
                raise UnexpectedToken("identifier type", self.in_stream.tokens[0])
            out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>" + "\n"
            self.in_stream.advance()
        
        self.out_stream.write(out)
        out = ''

        self.indent -= 1

        out += '\t' * self.indent + "</parameterList>" + "\n"

        self.out_stream.write(out)


    def compileSubroutineBody(self):
        out = ""
        out += '\t' * self.indent + "<subroutineBody>" + "\n"
        self.indent += 1
        
        if self.in_stream.tokens[0] != "{":
            raise UnexpectedToken("{", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>"+ "\n"
        self.in_stream.advance()

        self.out_stream.write(out)
        out = ""

        while not (self.in_stream.tokens[0] in ['let', 'if', 'while', 'do', 'return']):
            self.compileVarDec()

        self.compileStatements()

        if self.in_stream.tokens[0] != "}":
            raise UnexpectedToken("}", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>"+ "\n"
        self.in_stream.advance()

        self.indent -= 1
        out += '\t' * self.indent + "</subroutineBody>" + "\n"
        self.out_stream.write(out)

    def compileVarDec(self):
        out = ""
        out += '\t' * self.indent + "<varDec>" + "\n"
        self.indent += 1

        if self.in_stream.tokens[0] != "var":
            raise UnexpectedToken("var", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>"+ "\n"
        self.in_stream.advance()

        if self.in_stream.tokenType() != 3 and self.in_stream.tokenType() != 1:
            raise UnexpectedToken("var or identifier type", self.in_stream.tokens[0])
        if self.in_stream.tokenType() == 3:
            out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>" + "\n"
        else:
            out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>" + "\n"
        self.in_stream.advance()


        if self.in_stream.tokenType() != 3:
            raise UnexpectedToken("identifier type", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>"+ "\n"
        self.in_stream.advance()


        while (self.in_stream.tokens[0] == ','):
            out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
            self.in_stream.advance()

            if self.in_stream.tokenType() != 3:
                raise UnexpectedToken("identifier type", self.in_stream.tokens[0])
            out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>" + "\n"
            self.in_stream.advance()


        if self.in_stream.tokens[0] != ";":
            raise UnexpectedToken(";", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
        self.in_stream.advance()

        self.indent -= 1
        out += '\t' * self.indent + "</varDec>" + "\n"

        self.out_stream.write(out)

    def compileStatements(self):
        out = ""
        out += '\t' * self.indent + "<statements>" + "\n"
        self.indent += 1
        self.out_stream.write(out)
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
        out += '\t' * self.indent + "</statements>" + "\n"
        self.out_stream.write(out)


    def compileLet(self):
        out = ""
        out += '\t' * self.indent + "<letStatement>" + "\n"
        self.indent += 1

        if self.in_stream.tokens[0] != "let":
            raise UnexpectedToken("let", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>"+ "\n"
        self.in_stream.advance()

        if self.in_stream.tokenType() != 3:
            raise UnexpectedToken("identifier type", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>"+ "\n"
        self.in_stream.advance()

        if self.in_stream.tokens[0] == '[':
            out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
            self.in_stream.advance()

            self.out_stream.write(out)
            out = ''

            self.compileExpression()

            if self.in_stream.tokens[0] != "]":
                raise UnexpectedToken("]", self.in_stream.tokens[0])
            out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
            self.in_stream.advance()
        
        if self.in_stream.tokens[0] != "=":
            raise UnexpectedToken("=", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
        self.in_stream.advance()

        self.out_stream.write(out)
        out = ''

        self.compileExpression()

        if self.in_stream.tokens[0] != ";":
            raise UnexpectedToken(";", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
        self.in_stream.advance()

        self.indent -= 1
        out += '\t' * self.indent + "</letStatement>" + "\n"
        self.out_stream.write(out)


    def compileIf(self):
        out = ""
        out += '\t' * self.indent + "<ifStatement>" + "\n"
        self.indent += 1

        if self.in_stream.tokens[0] != "if":
            raise UnexpectedToken("if", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>"+ "\n"
        self.in_stream.advance()

        if self.in_stream.tokens[0] != "(":
            raise UnexpectedToken("(", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
        self.in_stream.advance()

        self.out_stream.write(out)
        out = ''

        self.compileExpression()

        if self.in_stream.tokens[0] != ")":
            raise UnexpectedToken(")", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
        self.in_stream.advance()


        if self.in_stream.tokens[0] != "{":
            raise UnexpectedToken("{", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
        self.in_stream.advance()


        self.out_stream.write(out)
        out = ''

        self.compileStatements()

        if self.in_stream.tokens[0] != "}":
            raise UnexpectedToken("}", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
        self.in_stream.advance()

        if self.in_stream.tokens[0] == 'else':
            out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>" + "\n"
            self.in_stream.advance()

            if self.in_stream.tokens[0] != "{":
                raise UnexpectedToken("{", self.in_stream.tokens[0])
            out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
            self.in_stream.advance()
            self.out_stream.write(out)
            out = ''

            self.compileStatements()

            if self.in_stream.tokens[0] != "}":
                raise UnexpectedToken("}", self.in_stream.tokens[0])
            out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
            self.in_stream.advance()
        
        self.indent -= 1
        out += '\t' * self.indent + "</ifStatement>" + "\n"
        self.out_stream.write(out)


    def compileWhile(self):
        out = ""
        out += '\t' * self.indent + "<whileStatement>" + "\n"
        self.indent += 1

        if self.in_stream.tokens[0] != "while":
            raise UnexpectedToken("while", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>"+ "\n"
        self.in_stream.advance()

        if self.in_stream.tokens[0] != "(":
            raise UnexpectedToken("(", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
        self.in_stream.advance()

        self.out_stream.write(out)
        out = ''

        self.compileExpression()

        if self.in_stream.tokens[0] != ")":
            raise UnexpectedToken(")", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
        self.in_stream.advance()


        if self.in_stream.tokens[0] != "{":
            raise UnexpectedToken("{", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
        self.in_stream.advance()


        self.out_stream.write(out)
        out = ''

        self.compileStatements()

        if self.in_stream.tokens[0] != "}":
            raise UnexpectedToken("}", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
        self.in_stream.advance()

        self.indent -= 1
        out += '\t' * self.indent + "</whileStatement>" + "\n"
        self.out_stream.write(out)


    def compileDo(self):
        out = ""
        out += '\t' * self.indent + "<doStatement>" + "\n"
        self.indent += 1

        if self.in_stream.tokens[0] != "do":
            raise UnexpectedToken("do", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>"+ "\n"
        self.in_stream.advance()

        self.out_stream.write(out)
        out = ''

        self.compileTerm(subroutinecall=True)

        if self.in_stream.tokens[0] != ";":
            raise UnexpectedToken(";", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>"+ "\n"
        self.in_stream.advance()

        self.indent -= 1
        out += '\t' * self.indent + "</doStatement>" + "\n"
        self.out_stream.write(out)

    def compileReturn(self):
        out = ""
        out += '\t' * self.indent + "<returnStatement>" + "\n"
        self.indent += 1

        if self.in_stream.tokens[0] != "return":
            raise UnexpectedToken("return", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>"+ "\n"
        self.in_stream.advance()

        self.out_stream.write(out)
        out = ''

        if self.in_stream.tokens[0] != ';':
            self.out_stream.write(out)
            out = ''
            self.compileExpression()
        
        if self.in_stream.tokens[0] != ";":
            raise UnexpectedToken(";", self.in_stream.tokens[0])
        out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>"+ "\n"
        self.in_stream.advance()

        self.indent -= 1
        out += '\t' * self.indent + "</returnStatement>" + "\n"
        self.out_stream.write(out)

    def compileExpression(self):
        out = ""
        out += '\t' * self.indent + "<expression>" + "\n"
        self.indent += 1

        self.out_stream.write(out)
        out = ''
        self.compileTerm()

        while self.in_stream.tokens[0] in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
            if not(self.in_stream.tokens[0] in ['<', '>', '&']):
                out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
            else:
                if self.in_stream.tokens[0] == '<':
                    out += '\t' * self.indent + f"<symbol> &lt; </symbol>" + "\n"
                if self.in_stream.tokens[0] == '>':
                    out += '\t' * self.indent + f"<symbol> &gt; </symbol>" + "\n"
                if self.in_stream.tokens[0] == '&':
                    out += '\t' * self.indent + f"<symbol> &amp; </symbol>" + "\n"
            self.in_stream.advance()

            self.out_stream.write(out)
            out = ''
            self.compileTerm()
        
        self.indent -= 1
        out += '\t' * self.indent + "</expression>" + "\n"
        self.out_stream.write(out)

    def compileTerm(self, subroutinecall = False):
        out = ""
        if subroutinecall == False:
            out += '\t' * self.indent + "<term>" + "\n"
            self.indent += 1

        x = self.in_stream.tokens[0]
        if x.isnumeric():
            out += '\t' * self.indent + f"<integerConstant> {self.in_stream.tokens[0]} </integerConstant>" + "\n"
            self.in_stream.advance()
        elif x.startswith('"') and x.endswith('"'):
            self.in_stream.tokens[0] = self.in_stream.tokens[0][1:-1]
            out += '\t' * self.indent + f"<stringConstant> {self.in_stream.tokens[0]} </stringConstant>" + "\n"
            self.in_stream.advance()
        elif x in ['true', 'false', 'null', 'this']:
            out += '\t' * self.indent + f"<keyword> {self.in_stream.tokens[0]} </keyword>" + "\n"
            self.in_stream.advance()
        elif x == '(':
            out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
            self.in_stream.advance()
            
            self.out_stream.write(out)
            out = ''
            self.compileExpression()

            if self.in_stream.tokens[0] != ")":
                raise UnexpectedToken(")", self.in_stream.tokens[0])
            out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
            self.in_stream.advance()
        
        #subroutine call
        elif self.in_stream.tokenType() == 3 and self.in_stream.tokens[1] in ['(', '.']:
            out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>" + "\n"
            self.in_stream.advance()

            if self.in_stream.tokens[0] == '(':
                out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
                self.in_stream.advance()

                if self.in_stream.tokens[0] == ')':
                    out += '\t' * self.indent + "<expressionList>" + "\n"
                    out += '\t' * self.indent + "</expressionList>" + "\n"
                    out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
                    self.in_stream.advance()
                    self.indent -= 1
                    if subroutinecall == False:
                        out += '\t' * self.indent + "</term>" + "\n"
                    self.out_stream.write(out)
                    return

                self.out_stream.write(out)
                out = ''
                self.compileExpressionList()

                if self.in_stream.tokens[0] != ")":
                    raise UnexpectedToken(")", self.in_stream.tokens[0])
                out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
                self.in_stream.advance()

            elif self.in_stream.tokens[0] == '.':
                out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
                self.in_stream.advance()

                if self.in_stream.tokenType() != 3:
                    raise UnexpectedToken("identifier type", self.in_stream.tokens[0])
                out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>" + "\n"
                self.in_stream.advance()

                if self.in_stream.tokens[0] == '(':
                    out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
                    self.in_stream.advance()

                if self.in_stream.tokens[0] == ')':
                    out += '\t' * self.indent + "<expressionList>" + "\n"
                    out += '\t' * self.indent + "</expressionList>" + "\n"
                    out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
                    self.in_stream.advance()
                    self.indent -= 1
                    if subroutinecall == False:
                        out += '\t' * self.indent + "</term>" + "\n"
                    self.out_stream.write(out)
                    return

                self.out_stream.write(out)
                out = ''
                self.compileExpressionList()

                if self.in_stream.tokens[0] != ")":
                    raise UnexpectedToken(")", self.in_stream.tokens[0])
                out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
                self.in_stream.advance()


        elif self.in_stream.tokenType() == 3 and self.in_stream.tokens[1] != '(' and self.in_stream.tokens[0] != '.': #varname expression and varname
            out += '\t' * self.indent + f"<identifier> {self.in_stream.tokens[0]} </identifier>" + "\n"
            self.in_stream.advance()
            
            if self.in_stream.tokens[0] == "[":

                out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
                self.in_stream.advance()
            
                self.out_stream.write(out)
                out = ''
                self.compileExpression()

                if self.in_stream.tokens[0] != "]":
                    raise UnexpectedToken("]", self.in_stream.tokens[0])
                out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
                self.in_stream.advance()

        elif self.in_stream.tokens[0] in ['~', '-']:
            out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
            self.in_stream.advance()
            self.out_stream.write(out)
            out = ''
            self.compileTerm()

        if subroutinecall == False:
            self.indent -= 1
            out += '\t' * self.indent + "</term>" + "\n"
        if out != '':
            self.out_stream.write(out)


    def compileExpressionList(self):
        out = ""
        out += '\t' * self.indent + "<expressionList>" + "\n"
        self.indent += 1
        count = 1
        self.out_stream.write(out)
        out = ''
        self.compileExpression()

        while self.in_stream.tokens[0] == ',':
            count += 1
            out += '\t' * self.indent + f"<symbol> {self.in_stream.tokens[0]} </symbol>" + "\n"
            self.in_stream.advance()
        
            self.out_stream.write(out)
            out = ''
            self.compileExpression()
        
        self.indent -= 1
        out += '\t' * self.indent + "</expressionList>" + "\n"
        self.out_stream.write(out)
        return count


class JackAnalyzer(object):
    def __init__(self, input_path):
        self.file_in = []
        for file in listdir(input_path):
            if isfile(join(input_path, file)) and file.endswith(".jack"):
                x = open(join(input_path, file), "r")
                y = open(join(input_path, file)[:-4] + "turtle.xml", "w")
                self.file_in.append((x, y))

    def run(self):
        filelog = open("tokenlog.txt", "w")
        for file_in, file_out in self.file_in:
            tokens = Tokenizer(file_in)
            filelog.write(str(tokens.tokens))
            compile_engine = CompilationEngine(tokens, file_out)
            compile_engine.compileClass()

file_in_path = input("dir in path: ")
analyzer = JackAnalyzer(file_in_path)
analyzer.run()