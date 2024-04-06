
//push constant 111
@111 
D=A 
@256 
M=D 
@0 
M=M+1
//push constant 333
@333 
D=A 
@257 
M=D 
@0 
M=M+1
//push constant 888
@888 
D=A 
@258 
M=D 
@0 
M=M+1
//pop static 8
@258 
D=M 
@24 
M=D 
@0 
M=M-1
//pop static 3
@257 
D=M 
@19 
M=D 
@0 
M=M-1
//pop static 1
@256 
D=M 
@17 
M=D 
@0 
M=M-1
//push static 3
@19 
D=M 
@256 
M=D 
@0 
M=M+1
//push static 1
@17 
D=M 
@257 
M=D 
@0 
M=M+1
//sub
@257 
D=M 
@256 
M=M-D 
@0 
M=M-1
//push static 8
@24 
D=M 
@257 
M=D 
@0 
M=M+1
//add
@257 
D=M 
@256 
M=M+D 
@0 
M=M-1
