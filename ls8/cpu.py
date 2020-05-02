"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.pc = 0
        self.ir = None
        self.ram = [0] * 256
        self.sp = 256
        self.commands = {
            0b00000001: self.hlt,
            0b10000010: self.ldi,
            0b01000111: self.prn,
            0b10100010: self.mul,
            0b01000101: self.push,
            0b01000110: self.pop,
            0b01010000: self.call,
            0b00010001: self.iret,
            0b10100000: self.add,
            0b10100111: self.cmp,
            0b01010100: self.jmp,
            0b01010101: self.jeq,
            0b01010110: self.jne
        }

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def hlt(self, operand_a, operand_b):
        return (0, False)

    def ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b
        return (3, True)

    def prn(self, operand_a, operand_b):
        print(self.reg[operand_a])
        return(2, True)

    def mul(self, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)
        return (3, True)
    
    def add(self, operand_a, operand_b):
        self.alu("ADD", operand_a, operand_b)
        return (3, True)

    def push(self, operand_a, operand_b):
        self.sp -= 1
        value = self.reg[operand_a]
        self.ram[self.sp] = value
        return (2, True)
    
    def pop(self, operand_a, operand_b):
        pop_value = self.ram[self.sp]
        reg_address = operand_a
        self.reg[reg_address] = pop_value
        self.sp += 1
        return (2, True)

    def call(self, operand_a, operand_b):
        next_address = self.pc + 2
        self.reg[2] = next_address
        self.push(2, None)

        routine_address = self.reg[operand_a]
        self.pc = routine_address
        return (0, True)
    
    def iret(self, *args):
        self.pop(2, None)
        next_address = self.reg[2]
        self.pc = next_address
        return (0, True)

    def cmp(self, operand_a, operand_b):
        self.alu("CMP", operand_a, operand_b)
        return (3, True)

    def jmp(self, operand_a, operand_b):
        self.pc = self.reg[operand_a]
        return (0, True)

    def jeq(self, operand_a, operand_b):
        if self.flag == 0b00000001:
            self.pc = self.reg[operand_a]
            return (0, True)
        return (2, True)

    def jne(self, operand_a, operand_b):
        if self.flag != 0b00000001:
            self.pc = self.reg[operand_a]
            return (0, True)
        return (2, True)

    def load(self, program):
        address = 0

        with open(program) as f:
            for line in f:
                comment_split = line.split('#')
                num = comment_split[0].strip()

                try:
                    self.ram_write(int(num, 2), address)
                    address += 1
                except ValueError:
                    pass


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] = (self.reg[reg_a] * self.reg[reg_b])
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.flag == 0b00000001
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.flag = 0b00000010
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.flag = 0b00000100
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        running = True
        
        while running:
            instruction_register = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            try:
                f = self.commands[instruction_register]
                operation_op = f(operand_a, operand_b)
                running = operation_op[1]
                self.pc += operation_op[0]

            except:
                print(f"Error: Instruction {instruction_register} not found")
                sys.exit(1)
