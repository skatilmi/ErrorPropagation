import dataclasses
import math
import sympy as sp
import numpy as np
from sympy.parsing.latex import parse_latex

from sympy.utilities.lambdify import lambdastr
import inspect
from typing import List

from dataclasses import dataclass


from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
transformations = (standard_transformations + (implicit_multiplication_application, ))

greek_letters = ['alpha',  'delta', 'epsilon', 'eta',
                 'theta', 'iota', 'kappa', 'lambda', 'mu',
                 'nu', 'omicron', 'rho', 'sigma', 'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega', 'xi', 'hbar']

greek_letters += ['Gamma', 'Delta', 'Theta', 'Xi',
                  'Pi', 'Sigma', 'Upsilon', 'Phi', 'Psi', 'Omega']

greek_letters += ['varepsilon', 'vartheta', 'varkappa',
                  'varphi', 'varpi', 'varrho', 'varsigma']


DEMOS = {'inspiration': ('4*E_1*E_2*sin(theta/2)**2', 'E_1'),
         'linear': ('a*x+b', ''),
         'quadratic': ('a*x**2+b*x+c', ''),
         'intensiy_of_refelected_light_beam': ('(A-B)/(C-D)', '')

         }


def latex_to_sym(latex_expression):
    return parse_expr(latex_expression, transformations=transformations)


def inline_rep(expression):

    return sp.latex(sp.parse_expr(expression))


def mathpix(expression):
    return '\['+expression+'\]'


def warp_in_function_syntax(function_name: str, keys: List[str], return_value: str) -> str:
    return f'def {function_name}({", ".join(keys)}):\n  return {return_value}'


class Field:
    def __init__(self, latex_code=False, python_code=False, as_function=False, fname='', description=''):
        if latex_code is False and python_code is False:
            return
        if latex_code is False:
            if fname:
                latex_code = latex_gleichung(sp.parse_expr(fname), sp.parse_expr(str(python_code)))
            else:
                latex_code = sp.latex(sp.parse_expr(str(python_code)))

        self.latex_code_mathpix = mathpix(latex_code)
        self.latex_code_raw = latex_code
        self.description = description

        self.python_code = python_code
        if '=' in str(python_code):
            self.python_code = python_code.split('=')[-1]
        self.editable = False


class Demo(Field):
    """inherit from Field and add another parameter in the super function"""

    def __init__(self, latex_code, python_code, demo_name, fname='f'):
        super().__init__(latex_code, python_code)
        self.demo_name = demo_name
        self.editable = True
        self.fname = fname


class Code:
    def __init__(self, x_, f_):
        raw_code = inspect.getsource(
            sp.lambdify(x_, f_)).split('return')[-1]
        replace = {
            'exp': 'np.exp', 'sqrt': 'np.sqrt',
            'sin': 'np.sin', 'cos': 'np.cos', 'tan': 'np.tan',
            'sinc': 'np.sinc',
            'atan': 'np.arctan', 'asin': 'np.arcsin', 'acos': 'np.arccos',
            'tanh': 'np.tanh', 'sinh': 'np.sinh', 'cosh': 'np.cosh',
            'log': 'np.log',
            'abs': 'np.abs', 'max': 'np.max', 'min': 'np.min',


        }
        for k, v in replace.items():
            raw_code = raw_code.replace(k, v)
        self.raw_code = raw_code
        self.t = sp.lambdify(x_, f_)

    @staticmethod
    def replace(x):
        x = str(x)
        _replace = {
            'exp': 'np.exp',
            'sqrt': 'np.sqrt',
            'sin': 'np.sin',
            'cos': 'np.cos',
            'tan': 'np.tan',
            'sinc': 'np.sinc',
            'atan': 'np.arctan',
            'asin': 'np.arcsin',
            'acos': 'np.arccos',
            'tanh': 'np.tanh',
            'sinh': 'np.sinh',
            'cosh': 'np.cosh',
            'log': 'np.log',
            'abs': 'np.abs',
            'max': 'np.max',
            'min': 'np.min',


        }
        for k, v in _replace.items():
            x = x.replace(k, v)
        return x


class Expression:
    def __init__(self, sympy_expression):
        self.sympy = sympy_expression
        self.latex = sp.latex(sp.parse_expr(str(sympy_expression)))


def latex_gleichung(lhs: sp.Expr, rhs: sp.Expr):
    return f"{sp.latex(lhs)} = {sp.latex(rhs)}"


def get_python_representation(expression, function_name, delta=False, relative_to_f=False):
    delta = 'Delta_' if delta else ''
    p = str(expression).replace('\\', '').replace('Delta ', 'Delta_')
    c: str = Code(sp.Symbol('xxx'), p).raw_code[1:-1]

    free_symbols: List[str] = [str(i).replace('\\', '').replace(
        'Delta ', 'Delta_') for i in expression.free_symbols]
    free_symbols = [i if str(
        i) != function_name else f'{function_name}_data' for i in free_symbols]
    free_symbols.sort()

    if relative_to_f:
        idx = c.find(function_name)
        c = f'{c[:idx]}{function_name}_data{c[idx+1:]}'

    return warp_in_function_syntax(
        f'{delta}{function_name}', free_symbols, c)


class Error_Propagation:
    def __init__(self, form) -> None:
        self.form = form
        self.zeros = [] if self.form['zeros'] == '' else [i.strip() for i in self.form['zeros'].split(',')]
        self.relative_error_checkbox = self.form['relative_error'] == 'on'
        self.fields: List[Field] = []
        self.input_expression = self.form['expression']
        self.input_function_sympy = sp.parse_expr(self.input_expression)
        self.free_symbols = self.input_function_sympy.free_symbols
        self.free_symbols = {i for i in self.free_symbols if str(i) not in self.zeros}

        self.input_function_name_sympy = sp.parse_expr(self.form['fname'])
        self.input_function_name = self.form['fname']
        self._deriv_cells = []
        self._deriv_cells_over_f = []
        self._deriv_cells_relative = []

        # self.field_error_zeros: Field = Field()
        self.fields.append(self.feed_field_input_function())
        self.fields.append(self.feed_field_error())
        self.fields.append(self.feed_field_error_relative_f())
        if self.relative_error_checkbox:
            self.fields.append(self.feed_field_error_relative_params())

    def feed_field_input_function(self):
        latex_expression = latex_gleichung(sp.parse_expr(self.input_function_name), sp.parse_expr(self.input_expression))
        return Field(latex_code=latex_expression, python_code=get_python_representation(self.input_function_sympy, self.input_function_name,  delta=False))

    def feed_field_error(self):
        sqrt_sum_squared_errors = sp.sqrt(sum(sp.simplify(i**2) for i in self.deriv_cells))
        latex_expression = latex_gleichung(sp.Symbol(rf'\Delta {self.input_function_name}'), sqrt_sum_squared_errors)
        return Field(latex_code=latex_expression, python_code=get_python_representation(sqrt_sum_squared_errors, self.input_function_name, delta=True))

    def feed_field_error_relative_f(self):
        sqrt_sum_squared_errors = self.input_function_name_sympy * sp.sqrt(sum(sp.simplify(i**2) for i in self.deriv_cells_over_f))
        latex_expression = latex_gleichung(sp.Symbol(rf'\Delta {self.input_function_name}'), sqrt_sum_squared_errors)
        return Field(latex_code=latex_expression, python_code=get_python_representation(sqrt_sum_squared_errors, self.input_function_name, relative_to_f=True, delta=True))

    def feed_field_error_relative_params(self):
        sqrt_sum_squared_errors = self.input_function_name_sympy * sp.sqrt(sum(sp.simplify(i**2) for i in self.deriv_cells_relative))
        latex_expression = latex_gleichung(sp.Symbol(rf'\Delta {self.input_function_name}'), sqrt_sum_squared_errors)
        return Field(latex_code=latex_expression)

    def derivate(self, symbol: str, f_: sp.Expr):
        return sp.diff(f_, sp.Symbol(symbol)) * sp.Symbol(rf'\Delta {symbol}') if symbol not in greek_letters else sp.Symbol(rf'\Delta \{symbol}')

    @property
    def deriv_cells(self):
        if not self._deriv_cells:
            self._deriv_cells = [self.derivate(str(i), self.input_function_sympy) for i in self.free_symbols]
        return self._deriv_cells

    @property
    def deriv_cells_over_f(self):
        if not self._deriv_cells_over_f:
            self._deriv_cells_over_f = [i/self.input_function_sympy for i in self.deriv_cells]
        return self._deriv_cells_over_f

    @property
    def deriv_cells_relative(self):
        if not self._deriv_cells_relative:
            self._deriv_cells_relative = []
            for cell, symbol in zip(self.deriv_cells_over_f, self.free_symbols):
                symbol = symbol if symbol not in greek_letters else rf'\{symbol}'
                to_append = cell.subs(sp.Symbol(rf'\Delta {symbol}'), symbol * sp.Symbol(rf'\Delta {symbol}__\%'))
                self._deriv_cells_relative.append(to_append)
        return self._deriv_cells_relative


class Ableiter:
    def __init__(self, expression: str) -> None:
        function_name = ''
        if '=' in expression:
            function_name, expression = expression.split('=')
        self.f = sp.parse_expr(expression.replace(
            'np.', '').replace('math.', '').replace('sp.', ''))
        self.params = {}
        self.params['f_raw'] = expression
        self.params['input_function'] = self.f
        self.params['free_symbols_deriv_raw'] = []
        self.params['derivatives_python'] = []

        fname = function_name if function_name else 'f'
        for i in self.f.free_symbols:
            to_append: str = str(sp.latex(sp.diff(self.f, i)))
            self.params['derivatives_python'] += [str(sp.diff(self.f, i))]

            to_append = r'\frac{\partial '+fname + \
                r'}{\partial '+sp.latex(i)+'} = ' + to_append
            self.params['free_symbols_deriv_raw'] += [to_append]

        self.params['derivatives_python_as_function'] = [
            Code.replace(i) for i in self.params['derivatives_python']]

# a,b,c,d,e,k,A,R
# 0,1,2,3,4,5,6,7


class Renderer:
    def __init__(self, expression_latex='', expression_python="") -> None:
        self.expression_latex = expression_latex
        self.expression_python = expression_python.replace('np.', '').replace('math.', '').replace('sp.', '')
        self.params = {}
        if expression_latex and not expression_python:
            self.latex = expression_latex
            self.params['rendered'] = mathpix(expression_latex)
        elif expression_python and not expression_latex:
            self.latex = sp.latex(sp.parse_expr(expression_python.replace(
                'np.', '').replace('math.', '').replace('sp.', '')))
            self.params['rendered'] = mathpix(self.latex)
        else:
            self.params['rendered'] = mathpix(expression_latex)

        if expression_latex and expression_python:
            self.field = Field(latex_code=expression_latex, python_code=expression_python)

        else:
            if expression_latex:
                self.field = Field(latex_code=expression_latex, python_code=latex_to_sym(expression_latex))
            elif expression_python:
                self.field = Field(latex_code=sp.latex(sp.parse_expr((expression_python))), python_code=expression_python)
