import sys

def sumcheck(data, checksum):
    checksum_new = 0
    i = 0
    while i < len(data):
        checksum_new += int(data[i:i + 2], 16)
        if checksum_new > 255:
            checksum_new -= 256

        i += 2

    if checksum == (256 - checksum_new):
        return True

    else:
        return False

def convert2byte(data):
    data = bin(data)
    data = data[2:]
    while len(data) < 8:
        data = "0" + data

    return data

def hexbyte(data):
    data = hex(data)
    data = "0X0" + data[2]

    return data

def hexbytes(data):
    data = hex(data)
    if len(data) == 3:
        data = "0X000" + data[2:]

    elif len(data) == 4:
        data = "0X00" + data[2:]
    
    elif len(data) == 5:
        data = "0X0" + data[2:]

    return data

def disassemble(data, obc, address, asm): # data = [first byte in string, second byte in string, ...]
    i = 0
    while (i < len(data)):
        x = 0
        while (x < len(obc)):
            if len(obc[x]) == 4:
                operands = obc[x][3].split(", ")

            if data[i] == int(obc[x][0], 16):
                if obc[x][1] == "1":
                    ltbw = "0X" + (hexbytes(address))[2:].upper() + "\t| " + hexbyte(data[i]).upper() + "\t\t |  " + obc[x][2] + ("" if obc[x][3] == "-" else " " + obc[x][3]) + " "

                    for operand in operands:
                        if operands[0] != "-":
                            ltbw += operand[0]

                    if sys.argv[1] == "-v" or sys.argv[1] == "--verbose":
                        pass

                    else:
                        ltbw = ltbw[ltbw.find("|  ") + 3:]

                    print(ltbw)
                    asm.write(ltbw)
                    asm.write("\n")
                    address += 1
                    i += 1

                elif obc[x][1] == "2":
                    ltbw = "0X" + (hexbytes(address))[2:].upper() + "\t| " + hexbyte(data[i]).upper() + " " + hexbyte(data[i + 1]).upper() + "\t |  " + obc[x][2] + " "
                    y = 1
                    for k, operand in enumerate(operands):
                        if operand == "bit addr" or operand == "data addr":
                            ltbw += str(hexbyte(data[i + k + y])).upper()
                        
                        elif operand == "#data":
                            ltbw += "#" + str(hexbyte(data[i + k + y])).upper()

                        elif operand == "code addr":
                            if obc[x][2] == "ACALL" or obc[x][2] == "AJMP":
                                codeaddr = int(convert2byte(data[i])[:3] + convert2byte(data[i + k + y]), 2)

                            else: 
                                codeaddr = address + 2 + data[i + k + y]
                                if codeaddr > 255:
                                    codeaddr = codeaddr - 256

                                if address > 127:
                                    codeaddr = 256 - codeaddr

                            codeaddr = hexbytes(codeaddr)
                            ltbw += "(" + codeaddr.upper() + ")"

                        else:
                            ltbw += operand
                            y = 0

                        if k < len(operands) - 1:
                            ltbw += ", "

                    if sys.argv[1] == "-v" or sys.argv[1] == "--verbose":
                        pass

                    else:
                        ltbw = ltbw[ltbw.find("|  ") + 3:]

                    print(ltbw)
                    asm.write(ltbw)
                    asm.write("\n")
                    address += 2
                    i += 2

                elif obc[x][1] == "3":
                    ltbw = "0X" + (hexbytes(address))[2:].upper() + "\t| " + hexbyte(data[i]).upper() + " " + hexbyte(data[i + 1]).upper() + " " + hexbyte(data[i + 2]).upper() + " |  " + obc[x][2] + " "
                    y = 1
                    for k, operand in enumerate(operands):
                        if operand == "bit addr" or operand == "data addr":
                            ltbw += str(hexbyte(data[i + k + y])).upper()
                        
                        elif operand == "#data":
                            ltbw += "#" + str(hexbyte(data[i + k + y])).upper()

                        elif operand == "code addr":
                            if obc[x][2] == "ACALL" or obc[x][2] == "AJMP":
                                codeaddr = int(convert2byte(data[i])[:3] + convert2byte(data[i + k + y]), 2)

                            elif obc[x][2] == "LCALL" or obc[x][2] == "LJMP":
                                codeaddr = int(convert2byte(data[i + 1]) + convert2byte(data[i + k + y + 1]), 2)

                            else: 
                                codeaddr = address + 3 + data[i + k + y]
                                if codeaddr > 255:
                                    codeaddr = codeaddr - 256

                                if address > 127:
                                    codeaddr = 256 - codeaddr

                            codeaddr = hexbytes(codeaddr)
                            ltbw += "(" + codeaddr.upper() + ")"

                        else:
                            ltbw += operand
                            y = 0

                        if k < len(operands) - 1:
                            ltbw += ", "

                    if sys.argv[1] == "-v" or sys.argv[1] == "--verbose":
                        pass

                    else:
                        ltbw = ltbw[ltbw.find("|  ") + 3:]

                    print(ltbw)
                    asm.write(ltbw)
                    asm.write("\n")
                    address += 3
                    i += 3
            
            x += 1
            if i == len(data):
                break

    return

def main():
    f = open(sys.argv[-2], "r")
    lines = f.readlines()
    f.close()

    asm = open(sys.argv[-1], "w")
    print("\t|\t\t |  " + "ORG (0X" + lines[0][3:7] + ")")
    asm.write("ORG 0X" + lines[0][3:7])
    opc = open("opcodehex.txt", "r")
    obc = []
    for line in opc.readlines():
        line = line.replace("\n", "")
        obc.append(line.split("  "))

    opc.close()

    for index, line in enumerate(lines):

        bytecount = int(line[1:3], 16) # convert from hex to decimal
        address = int(line[3:7], 16)

        # byte count verification:
        lng = len(line) - 12
        bytecount *= 2
        if lng != bytecount:
            print(f"Byte count mismatch in line: {index + 1}")
            break

        data = [] # data to be stored as base 10 integer
        i = 9
        while i < len(line) - 3:
            data.append(int(line[i:i+2], 16))
            i += 2

        checksum = int(line[-3:], 16)

        if not sumcheck(line[1:-3], checksum):
            print(f"Checksum error in line: {index + 1}")
            break

        disassemble(data, obc, address, asm)

    print("\t|\t\t |  " + "END")
    asm.write("\t|\t\t |  " + "END")
    asm.close()

if __name__ == "__main__":
    main()