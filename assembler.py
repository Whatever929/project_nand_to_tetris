from itertools import count
from sys import argv

# Translation table for C-instruction.
comp_0 = {"0":"101010", "1":"111111","-1":"111010", "D":"001100", "A":"110000", "!D":"001101","!A":"110001",
"-A":"110001","D+1":"011111","A+1":"110111","D-1":"001110","A+1":"110111","D-1":"001110",
"A-1":"110010","D+A":"000010","D-A":"010011","A-D":"000111","D&A":"000000","D|A":"010101"
}

jump = {"JGT":"001","JEQ":"010","JGE":"011","JLT":"100","JNE":"101","JLE":"110","JMP":"111"}

# Translation table for symbols.
symbol_table = {"SP":'0', "LCL":'1',"ARG":'2',"THIS":'3',"THAT":'4',"SCREEN":'16384', "KBD":'24576'}

with open(argv[1].rstrip(".asm") + ".hack", "w") as f:
    pass

def addr_generator():
    addr = 16
    while addr < 16384:
        yield addr
        addr += 1

addr_gen = addr_generator()

with open(argv[1]) as f:
    row = 0
    for line in f:
        if line.strip():
            if line.strip()[0].isalnum() or line.strip()[0] == '@':
                row += 1
            elif line.strip()[0] == '(':
                line = line.partition('/')[0].strip()
                symbol_table[line[1:len(line) - 1]] = row



with open(argv[1]) as f:
    # Filter whitespace, ignore blank line and comment line.
    filtered = (line.replace(" ", "").replace("\n", "") for line in f if line[0:2] != "//")
    for line in filtered:
        # Ignore the blank line.
        if line != "":
            if line[0] == "@":
                buffer = ""
                # Case 1: Symbols
                if line[1].isalpha():
                    if (line[1] == 'R') and ((line[2].isdigit() and len(line) == 3) or (line[2].isdigit() and line[3] in ('1', '2', '3', '4', '5'))):
                        for i in range(2, len(line)):
                            if line[i].isdigit():
                                buffer += line[i]
                            else:
                                break
                    else:
                        line = line.partition('//')[0]
                        try:
                            buffer = symbol_table[line[1:]]
                        except KeyError:
                            symbol_table[line[1:]] = str(next(addr_gen))
                            buffer = symbol_table[line[1:]]
                # Case 2: Integer constant
                else:
                    for i in range(1, len(line)):
                        if line[i].isdigit():
                            buffer += line[i]
                        else:
                            break
                with open(argv[1].rstrip(".asm") + ".hack", "a") as out:
                    out.write("{0:016b}\n".format(int(buffer)))
            elif line[0] != '(':
                # Filter out comments and spread the instruction.
                instruction = line.partition(r"//")[0].partition(";")
                d,c = instruction[0].partition("=")[0:3:2]
                j = instruction[2][0:3]
                # Translate comp
                if c and d:
                    if "M" in c:
                        c = "1" + comp_0[c.replace("M", "A")]
                    else:
                        c = "0" + comp_0[c];
                elif d and not c:
                    c = d
                    d = 0
                    c = "0" + comp_0[c];
                else:
                    c = "0000000"
                # Translate dest
                bin_d = 0
                if d:
                    if "M" in d:
                        bin_d += 1
                    if "D" in d:
                        bin_d += 10
                    if "A" in d:
                        bin_d += 100
                # Translate jump
                if j:
                    j = jump[j]
                else:
                    j = "000"
                with open(argv[1].rstrip(".asm") + ".hack", "a") as out:
                    out.write("111{0}{1:0>3s}{2}\n".format(c,str(bin_d),j))
