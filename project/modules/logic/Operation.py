# -*- coding:utf8 -*-
import re

class CompilationError(Exception): pass

class Operation(object):

    DEFINED = {
        'DTA':  (0, 'val'),


        'SET':  (0x0500, 'reg', 0, 'val'),
        'LD':   (0x0600, 'reg', 0, 'val'),
        'ST':   (0x0700, 'reg', 0, 'adr'),
        'MV':   (0x0800, 'reg', 0, 'reg'),

        'ADD':  (0x1100, 'reg', 0, 'reg'),
        'SUB':  (0x1200, 'reg', 0, 'reg'),
        'MUL':  (0x1300, 'reg', 0, 'reg'),
        'DIV':  (0x1400, 'reg', 0, 'reg'),

        'OR':   (0x2100, 'reg', 0, 'reg'),
        'AND':  (0x2200, 'reg', 0, 'reg'),
        'XOR':  (0x2300, 'reg', 0, 'reg'),
        'NOT':  (0x2400, 'reg'),

        'LT':   (0x3100, 'reg', 0, 'val'),
        'GT':   (0x3200, 'reg', 0, 'val'),
        'LE':   (0x3300, 'reg', 0, 'val'),
        'GE':   (0x3400, 'reg', 0, 'val'),
        'EQ':   (0x3500, 'reg', 0, 'val'),
        'EZ':   (0x3600, 'reg'),
        'NZ':   (0x3700, 'reg'),

        'JMP':  (0x0100, 'adr'),
        'JMZ':  (0x0200, 'adr'),
        'JMO':  (0x0300, 'adr'),
        'JMC':  (0x0400, 'adr'),

        'NOP':  (0x0000,),
        'HLT':  (0x0F00,)
    }

    REGISTER = {
        "A": 0x01,
        "B": 0x02,
        "C": 0x03,
        "D": 0x04,
    }

    def __init__(self, BASECODE, *args): pass
    # phew. need more thinkin.

    @classmethod        
    def compile(cls, source):
        command = source.split(" ")      
        while command.count(''): del command[command.index('')]
        if len(command) != 0:
            '''
            TEST DTA
            '''
            if command[0] == "DTA":
                arg = ' '.join(command[1:])
                parsed = None
                compiled =[]

                try:
                    parsed = int(arg)
                    return '%d' % (parsed)
                except:
                    try:

                        p = re.compile('^".*"$')
                        if p.match(arg) is None: 
                            raise CompilationError("Argument incorrect")
                        else:
                            parsed = arg[1:-1]
                            for c in parsed:
                                compiled.append(str(ord(c)))
                            return ' '.join(compiled)              

                    except Exception as e:
                        raise e


            '''
            AUTRE Operation
            '''
            Op = cls.DEFINED[str(command[0])]

            #Test les operation sans argument
            if len(command) == 1 and (command[0] == "NOP" or command[0] == "HLT")  :
                return '%d' % (Op[0])

            #Test Si l'operation a le bon nombre d'argument   
            elif len(command[1:]) == len(Op)/2:

                #Test si le premier argument attendu est bien le bon ici registre
                if Op[1] == 'reg' and command[1] in 'ABCD':   

                    if len(command)>2:

                        if Op[3] == 'reg' and command[2] in 'ABCD':
                            int1 = Op[0]+cls.REGISTER[str(command[1])]
                            int2 = 0x0000 + cls.REGISTER[str(command[2])]
                            return '%d %d' % (int1,int2)     

                        elif Op[3] == 'adr' or Op[3] == 'val':
                            try:
                                int2 = int(command[2],0)
                                int1 = Op[0]+cls.REGISTER[str(command[1])]
                                return '%d %d' % (int1,int2)
                            except:
                                raise CompilationError('Argument non valide: Adresse ou valeur attendu')

                        else:
                            raise CompilationError('Argument non valide: Registre attendu')

                    else:
                        int1 = Op[0]+cls.REGISTER[str(command[1])]
                        return '%d' % (int1)

                #Test si le premier argument attendu est bien le bon ici une adresse       
                elif Op[1] == 'adr':
                    try:
                        int1 = Op[0]
                        int2 = int(command[1],0)
                        return '%d %d' % (int1,int2)

                    except:
                        raise CompilationError('Argument non valide: Adresse attendu')

                #Si Op[1] == 'reg' mais que l argument n est pas un registre
                else :
                    raise CompilationError('Argument non valide: Registre attendu')

            else:
                raise CompilationError("Nombre d'argument incorrect")
				
        else:
            return '';
   

