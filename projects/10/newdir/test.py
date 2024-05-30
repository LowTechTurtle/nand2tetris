f = open('SquareGame.jack', "r")

symbol = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+',
        '-', '*', '/', '&', '|', '<', '>', '=', '~']

selftoken = []
token = ''
mul_comment = 0
string = 0
for line in f:
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
                selftoken.append(token)
                token = ''
                string = 0
        elif c == " " and token != '':
            selftoken.append(token)
            token = ''
        elif c.isalnum():
            token += c
        elif c.isspace():
            if token != "":
                selftoken.append(token)
                token = ''
        elif c in symbol:
            if token != '':
                selftoken.append(token)
            selftoken.append(c)
            token = ''
        elif c == '"':
            if string == 0:
                string = 1
                if token != '':
                    selftoken.append(token)
                    token = ''
            elif string == 1:
                string = 0
                selftoken.append(token)
                token = ''

print(selftoken)
