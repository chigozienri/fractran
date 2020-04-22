class f_int:
    """Represent an integer as the product of its prime factors"""
    def __init__(self, n):
        self.n = n
        self.factors = self.factorize(n)
        
    def factorize(self, a):
        """
        Get prime factors of a,
        return as dictionary with keys as factors and values as count of each factor
        """
        factors = {}
        for i in range(2, int(a**0.5) + 1):
            while a % i == 0:
                if not i in factors:
                    factors[i] = 1
                else:
                    factors[i] += 1
                a //= i
        if a > 1:
            if not a in factors:
                factors[a] = 1
            else:
                factors[a] += 1
                
        return factors

    def __repr__(self):
        """Print in form '2^a * 3^b * 5^c * ...''"""
        return ' * '.join([f'{key}^{value}' for key, value in self.factors.items()])


class FractionGame:
    """Represent a FRACTRAN-1 program, and play the 'fraction game' on it"""
    def __init__(self, *args, N_0=2):
        if type(N_0) is not int:
            raise RuntimeError("Starting value N_0 must be integer")
        for frac in args:
            if type(frac) is not tuple:
                raise RuntimeError("fractions must be tuples")
            if len(frac) != 2:
                raise RuntimeError("Each fraction must be a pair of ints")
            if type(frac[0]) is not int:
                raise RuntimeError(f"Numerator {frac[0]} is a {type(frac[0])}, not an int")
            if type(frac[1]) is not int:
                raise RuntimeError(f"Denominator {frac[1]} is not an int")
            # should probably check if fraction is the simplest possible, because otherwise it will mess with my program interpretation, but whatever
                
        self.f = tuple(frac for frac in args)
        self.N = [N_0]
        self.transitions = []
        self.registers = self.get_registers()

    
    def __repr__(self):
        history = []
        for i, N_i in enumerate(self.N):
            if i < len(self.transitions):
                fraction = self.f[self.transitions[i]]
                history.append(f'{f_int(N_i)}\n*{fraction[0]}/{fraction[1]} ({chr(self.transitions[i]+65)})')
            else:
                history.append(f'{f_int(N_i)}')
        return '\n'.join(history)
    
    def get_registers(self):
        """
        Given the list of fractions in a program, check what registers that program uses
        (the set of prime factors of the numerators and denominators of all fractions)
        """
        registers = {}
        for i, f in enumerate(self.f):
            numerator = f_int(f[0]).factors
            for factor in numerator:
                registers[factor] = 0
            denominator = f_int(f[1]).factors
            for factor in denominator:
                registers[factor] = 0
        return registers
    
    def python_equivalent(self, max_steps=100):
        """
        Print the FRACTRAN program as an equivalent runnable python program,
        making clear the register machine structure
        """
        python_program = []
        registers = self.registers
        python_program.append('# Starting conditions')
        N_0_factors = f_int(self.N[0]).factors
        python_program.append('registers = {}')
        for factor in N_0_factors.keys():
            registers[factor] = N_0_factors[factor]
        for factor in sorted(registers.keys()):
            python_program.append(f'registers[{factor}] = {registers[factor]}')
        python_program.append('\n# Main Loop')
        python_program.append("counter = 0")
        python_program.append('while sum(registers.values()) > 0:')
        python_program.append('\tcounter += 1')
        for i, f in enumerate(self.f):
            numerator = f_int(f[0]).factors
            denominator = f_int(f[1]).factors
            conditions = []
            endloop=False
            for factor in denominator.keys():
                conditions.append(f'registers[{factor}] >= {denominator[factor]}')
            
            if i == 0:
                python_program.append(f"\tif ({') & ('.join(conditions)}): # fraction {chr(i+65)} ({f[0]}/{f[1]})")
            elif f[1] == 1:
                python_program.append(f"\telse: # fraction {chr(i+65)} ({f[0]}/{f[1]})")
                endloop=True
            else:
                python_program.append(f"\telif ({') & ('.join(conditions)}): # fraction {chr(i+65)} ({f[0]}/{f[1]})")
            if f[0] == 0:
                python_program.append('\t\tregisters.clear()')
            else:
                for factor in denominator.keys():
                    python_program.append(f'\t\tregisters[{factor}] -= {denominator[factor]}')
                for factor in numerator.keys():
                    python_program.append(f'\t\tregisters[{factor}] += {numerator[factor]}')

        if not endloop:
            python_program.append(f"\telse:")
            python_program.append(f"\t\tregisters.clear()")
        

        python_program.append(f"\tprint(' * '.join([str(factor) + '^' + str(registers[factor]) for factor in registers.keys()]))")
        python_program.append(f'\tif counter > {max_steps}:')
        python_program.append('\t\tbreak')
        return '\n'.join(python_program)
    
    def run_step(self, verbose=0):
        for i, (numerator, denominator) in enumerate(self.f):

            if verbose == 2:
                print(f'trying {numerator}/{denominator} * {self.N[-1]}')

            if (numerator * self.N[-1]) % denominator == 0:
                next_N = (numerator * self.N[-1]) // denominator
                if verbose > 0:
                    print(f'Success! N_{len(self.N)} = {numerator}/{denominator}*{self.N[-1]} = {next_N} = {str(f_int(next_N))}')
                self.N.append(next_N)
                self.transitions.append(i)
                return
        # If none of the products is an integer, append 0 to halt.
        self.N.append(0)
    
    def run(self, N_0=None, verbose=0, max_steps=100):
        """Repeatedly run the FRACTRAN program until halt or max_steps is reached"""
        if N_0:
            self.N = [N_0]
        while self.N[-1] is not 0:
            self.run_step(verbose=verbose)
            if len(self.N) + 1 > max_steps:
                self.N.append(0)