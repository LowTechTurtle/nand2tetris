// for (int i = 0; i < n; i++) {
//    mult += m;
//}

//initialize i = 0
@R0
D = A
@i
M = D

@R0
D = M
@n
M = D // store n

@R1
D = M
@m
M = D // store m

@R0
D = A
@sum
M = D // initialize sum = 0

(LOOP)
@n
D = M
@i 
D = M - D
@END
D; JGE

@m
D = M
@sum
M = M + D // sum += m

@i
M = M + 1 // i += 1

@LOOP
0; JMP

(END)
@sum
D = M
@R2
M = D //write to RAM[2]
@END
0; JMP