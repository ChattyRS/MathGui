from typing import List, Tuple, Union
import sys
import math
import re
import cmath
import matplotlib.pyplot as plt
import numpy as np
import sympy
from utils import is_int, is_float, float_to_formatted_string
from forex_python.converter import CurrencyRates
from utils import units, unit_aliases
import io

numeric = Union[int, float, complex, np.number]

np.seterr(all='raise')

pi = math.pi
alpha = 2.502907875095892822283902873218
delta = 4.669201609102990671853203821578
theta = 1.30637788386308069046861449260260571
tau = math.tau
phi = 1.6180339887498948482
gamma = 0.57721566490153286060651209008240243104215933593992
lambda_var = 1.303577269034
psi = 3.35988566624317755317201130291892717
rho = 1.32471795724474602596090885447809734
e = math.e
i = complex(0,1)
inf = math.inf
pattern = '(?<=[0-9a-z])(?<!log)(?<!sqrt)(?<!floor)(?<!ceil)(?<!sin)(?<!cos)(?<!tan)(?<!round)(?<!abs)(?<!inf)(?<!x)(?<!sum)(?<!product)\('
legal = ['log', 'sqrt', 'floor', 'ceil', 'sin', 'cos', 'tan', 'round', 'abs', 'pi', 'alpha', 'delta', 'theta', 'tau', 'phi', 'gamma', 'lambda', 'psi', 'rho', 'e', 'i', 'inf', 'mod', 'x', 'sum', 'product']
pattern_graph = '(?<=[0-9a-z])(?<!log)(?<!sqrt)(?<!floor)(?<!ceil)(?<!sin)(?<!cos)(?<!tan)(?<!round)(?<!abs)(?<!x)\('
legal_graph = ['log', 'sqrt', 'floor', 'ceil', 'sin', 'cos', 'tan', 'round', 'abs', 'pi', 'alpha', 'delta', 'theta', 'tau', 'phi', 'gamma', 'lambda', 'psi', 'rho', 'e', 'mod', 'x']
pattern_solve = '(?<=[0-9a-z])(?<!log)(?<!sqrt)(?<!sin)(?<!cos)(?<!tan)(?<!x)\('
legal_solve = ['log', 'sqrt', 'sin', 'cos', 'tan', 'pi', 'alpha', 'delta', 'theta', 'tau', 'phi', 'gamma', 'lambda', 'psi', 'rho', 'e', 'x', 'i']


def get_currency_rate(input: str, output: str) -> numeric:
    '''
    Gets the currency rate from currency input to currency output
    '''
    c = CurrencyRates()
    rates = c.get_rates(input)
    rate = rates[output]
    return rate

def get_alias(unit: str) -> str:
    '''
    Gets the best matching unit for the given unit / alias
    '''
    best = ''
    dif = math.inf
    for alias in unit_aliases:
        if unit in alias:
            if len(alias) - len(unit) < dif:
                dif = len(alias) - len(unit)
                best = alias
    return unit_aliases[best]

def calcsum(start: int, end: int, f: str) -> numeric:
    '''
    Calculates the sum of the given function f(x) from given start to end (fixed steps of 1).
    '''
    if not isinstance(f, str):
        f = str(f)
    sum = 0
    for index in range(start,end+1):
        res = eval(f.replace('x', str(index)))
        sum += res
    return sum

def calcproduct(start: int, end: int, f: str) -> numeric:
    '''
    Calculates the product of function f(x) from given start to end (fixed steps of 1).
    '''
    if not isinstance(f, str):
        f = str(f)
    product = 1
    for index in range(start,end+1):
        res = eval(f.replace('x', str(index)))
        product *= res
    return product


def calculate(input: str) -> numeric:
    '''
    Calculate the result of a mathematical expression.
    The result is written under key 'val' in the input dictionary of the same name.
    '''
    return eval(input)

def format_input(input: str, style: int) -> str:
    '''
    Sanitize and format the user-input mathematical expression
    Style 0 = math, 1 = graph, 2 = solve
    '''
    # Get list of 'words' included in the user input
    word_list = re.sub('(?:[0-9]|[^\w])', ' ', input).split()

    # Validate for each distinct style if all word occurrences are allowed
    if style == 0:
        for word in word_list:
            if not word in legal:
                raise ValueError(f'Illegal argument: {word}')
    elif style == 1:
        for word in word_list:
            if not word in legal_graph:
                raise ValueError(f'Illegal argument: {word}')
    elif style == 2:
        for word in word_list:
            if not word in legal_solve:
                raise ValueError(f'Illegal argument: {word}')

    # Replace operators with python notation / functions
    input = input.replace('mod', '%')
    if style == 0:
        input = input.replace('sin', 'cmath.sin')
        input = input.replace('cos', 'cmath.cos')
        input = input.replace('tan', 'cmath.tan')
        input = input.replace('floor', 'math.floor')
        input = input.replace('ceil', 'math.ceil')
        input = input.replace('sqrt', 'cmath.sqrt')
        input = input.replace('log', 'cmath.log')
        input = input.replace('sum', 'calcsum')
        input = input.replace('product', 'calcproduct')
    elif style == 1:
        input = input.replace('sin', 'np.sin')
        input = input.replace('cos', 'np.cos')
        input = input.replace('tan', 'np.tan')
        input = input.replace('round', 'np.round_')
        input = input.replace('floor', 'np.floor')
        input = input.replace('ceil', 'np.ceil')
        input = input.replace('sqrt', 'np.sqrt')
        input = input.replace('log', 'np.log')
    input = input.replace(')(', ')*(')
    input = input.replace('^', '**')
    input = input.replace('lambda', 'lambda_var')

    # Prepend and append multiplication symbols to any strings 
    # matching the pattern depending on the style
    if style == 0:
        input = re.sub(pattern, '*(', input)
    elif style == 1:
        input = re.sub(pattern_graph, '*(', input)
    elif style == 2:
        input = re.sub(pattern_solve, '*(', input)
    input = re.sub('\)(?=[0-9a-z])', ')*', input)

    # For any indices where a number is followed by a letter or vice versa,
    # Insert a multiplication symbol
    indices = []
    for index, char in enumerate(input):
        if len(input) > index+1:
            if re.search('[\d]', char):
                next_char = input[index+1]
                if re.search('[a-z]', next_char):
                    indices.append(index)
        if len(input) > index+1:
            if re.search('[a-z]', char):
                next_char = input[index+1]
                if re.search('[\d]', next_char):
                    indices.append(index)
    for index in reversed(indices):
        input = input[:index+1] + '*' + input[index+1:]
    
    # If using the math command, validate formatting for sum and product functions
    if style == 0:
        indices = []
        for index, char in enumerate(input):
            if char == 'x':
                check = 0
                j = index
                parentheses = 0
                while j >= 0:
                    if input[j] == ',':
                        indices.append(j)
                        check += 1
                        break
                    elif input[j] == '(':
                        parentheses += 1
                    elif input[j] == ')':
                        parentheses -= 1
                    j -= 1
                j = index
                while len(input) > j:
                    if input[j] == '(':
                        parentheses += 1
                    elif input[j] == ')' and parentheses == 0:
                        indices.append(j-1)
                        check += 1
                        break
                    elif input[j] == ')':
                        parentheses -= 1
                    j += 1
                if not check == 2:
                    raise ValueError(f'Incorrectly formatted function f(x) at index {index}')
        for index in sorted(indices, reverse=True):
            input = input[:index+1] + '\'' + input[index+1:]
    
    # If using the math command, format factorials
    if style == 0:
        # Get all indices of occurrences of '!'
        indices = [i for i, char in enumerate(input) if char == '!']
        # Construct a dictionary mapping each index of an occurrence of '!' to its depth level of parentheses.
        # E.g. (10!)! would have depth 1 for the first occurrence, and depth 0 for the second.
        parentheses_depth_dict = {}
        for index in indices:
            parentheses_depth_dict[index] = parentheses_depth(input, index)
        
        # Loop through occurrences of '!' in descending order of parentheses depth level
        processed = []
        for occurrence in sorted([i for i in range(len(indices))], key=lambda i: parentheses_depth_dict[indices[i]], reverse=True):
            # In each iteration an occurrence is removed, 
            # hence for each occurrence we need to subtract 1 for each processed earlier occurrence
            occurrence -= len([p for p in processed if p < occurrence])

            # Get the current index of this occurrence
            index = index_of_occurrence(input, '!', occurrence+1)

            # Replace f(x)! by math.factorial(f(x))
            # First replace the '!' by ')'
            input = input[:index] + ')' + input[index+1:]
            # Then find the index to insert 'math.factorial('
            parentheses = 0
            for i, char in enumerate(reversed(input[:index])):
                if char == ')':
                    parentheses += 1
                    continue
                elif char == '(':
                    parentheses -= 1
                    continue
                # If this is the first character of the string, then insert here
                if index - i == 1:
                    input = 'math.factorial(' + input
                    break
                # If this is a number and the next (i.e. preceding) character is not a number, insert here
                elif parentheses == 0 and re.search('[\d]', char):
                    if not re.search('[\d]', input[index-i-2]):
                        input = input[:index-i-1] + 'math.factorial(' + input[index-i-1:]
                        break
                # If this character is not a number and not a letter, decimal point, or underscore, insert here
                elif parentheses == 0 and not re.search('[a-z]|\.|_', char):
                    input = input[:index-i-1] + 'math.factorial(' + input[index-i-1:]
                    break
                

            processed.append(occurrence)

    return input

def parentheses_depth(input: str, index: int) -> int:
    '''
    Get the depth level of parentheses at the given index in the input string.
    '''
    depth = 0
    for char in input[:index]:
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
    return depth

def index_of_occurrence(input: str, sub: str, n: int) -> int:
    '''
    Gets the index of the nth occurrence of the given substring in the input string.
    '''
    occurrence, index = 0, 0
    while occurrence < n:
        index = input[index+(1 if index > 0 else 0):].index(sub) + index + (1 if index > 0 else 0)
        occurrence += 1
    return index

def format_output(result: numeric) -> str:
    '''
    Format the output result as a mathematical expression
    '''
    if isinstance(result, complex):
        if cmath.isclose(result.imag, 0, abs_tol=1*10**(-11)):
            result = result.real
        elif cmath.isclose(result.real, 0, abs_tol=1*10**(-11)):
            result = complex(0, result.imag)
    if isinstance(result, complex):
        if (math.isinf(result.real) and result.real > 0) and (math.isinf(result.imag) and result.imag > 0):
            result = '∞ + ∞i'
        elif (math.isinf(result.real) and result.real < 0) and (math.isinf(result.imag) and result.imag < 0):
            result = '-∞ - ∞i'
        elif (math.isinf(result.real) and result.real > 0) and (math.isinf(result.imag) and result.imag < 0):
            result = '∞ - ∞i'
        elif (math.isinf(result.real) and result.real < 0) and (math.isinf(result.imag) and result.imag > 0):
            result = '-∞ + ∞i'
        elif (math.isinf(result.real) and result.real > 0):
            result = f'∞ + {result.imag}i'
        elif (math.isinf(result.imag) and result.imag > 0):
            result = f'{result.real} + ∞i'
        elif (math.isinf(result.real) and result.real < 0):
            result = f'-∞ + {result.imag}i'
        elif (math.isinf(result.imag) and result.imag < 0):
            result = f'{result.real} - ∞i'
    if isinstance(result, float):
        if math.isinf(result) and result > 0:
            result = '∞'
        elif math.isinf(result) and result < 0:
            result = '-∞'
        elif result.is_integer():
            result = round(result)
    result = str(result)

    result = result.replace('j', 'i')
    result = result.replace('(', '')
    result = result.replace(')', '')

    return result

def beautify_input(input: str) -> str:
    '''
    Make the user-input pretty when showing it in the result
    '''
    #input = input.replace('*', '\*')
    input = input.replace('pi', 'π')
    input = input.replace('alpha', 'α')
    input = input.replace('delta', 'δ')
    input = input.replace('theta', 'θ')
    input = input.replace('tau', 'τ')
    input = input.replace('phi', 'φ')
    input = input.replace('gamma', 'γ')
    input = input.replace('lambda', 'λ')
    input = input.replace('psi', 'ψ')
    input = input.replace('rho', 'ρ')
    input = input.replace('inf', '∞')
    input = input.replace('sum', 'Σ')
    input = input.replace('product', '∏')
    input = input.replace('sqrt', '√')
    input = input.replace('x', '𝓍')
    input = input.replace('i', '𝑖')
    input = input.replace('e', '𝑒')
    input = input.replace('s𝑖n', 'sin')
    return input

def solve_for_x(input: str) -> List[numeric]:
    '''
    Reformat input and solve the resulting mathematical equality for x.
    Output(s) are added to the values of dictionary 'val'.
    '''
    input = input.replace('pi', str(pi))
    input = input.replace('alpha', str(alpha))
    input = input.replace('delta', str(delta))
    input = input.replace('theta', str(theta))
    input = input.replace('tau', str(tau))
    input = input.replace('phi', str(phi))
    input = input.replace('gamma', str(gamma))
    input = input.replace('lambda', str(lambda_var))
    input = input.replace('psi', str(psi))
    input = input.replace('rho', str(rho))
    input = input.replace('e', str(e))
    input = input.replace('i', 'I')
    input = input.replace('sIn', 'sin')
    if not 'x' in input:
        raise ValueError('No variable \'x\' in equation')
    inputs = input.split('=')
    if len(inputs) == 1:
        raise ValueError('No equality sign \'=\' in equation')
    elif len(inputs) > 2:
        raise ValueError('More than one equality sign \'=\' in equation')
    input = f'Eq({inputs[0]}, {inputs[1]})'
    equation = sympy.sympify(input)
    solutions = sympy.solve(equation)
    result = []
    for solution in solutions:
        result.append(solution)
    return result

def plot_func(x: np.ndarray, input: str) -> dict:
    '''
    Plot the given function 'input' for given range x.
    Output(s) are added to the values of dictionary 'val'.
    '''
    val = {}
    def func(x):
        return eval(input)
    for i in x:
        val[i] = func(i)
    return val

def calculate_expression(*formulas) -> str:
    '''
    Calculates the result of a given mathematical problem.
    Supported operations:
    Basic: +, -, *, /
    Modulus: % or mod
    Powers: ^
    Square roots: sqrt()
    Factorial: !
    Logarithms: log(,[base]) (default base=e)
    Absolute value: abs()
    Rounding: round(), floor(), ceil()
    Trigonometry: sin(), cos(), tan() (in radians)
    Parentheses: ()
    Constants: pi, e, phi, tau, etc...
    Complex/imaginary numbers: i
    Infinity: inf
    Sum: sum(start, end, f(x)) (start and end inclusive)
    Product: product(start, end, f(x)) (start and end inclusive)
    '''
    
    formula = ''
    for f in formulas:
        formula += f + ' '
    formula = formula.strip()
    if not formula:
        raise ValueError(f'Required argument missing: `expression`.')
    try:
        input = format_input(formula.lower(), 0)

        result = calculate(input)

        output = format_output(result)
        formula = beautify_input(formula)
        return f'{formula} = {output}'
    except Exception as e:
        raise ValueError(f'Invalid mathematical expression:\n\t{e}')

def plot(start: float, end: float, *formulas) -> Tuple[str, io.BytesIO]:
    '''
    Plots a given mathematical function
    Arguments: start, end, f(x)
    Supported operations:
    Basic: +, -, *, /
    Modulus: % or mod
    Powers: ^
    Square roots: sqrt()
    Logarithms: log() (base=e)
    Absolute value: abs()
    Rounding: round(), floor(), ceil()
    Trigonometry: sin(), cos(), tan() (in radians)
    Parentheses: ()
    Constants: pi, e, phi, tau, etc...
    Example: graph -10 10 x
    '''
    
    formula = ''
    for f in formulas:
        formula += f + ' '
    formula = formula.strip()
    if not is_float(start) or not is_float(end):
        raise ValueError(f'Invalid argument(s): `start/end`.')
    elif start >= end:
        raise ValueError(f'Invalid arguments: `start`, `end`.')
    if not formula:
        raise ValueError(f'Required argument missing: `formula`.')
    try:
        input = format_input(formula.lower(), 1)

        x = np.linspace(start, end, 250)

        plt.style.use('dark_background')
        fig, ax = plt.subplots()

        val = plot_func(x, input)
        
        y = [v for v in val.values()]

        potential_error = y[len(y)-1]
        if isinstance(potential_error, Exception):
            raise potential_error

        plt.plot(x, y, color='#47a0ff')

        ax.yaxis.grid()
        ax.xaxis.grid()
        plt.xlim(start, end)
        plt.savefig('images/math_graph.png', transparent=True)
        plt.close(fig)

        with open('images/math_graph.png', 'rb') as f:
            file = io.BytesIO(f.read())

        formula = beautify_input(formula)
        return (f'𝘧(𝓍) = {formula}', file)
    except Exception as e:
        raise ValueError(f'Invalid mathematical expression: \n```{e}```')

def solve(*formulas) -> str:
    '''
    Solves a given equation for x.
    Supported operations:
    Basic: +, -, *, /
    Powers: ^
    Square roots: sqrt()
    Logarithms: log() (base e)
    Parentheses: ()
    Constants: pi, e, phi, tau, etc...
    Trigonometry: sin(), cos(), tan() (in radians)
    Complex/imaginary numbers: i
    '''
    
    formula = ''
    for f in formulas:
        formula += f + ' '
    formula = formula.strip()
    if not formula:
        raise ValueError(f'Required argument missing: `formula`.')
    try:
        input = format_input(formula.lower(), 2)

        solutions = solve_for_x(input)

        if len(solutions) == 0:
            output = 'False'
        elif len(solutions) == 1:
            output = f'𝓍 = {solutions[0]}'.lower()
        else:
            output = ''
            for i, sol in enumerate(solutions):
                if not i == 0:
                    output += ' ∨ '
                output += f'𝓍 = {sol}'.lower()

        output = output.replace('pi', 'π')
        output = output.replace('i', '𝑖')
        output = output.replace('exp', 'EXP')
        output = output.replace('x', '𝓍')
        output = output.replace('EXP', 'exp')
        output = output.replace('sqrt', '√')
        formula = beautify_input(formula)
        
        return f'{output}'
    except Exception as e:
        raise ValueError(f'Invalid mathematical expression:\n```{e}```')

def convert(value='', unit='', new_unit='') -> str:
    '''
    Converts given unit to new unit.
    Default value = 1
    '''

    if not value or not unit:
        raise ValueError(f'Required argument(s) missing: `value/unit`.')
    elif not new_unit:
        new_unit = unit
        unit = value
        value = 1

    unit = unit.lower().replace(' ', '')
    new_unit = new_unit.lower().replace(' ', '')

    if not is_float(value):
        raise ValueError(f'Invalid argument: `{value}`.')
    elif is_int(value):
        value = int(value)
    else:
        value = float(value)

    if value > sys.maxsize:
        raise ValueError(f'Invalid argument: `{value}`. This value is too high.')

    if not unit in units:
        if not any(unit in alias for alias in unit_aliases):
            raise ValueError(f'Invalid argument: `{unit}`.')
        else:
            unit = get_alias(unit)


    conversion_units = units[unit]
    if new_unit in conversion_units:
        factor = conversion_units[new_unit]
    else:
        if not any(new_unit in alias for alias in unit_aliases):
            raise ValueError(f'Invalid argument: `{new_unit}`.')
        else:
            new_unit = get_alias(new_unit)
            if new_unit in conversion_units:
                factor = conversion_units[new_unit]
            else:
                if not any(unit in alias for alias in unit_aliases):
                    raise ValueError(f'Incompatible units: `{unit}`, `{new_unit}`.')
                else:
                    unit = get_alias(unit)
                    conversion_units = units[unit]
                    if new_unit in conversion_units:
                        factor = conversion_units[new_unit]
                    else:
                        new_unit = get_alias(new_unit)
                        if new_unit in conversion_units:
                            factor = conversion_units[new_unit]
                        else:
                            raise ValueError(f'Incompatible units: `{unit}`, `{new_unit}`.')

    if isinstance(factor, int) or isinstance(factor, float):
        new_value = value * factor
    else:
        new_value = eval(f'{value}{factor}')
    new_value = str(new_value).replace('e', ' • 10^').replace('+', '')

    return f'{value} {unit} = {new_value} {new_unit}'

def get_units() -> str:
    '''
    List of units supported by convert command.
    '''

    txt = ''
    prev = [None]
    for unit in units:
        if prev:
            if unit in prev:
                txt += ', '
            else:
                txt += '\n'
        txt += unit
        prev = units[unit]

    return f'{txt}'

def scientific(*number) -> str:
    '''
    Convert a number literal to scientific notation and vice versa.
    '''

    if not number:
        raise ValueError('No input. Please give a number literal as argument.')
    
    input = ' '.join(number)

    input = input.replace(' ', '').replace(',', '')
    input = input.replace('*10^', 'e')
    input = input.replace('x10^', 'e')
    input = input.replace('•10^', 'e')

    if 'e' in input: # convert from scientific notation to number
        num = input[:input.index('e')]
        exp = input[input.index('e')+1:]
        if not is_float(num) or not is_float(exp):
            raise ValueError(f'Invalid input: `{input}`. Please give a number literal as argument.')
        num, exp = float(num), float(exp)
        try:
            result = num * (10**exp)
        except Exception as e:
            raise ValueError(f'Invalid input: `{input}`. Error: {e}')
        output = float_to_formatted_string(result)
    else: # convert from number literal to scientific notation
        if not is_float(input):
            raise ValueError(f'Invalid input: `{input}`. Please give a number literal as argument.')

        # Calculate result
        num = input if '.' in input else input + '.0'
        exp = 0
        while num.index('.') > 1:
            decimal_index = num.index('.')
            num = num[:decimal_index-1] + '.' + num[decimal_index-1:].replace('.', '')
            exp += 1

        # Remove non-significant digits and trailing decimal point
        significant_digits = max([i for i, d in enumerate([n for n in num if re.match('[\d]', n)]) if d != '0']) + 1
        digits = len([i for i in num if re.match('[\d]', i)])
        while digits > significant_digits:
            num = num[:len(num)-1]
            digits = len([i for i in num if re.match('[\d]', i)])
        if num.endswith('.'):
            num = num[:len(num)-1]
        
        output = f'{num} • 10^{exp}'
    
    if len(output) < 1998:
        return f'{output}'
    else:
        raise ValueError(f'Error: output exceeds character limit.')