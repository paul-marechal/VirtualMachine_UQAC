# -*- coding:utf8 -*-
from ..utilities import int16
from .IComponent import *
from .ALU import *

class CPU(IComponent):
    """CENTRAL PROCESSING UNIT"""

    STATUS_PARITY = 0
    STATUS_SIGN = 1
    STATUS_CARRY = 2
    STATUS_ZERO = 3
    STATUS_CND = 4

    def __init__(self, bus):
        super().__init__(bus)
        self.ALU = ALU() # Inutile dans notre implémentation ?

        # A B C D
        self.REGISTERS = [0 for i in range(4)]

        # S, P et I
        self.STATE = 0
        self.PC = 0
        self.IR = 0

    def getStatusBit(self, bit):
        return int16.BitGet(self.STATUS, bit)

    def setStatusBit(self, bit, val):
        self.STATUS = int16.BitSet(self.STATUS, bit, val)
        return self

    def getRegister(self, reg):
        """Register is from 0x01 to 0x04,
        but indices range from 0 to 3..."""
        i = reg - 1
        if i < 0 or i > 3:
            raise ValueError('Register at 0x%x is invalid' % reg)
        return self.REGISTERS[i]

    def setRegister(self, reg, val):
        i = reg - 1
        self.REGISTERS[i] = val
        return self

    def getShared(self, adr):
        """Get data through the BUS"""
        pass

    def setShared(self, adr, val):
        """Set data through the BUS"""
        pass

    def fetch(self):
        pass

    def decode(self):
        pass

    def execute(self):
        pass

    def clock(self):
        self.fetch()
        self.decode()
        self.execute()

    # MEGA DEF OF DOOM
    def invoke(self, method):
        """CPU_OBJECT.invoke(OP)(*args)"""
        try:
            return getattr(self, method.upper())
        except AttributeError: # Empty function
            return lambda *args, **kargs: None

    def Managed(*types, store=None, status=None):
        """This ensure each function affects correctly the different CPU registers.
        Also allows for fuzzy arguments conversion.
        Types:
         - r, reg, register
         - a, adr, address
         - v, val, value
        """

        TYPES = {
            'register': ('r', 'reg', 'register'),
            'address': ('a', 'adr', 'address'),
            'value': ('v', 'val', 'value', None),
        }

        def decorator(func):
            """The actual decorator"""

            def modified(self, *args):
                """Decorated _INSTANCE_ function"""

                # Argument conversion based on 'types'
                cargs = []
                for i in range(len(types)):
                    carg = args[i]
                    T = types[i]

                    if T in TYPES['register']:
                        carg = self.getRegister(carg)

                    elif T in TYPES['address']:
                        carg = self.getShared(carg)

                    elif T not in TYPES['value']:
                        raise TypeError('Managed type is invalid [%s]' % T)

                    cargs.append(carg)

                # Complete the rest
                cargs += args[i+1:]

                # Call with converted args the function
                value = func(*cargs)

                # Check for parity
                parity = int16.BitGet(0)
                self.setStatusBit(self.STATUS_PARITY, parity)

                # Check sign
                sign = 0
                if value < 0:
                    value = abs(value)
                    sign = 1
                self.setStatusBit(self.STATUS_CARRY, sign)

                # Check for overflow
                overflow, cleanValue = int16.Overflow(value)
                self.setStatusBit(self.STATUS_CARRY, int(overflow))

                if status is not None:
                    self.setStatusBit(status, cleanValue)

                if store is not None:
                    i = stored - 1
                    if types[i] not in TYPES['register']:
                        raise TypeError("Can't store your shit")
                    self.setRegister(args[i], cleanValue)

                return value

            return modified

        return decorator

    ###
    # Data manipulation

    @Managed('r', 'v', store=1)
    def SET(self, reg, val): return val

    @Managed('r', 'a', store=1)
    def LD(self, reg, adr): return adr

    @Managed('r', 'v') # Little hack for setting distant address
    def ST(self, reg, adr): self.setShared(adr, reg)

    @Managed('r', 'r', store=1)
    def MV(self, reg1, reg2): return reg2

    ###
    # Comparisons

    @Managed('r', 'r', status=STATUS_CND)
    def LT(self, reg1, reg2): return int(reg1 < reg2)

    @Managed('r', 'r', status=STATUS_CND)
    def GT(self, reg1, reg2): return int(reg1 > reg2)

    @Managed('r', 'r', status=STATUS_CND)
    def LE(self, reg1, reg2): return int(reg1 <= reg2)

    @Managed('r', 'r', status=STATUS_CND)
    def GE(self, reg1, reg2): return int(reg1 >= reg2)

    @Managed('r', 'r', status=STATUS_CND)
    def EQ(self, reg1, reg2): return int(reg1 == reg2)

    @Managed('r', status=STATUS_CND)
    def EZ(self, reg1): return int(reg1 == 0)

    @Managed('r', status=STATUS_CND)
    def NZ(self, reg1): return int(reg1 != 0)

    ###
    # Logic

    @Managed('r', 'r', store=1)
    def OR(self, reg1, reg2): return reg1 | reg2

    @Managed('r', 'r', store=1)
    def AND(self, reg1, reg2): return reg1 & reg2

    @Managed('r', 'r', store=1)
    def XOR(self, reg1, reg2): return reg1 ^ reg2

    @Managed('r', store=1)
    def NOT(self, reg1): return int16.Inverse(reg1)

    ###
    # Basic operations

    @Managed('r', 'r', store=1)
    def ADD(self, reg1, reg2): return reg1 + reg2

    @Managed('r', 'r', store=1)
    def SUB(self, reg1, reg2): return reg1 - reg2

    @Managed('r', 'r', store=1)
    def MUL(self, reg1, reg2): return reg1 * reg2

    @Managed('r', 'r', store=1)
    def DIV(self, reg1, reg2): return reg1 / reg2

    ###
    # Flow control

    @Managed('a')
    def JMP(self, adr):
        self.IR = adr
        return adr

    @Managed('a')
    def JMZ(self, adr):
        if self.getStatusBit(self.STATUS_ZERO):
            self.IR = adr
        return adr

    @Managed('a')
    def JMO(self, adr):
        if self.getStatusBit(self.STATUS_CARRY):
            self.IR = adr
        return adr

    @Managed('a')
    def JMC(self, adr):
        if self.getStatusBit(self.STATUS_CND):
            self.IR = adr
        return adr

    # \o/
    def NOP(self): pass
    def HALT(self): pass
