
__version__ = 1.0

enc = "utf-8"

import sys
import binascii
import binhex
import struct

# Dictionary for the opcodes
# 0 and 1 have special meaning and do not directly define the function
opcodes = {

    "00": "add",
    "01": "add",
    "02": "add",
    "03": "add",
    "04": "add",
    "05": "add",
    "20": "and",
    "21": "and",
    "22": "and",
    "23": "and",
    "39": "cmp",
    "40": "inc",
    "41": "inc",
    "42": "inc",
    "43": "inc",
    "44": "inc",
    "45": "inc",
    "46": "inc",
    "47": "inc",
    "48": "dec",
    "49": "dec",
    "4a": "dec",
    "4b": "dec",
    "4c": "dec",
    "4d": "dec",
    "4e": "dec",
    "4f": "dec",
    "50": "push",
    "51": "push",
    "52": "push",
    "53": "push",
    "54": "push",
    "55": "push",
    "56": "push",
    "57": "push",
    "58": "pop",
    "59": "pop",
    "5a": "pop",
    "5b": "pop",
    "5c": "pop",
    "5d": "pop",
    "5e": "pop",
    "5f": "pop",
    "68": "push",
    "74": "jz",
    "8b": "mov",
    "ae": "clflush",
    "b8": "mov",
    "c2": "ret",
    "ff": "mov",
    "89": "mov",
    "8D": "lea",
    "90": "nop",
    "e7": "out",
    "e9": "jmp",

}

# if we have a r-type instruction (opcode 0), we need the function codes to decode the functions
modrm = {

    "ff000": "inc",
    "ff001": "dec",
    "ff010": "call",
    "ff011": "call",
    "ff100": "jmp",
    "ff101": "jmp",
    "ff110": "push"

}

# List of registernumbers and their cleartext names
registers = {
    "000": "%eax",
    "011": "%ebx",
    "001": "%ecx",
    "010": "%edx",
    "110": "%esi",
    "111": "%edi",
    "100": "%esp",
    "101": "%ebp",
    "0": "%eax",
    "3": "%ebx",
    "1": "%ecx",
    "2": "%edx",
    "6": "%esi",
    "7": "%edi",
    "4": "%esp",
    "5": "%ebp",
    "8": "%eax",
    "b": "%ebx",
    "9": "%ecx",
    "a": "%edx",
    "e": "%esi",
    "f": "%edi",
    "c": "%esp",
    "d": "%ebp"
}



def getModrm(instruction):
    unhex = binascii.unhexlify(instruction[2:4])
    unhex = "{0:b}".format(ord(unhex))
    while len(unhex) < 8:
        unhex = "0" + unhex
    return unhex

def endianFlip(constant):
    return "".join(reversed([constant[i:i+2] for i in range(0, len(constant), 2)]))

def prettyHexPrint(instructions, address):

    pretty = " ".join([instructions[i:i + 2] for i in range(0, len(instructions), 2)])
    return str(hex(address)) + ":  " + pretty

def disassemble_x86(instruction, addresscounter):

    if not instruction:
        return ""

    counter = 0
    opcode = instruction[:2]

    if opcode not in opcodes:
        print ("Unrecognized Opcode: "+opcode)
        counter += 2
        addresscounter += 1
    #push/pop
    elif opcode[0] == "5":
        counter += 2
        print(prettyHexPrint(instruction[:counter], addresscounter)+""
                                                                   "              "+opcodes[opcode]+" "+registers[opcode[1]])
        addresscounter += 1

    #dec/inc
    elif opcode[0] == "4":
        counter += 2
        print(prettyHexPrint(instruction[:counter], addresscounter) + ""
                                                                      "              " + opcodes[opcode] + " " +
              registers[opcode[1]])
        addresscounter += 1
    #mov
    elif opcode == "89":
        ascii = getModrm(instruction)
        mod = ascii[0:2]
        reg = ascii[2:5]
        rm = ascii[5:8]
        if mod == "11":
            counter += 4
            print(prettyHexPrint(instruction[:counter], addresscounter)+" "+opcodes[opcode]+"     "+registers[reg]+","+registers[rm])
            addresscounter += 2
    #nop
    elif opcode == "90":
        counter += 2
        print(prettyHexPrint(instruction[:counter], addresscounter) + " " + opcodes[opcode])
        addresscounter += 1
    #lea
    elif opcode == "8D":
        offset = endianFlip(instruction[2:10])
        counter += 10
        print(prettyHexPrint(instruction[:counter], addresscounter) + "    " + opcodes[opcode] + "    " + offset)
        addresscounter += 5

    #cmp
    elif opcode == "39":
        ascii = getModrm(instruction)
        mod = ascii[0:2]
        reg = ascii[2:5]
        rm = ascii[5:8]
        if mod == "11":
            counter += 4
            print(prettyHexPrint(instruction[:counter], addresscounter)+" "+opcodes[opcode]+"     "+registers[reg]+","+registers[rm])
            addresscounter += 2
    #je
    elif opcode == "74":
        offset = instruction[3:4]
        target = int(offset, 16) + addresscounter + 2
        counter += 4
        print(prettyHexPrint(instruction[:counter], addresscounter) + " " + opcodes[opcode] + "     " + hex(target))
        addresscounter += 2

    #mov
    elif opcode == "8b":
        ascii = getModrm(instruction)
        mod = ascii[0:2]
        reg = ascii[2:5]
        rm = ascii[5:8]
        if mod == "01":
            offset = instruction[5:6]
            counter += 6
            print(prettyHexPrint(instruction[:counter], addresscounter)+"     "+opcodes[opcode]+"     0x"+str(offset)+"("+registers[rm]+"),"+registers[reg])
            addresscounter += 3
        elif mod == "10":
            offset = instruction[5:12]
            offset = offset[::-1]
            counter += 12
            print(prettyHexPrint(instruction[:counter], addresscounter) + "     " + opcodes[opcode] + "     0x" + str(offset) + "(" + registers[rm] + ")," + registers[
                reg])
            addresscounter += 6

    #mov
    elif opcode[0] == "b" and int(opcode[1]) >= 8:
        register = str(int(opcode[1]) - 8)
        offset = endianFlip(instruction[2:10])
        counter += 10
        print(prettyHexPrint(instruction[:counter], addresscounter)+"    "+opcodes[opcode]+"    "+offset+","+registers[register])
        addresscounter += 5

    #add
    elif opcode == "00" or opcode == "01" or opcode == "02" or opcode == "03":
        ascii = getModrm(instruction)
        mod = ascii[0:2]
        reg = ascii[2:5]
        rm = ascii[5:8]
        if mod == "11":
            counter += 4
            print(prettyHexPrint(instruction[:counter], addresscounter) + "    " + opcodes[opcode] + "    " + registers[reg] + "," + registers[rm])
            addresscounter += 2

    #and
    elif opcode == "20" or opcode == "21" or opcode == "22" or opcode == "23":
        ascii = getModrm(instruction)
        mod = ascii[0:2]
        reg = ascii[2:5]
        rm = ascii[5:8]
        if mod == "11":
            counter += 4
            print(prettyHexPrint(instruction[:counter], addresscounter) + "    " + opcodes[opcode] + "    " + registers[
                reg] + "," + registers[rm])
            addresscounter += 2

    #out
    elif opcode == "e7":
        offset = instruction[3:4]
        target = int(offset, 16) + addresscounter + 2
        counter += 4
        print(prettyHexPrint(instruction[:counter], addresscounter) + " " + opcodes[opcode] + "     " + hex(target))
        addresscounter += 2

    elif opcode == "82":
        ascii = getModrm(instruction)
        mod = ascii[0:2]
        reg = ascii[2:5]
        rm = ascii[5:8]
        #add
        if reg == "000":
            counter += 4
            print(prettyHexPrint("add ", addresscounter) + "    " + opcodes[opcode] + "    " + registers[
                reg] + "," + registers[rm])
            addresscounter += 2
        #or
        elif reg == "001":
            counter += 4
            print(prettyHexPrint("or ", addresscounter) + "    " + opcodes[opcode] + "    " + registers[
                reg] + "," + registers[rm])
            addresscounter += 2
        #and
        elif reg == "100":
            counter += 4
            print(prettyHexPrint("and ", addresscounter) + "    " + opcodes[opcode] + "    " + registers[
                reg] + "," + registers[rm])
            addresscounter += 2
        #xor
        elif reg == "110":
            counter += 4
            print(prettyHexPrint("xor ", addresscounter) + "    " + opcodes[opcode] + "    " + registers[
                reg] + "," + registers[rm])
            addresscounter += 2

    elif opcode == "83":
        ascii = getModrm(instruction)
        mod = ascii[0:2]
        reg = ascii[2:5]
        rm = ascii[5:8]
        #add
        if reg == "000":
            counter += 14
            print(prettyHexPrint("add ", addresscounter) + "    " + opcodes[opcode] + "    " + registers[
                reg] + "," + instruction[5:15])
            addresscounter += 7
        #or
        elif reg == "001":
            counter += 14
            print(prettyHexPrint("or ", addresscounter) + "    " + opcodes[opcode] + "    " + registers[
                reg] + "," + instruction[5:15])
            addresscounter += 7
        elif reg == "100":
            counter += 14
            print(prettyHexPrint("and ", addresscounter) + "    " + opcodes[opcode] + "    " + registers[
                reg] + "," + instruction[5:15])
            addresscounter += 7
        elif reg == "110":
            counter += 14
            print(prettyHexPrint("xor ", addresscounter) + "    " + opcodes[opcode] + "    " + registers[
                reg] + "," + instruction[5:15])
            addresscounter += 7
    # or
    elif opcode == "20" or opcode == "21" or opcode == "22" or opcode == "23":
        ascii = getModrm(instruction)
        mod = ascii[0:2]
        reg = ascii[2:5]
        rm = ascii[5:8]
        if mod == "11":
            counter += 4
            print(prettyHexPrint(instruction[:counter], addresscounter) + "    " + opcodes[opcode] + "    " +
                      registers[
                          reg] + "," + registers[rm])
            addresscounter += 2

    #push
    elif opcode == "68":
        const = instruction[2:10]
        const = const[::-1]
        counter += 10
        print(prettyHexPrint(instruction[:counter], addresscounter) + "       " + opcodes[opcode] + " $0x" + const)

        addresscounter += 5

    #ret
    elif opcode == "c2":
        immediate = instruction[2:5]
        immediate = endianFlip(immediate)
        counter += 6
        print (prettyHexPrint(instruction[:counter], addresscounter) + "    " + opcodes[opcode] + "    0x" + str(int(immediate)))
        addresscounter += 3
    #clflush
    elif opcode == "ae":
        const = instruction[2:10]
        const = const[::-1]
        counter += 10
        print(prettyHexPrint(instruction[:counter], addresscounter) + "       " + opcodes[opcode] + " $0x" + const)

        addresscounter += 5

    elif opcode == "f6":
        ascii = getModrm(instruction)
        mod = ascii[0:2]
        reg = ascii[2:5]
        rm = ascii[5:8]

        # not
        if reg == "010":
            const = instruction[4:5]
            counter += 6
            print(prettyHexPrint("not ", addresscounter) + modrm[opcode + reg] + " " + const + "")
        addresscounter += 3
        # neg
        if reg == "011":
            const = instruction[4:5]
            counter += 6
            print(prettyHexPrint("neg ", addresscounter) + modrm[opcode + reg] + " " + const + "")
        addresscounter += 3

    elif opcode == "ff":
        ascii = getModrm(instruction)
        mod = ascii[0:2]
        reg = ascii[2:5]
        rm = ascii[5:8]

        #mov
        if mod == "00" and reg == "110" and rm == "101":
            const = instruction[4:12]
            const = const[::-1]
            counter += 14
            print(prettyHexPrint(instruction[:counter], addresscounter) + modrm[opcode + reg] + " dword [ " + const + " ]")
        #call
        elif reg == "001":
            const = instruction[4:12]
            const = const[::-1]
            counter += 14
            print(prettyHexPrint("call ", addresscounter) + modrm[opcode + reg] + " dword [ " + const + " ]")
        #jmp
        elif reg == "010":
            const = instruction[4:12]
            const = const[::-1]
            counter += 14
            print(prettyHexPrint("jmp ", addresscounter) + modrm[opcode + reg] + " dword [ " + const + " ]")


        addresscounter += 7
    disassemble_x86(instruction[counter:], addresscounter)



def main():
    with open(sys.argv[1], 'rb') as f:
            byte = f.read()
            disassemble_x86(binascii.hexlify(byte), 0)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("""Python disassembler\nUsage: """ + sys.argv[0] + """ [filepath]""")
    else:
        main()
