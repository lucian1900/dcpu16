import re

comment_pattern = re.compile(r';.*\n')
separators = [':', ',', '[', ']', '+', '-']

basic_op = ['SET', 'ADD', 'SUB', 'MUL', 'DIV', 'MOD', 'SHL', 'SHR', 'AND',
            'BOR', 'XOR', 'IFE', 'IFN', 'IFG', 'IFB']
reg_names = ['A', 'B', 'C', 'X', 'Y', 'Z', 'I', 'J']
sreg_names = ['POP', 'PEEK', 'PUSH', 'SP', 'PC', 'O']

def disassemble(code):
    'Ported from https://gist.github.com/2300590'

    PC = [0]

    def operand(bits):

        if bits <= 0x07:
            return reg_names[bits]

        if bits <= 0x0f:
            return '[{0}]'.format(reg_names[bits - 0x08])

        if bits <= 0x17:
            PC[0] += 1
            return '[{0}+{1}]'.format(hex(code[PC[0]]), reg_names[bits - 0x10])

        if bits == 0x18:
            return 'POP'

        if bits == 0x19:
            return 'PEEK'

        if bits == 0x1a:
            return 'PUSH'

        if bits == 0x1b:
            return 'SP'

        if bits == 0x1c:
            return 'PC'

        if bits == 0x1d:
            return 'O'

        if bits == 0x1e:
            PC[0] += 1
            return '[{0}]'.format(hex(code[PC[0]]))

        if bits == 0x1f:
            # literal
            PC[0] += 1
            return hex(code[PC[0]])

        # literal
        return hex(bits - 0x20)

    asm = []

    while PC[0] < len(code):
        inst = code[PC[0]]

        if inst & 0xf == 0:
            # non-basic
            if ((inst >> 4) & 0x3f) == 0x01:
                asm.append('JSR ' + operand(inst >> 10))
        else:
                asm.append('{0} {1}, {2}'.format(basic_op[inst & 0xf - 1],
                                                 operand((inst >> 4) & 0x3f),
                                                 operand(inst >> 10)))

        PC[0] += 1

    return '\n'.join(asm)


def value(toks):
    regs = dict((e, i) for i, e in enumerate(reg_names))
    sregs = dict((e, i + 0x18) for i, e in enumerate(sreg_names))

    if toks[0] in regs:
        return regs[toks[0]]

    if toks[0] == '[' and toks[2] == ']' and toks[1] in sregs:
        return sregs[toks[1]]

    return -1


def assemble(source):
    ops = dict((e, i + 0x1) for i, e in enumerate(basic_op))

    insts = lex(source)
    binary = []

    labels = {}
    for i, inst in enumerate(insts):
        if inst[0] == ':':
            if isinstance(inst, str):
                labels[inst[1]] = i
                insts[i] = insts[2:]
            else:
                raise SyntaxError("Expected string label, got: {0}" \
                                    .format(inst))

    for i, inst in enumerate(insts):
        if inst[0] == 'JSR':
            low = 0x0
            mid = 0x01
            high = value(inst[1])
        else:
            # basic op
            low = ops[inst[0]]

            try:
                comma = inst.index(',')
            except ValueError:
                raise SyntaxError("Expected , in {0}".format(' '.join(inst)))

            mid = value(inst[1:comma])
            high = value(inst[comma + 1:]) << 10

        binary.append(low + (mid << 4) + (high << 10))

    return binary


def lex(source):
    source = re.sub(comment_pattern, '\n', source)
    lines = source.split('\n')

    for i, _ in enumerate(lines):
        for s in separators:
            lines[i] = lines[i].replace(s, ' {0} '.format(s))

        lines[i] = lines[i].split()

    return filter(len, lines)


if __name__ == '__main__':
    prog = [
        0x7c01, 0x0030, 0x7de1, 0x1000, 0x0020, 0x7803, 0x1000, 0xc00d,
        0x7dc1, 0x001a, 0xa861, 0x7c01, 0x2000, 0x2161, 0x2000, 0x8463,
        0x806d, 0x7dc1, 0x000d, 0x9031, 0x7c10, 0x0018, 0x7dc1, 0x001a,
        0x9037, 0x61c1, 0x7dc1, 0x001a, 0x0000, 0x0000, 0x0000, 0x0000]

    asm = disassemble(prog)
    print asm

    print assemble(asm)

    print assemble(":foo SET PC 0x01")
