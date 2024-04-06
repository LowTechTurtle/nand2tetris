
//push constant 10
@10 
D=A 
@256 
M=D 
@0 
M=M+1
//pop local 0
@256 
D=M 
@300 
M=D 
@0 
M=M-1
//push constant 21
@21 
D=A 
@256 
M=D 
@0 
M=M+1
//push constant 22
@22 
D=A 
@257 
M=D 
@0 
M=M+1
//pop argument 2
@257 
D=M 
@402 
M=D 
@0 
M=M-1
//pop argument 1
@256 
D=M 
@401 
M=D 
@0 
M=M-1
//push constant 36
@36 
D=A 
@256 
M=D 
@0 
M=M+1
//pop this 6
@256 
D=M 
@3006 
M=D 
@0 
M=M-1
//push constant 42
@42 
D=A 
@256 
M=D 
@0 
M=M+1
//push constant 45
@45 
D=A 
@257 
M=D 
@0 
M=M+1
//pop that 5
@257 
D=M 
@3015 
M=D 
@0 
M=M-1
//pop that 2
@256 
D=M 
@3012 
M=D 
@0 
M=M-1
//push constant 510
@510 
D=A 
@256 
M=D 
@0 
M=M+1
//pop temp 6
@256 
D=M 
@11 
M=D 
@0 
M=M-1
//push local 0
@300 
D=M 
@256 
M=D 
@0 
M=M+1
//push that 5
@3015 
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
//push argument 1
@401 
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
//push this 6
@3006 
D=M 
@257 
M=D 
@0 
M=M+1
//push this 6
@3006 
D=M 
@258 
M=D 
@0 
M=M+1
//add
@258 
D=M 
@257 
M=M+D 
@0 
M=M-1
//sub
@257 
D=M 
@256 
M=M-D 
@0 
M=M-1
//push temp 6
@11 
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
