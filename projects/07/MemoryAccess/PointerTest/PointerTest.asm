
//push constant 3030
@3030 
D=A 
@256 
M=D 
@0 
M=M+1
//pop pointer 0
@256 
D=M 
@3 
M=D 
@0 
M=M-1
//push constant 3040
@3040 
D=A 
@256 
M=D 
@0 
M=M+1
//pop pointer 1
@256 
D=M 
@4 
M=D 
@0 
M=M-1
//push constant 32
@32 
D=A 
@256 
M=D 
@0 
M=M+1
//pop this 2
@256 
D=M 
@3032 
M=D 
@0 
M=M-1
//push constant 46
@46 
D=A 
@256 
M=D 
@0 
M=M+1
//pop that 6
@256 
D=M 
@3046 
M=D 
@0 
M=M-1
//push pointer 0
@3 
D=M 
@256
 M=D 
@0 
M=M+1
//push pointer 1
@4 
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
//push this 2
@3032 
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
//push that 6
@3046 
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
