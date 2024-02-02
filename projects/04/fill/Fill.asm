// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen
// by writing 'black' in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen by writing
// 'white' in every pixel;
// the screen should remain fully clear as long as no key is pressed.

//// Replace this comment with your code.

// for (int i = KBD; i < KBD+8192; i++) {
//     RAM[i] = -1;
// }

//declare constant len=2^13
@8192
D = A
@len
M = D

//initialize i = 0
@R0
D = M
@i
M = D // i = 0

(LOOP)
@KBD
D = M
@PAINT_BLACK
D; JNE
@PAINT_WHITE
D; JEQ

(PAINT_BLACK)
@i 
D = M
@len
D = D - M
@END
D; JGE // if i >= n then terminate

@i 
D = M
@SCREEN
A = A + D
M = -1 //RAM[i] = -1

@i
M = M + 1 //i += 1 
@R0
D = M
@PAINT_BLACK
D; JMP


(PAINT_WHITE)
@i 
D = M
@len
D = D - M
@END
D; JGE // if i >= n then terminate

@i 
D = M
@SCREEN
A = A + D
M = 0 //RAM[i] = -1

@i
M = M + 1 //i += 1 
@R0
D = M
@PAINT_WHITE
D; JMP

(END)
@i
M = 0
D = M
@LOOP
D; JMP
