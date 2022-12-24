import dataclasses
import math
import sympy as sp
import numpy as np

from sympy.utilities.lambdify import lambdastr
import inspect
from typing import List

from dataclasses import dataclass

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


def inline_rep(expression):

    return sp.latex(sp.parse_expr(expression))


class Field:
    def __init__(self, latex_code=False, python_code=False):
        if latex_code is False:
            latex_code = sp.latex(sp.parse_expr(str(python_code)))

        self.latex_code_mathpix = mathpix(latex_code)
        self.latex_code_raw = latex_code

        self.python_code = python_code
        if '=' in str(python_code):
            print(python_code)
            #self.python_code = python_code.split('=')[-1]

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
            'exp': 'np.exp', 'sqrt': 'np.sqrt',
            'sin': 'np.sin', 'cos': 'np.cos', 'tan': 'np.tan',
            'sinc': 'np.sinc',
            'atan': 'np.arctan', 'asin': 'np.arcsin', 'acos': 'np.arccos',
            'tanh': 'np.tanh', 'sinh': 'np.sinh', 'cosh': 'np.cosh',
            'log': 'np.log',
            'abs': 'np.abs', 'max': 'np.max', 'min': 'np.min',


        }
        for k, v in _replace.items():
            x = x.replace(k, v)
        return x


class Expression:
    def __init__(self, sympy_expression):
        self.sympy = sympy_expression
        self.latex = sp.latex(sp.parse_expr(str(sympy_expression)))


class Error_propagation:
    def __init__(self, func, relative_error=False, function_name='f'):
        self.function_name = function_name
        self.func = func
        self.F = sp.Symbol(self.function_name)
        self.F_err = sp.Symbol('\Delta '+self.function_name)
        self.f: sp.Expr = sp.parse_expr(self.func)
        self.f_free_symbols = self.f.free_symbols
        self._f = sp.latex(self.f)
        self.substitution = False
        self.relative_error = relative_error
        self.fields: List[Field] = []

        self.params: dict = {}
        self.params['f'] = mathpix(f'{self.function_name} = {self._f}')
        self.params['f_raw'] = f'{self.function_name} = {self._f}'
        self.params['f_raw_svg'] = mathpix(
            f'{self.function_name} = {self._f}').replace('\\', '\\\\')

    def get_free_symbols_as_latex(self):
        a = ', '.join(list(map(sp.latex, self.f.free_symbols)))
        return mathpix(a)

    def derivate_and_square(self, symbol: str, f_: sp.Expr):
        s = sp.Symbol(symbol)
        delta = sp.Symbol(
            '\\Delta '+symbol) if symbol not in greek_letters else sp.Symbol('\\Delta '+'\\'+symbol)
        a = sp.diff(f_, s) * delta
        a = a**2
        return a

    def set_error_to_zero(self, params: List[str]):
        self.substitution = True
        p = self.error
        for param in params:
            var = '\\Delta '+param
            p = p.subs(var, 0)

        self.error_0 = p
        self._err2 = sp.latex(sp.sqrt(self.error_0))

        if self.relative_error:
            self.err_rel = self.collect_relative_error(self.error_0)
            self._err2_simple = sp.latex(self.err_rel)
            return
        self.err_simple_0 = self.F*sp.simplify(sp.sqrt(self.error_0/self.f**2))
        self._err2_simple = sp.latex(self.err_simple_0)

    def collect_relative_error(self, ppp):
        arg = sp.simplify(ppp/self.f**2)

        f = arg
        for symbol in f.free_symbols:
            f = f.subs(sp.Symbol('\\Delta '+str(symbol)), symbol *
                       sp.Symbol('\\Delta '+str(symbol)+'_rel'))

        return self.F*sp.simplify(sp.sqrt(f))

    def do_error(self):
        self.error = sum(self.derivate_and_square(i, self.f)
                         for i in list(map(str, self.f_free_symbols)))
        self._err1 = sp.latex(sp.sqrt(self.error))

        if self.relative_error:
            self.err_simple = self.F*sp.simplify(sp.sqrt(self.error/self.f**2))
            err_rel = self.collect_relative_error(self.error)
            self._err1_simple = sp.latex(err_rel)
            return

        self.error_simple = self.F*sp.simplify(sp.sqrt(self.error/self.f**2))
        self._err1_simple = sp.latex(self.error_simple)

        # normal error
        #self.ex_error_1 = Expression(sum(self.derivate_and_square(i, self.f) for i in list(map(str, self.f_free_symbols))))
        # error with relative to f
        #self.ex_error_2 = Expression(self.F*sp.simplify(sp.sqrt(self.error_1.sympy/self.f**2)))
        # error with relative paramter errors

    def set_fields(self, zeros=[]):
        self.fields += [
            Field(self.function_name+' = '+self._f,
                  self.gpr(self.f, nosqrt=True)),
            Field(self.wrap_error(self._err1),
                  self.gpr(self.error, delta=True)),
            Field(self.wrap_error(self._err1_simple),
                  self.gpr(self.error_simple, delta=True, relative_to_f=True)),
        ]

        if not self.substitution:
            return

        self.fields += [
            Field(self.wrap_error(self._err2, zeros),
                  self.gpr(self.error_0, delta=True)),
        ]

    def wrap_error(self, expression, zeros=[]):
        new = []
        for i in zeros:
            if i in greek_letters:
                new.append('\\'+i)
            else:
                new.append(i)
        zeros = new

        tail = '\Big|_{' + ', '.join(['\Delta '+i for i in zeros])+'=0}'
        if not zeros:
            tail = ''
        return '\Delta '+self.function_name+tail+' = '+expression

    def gpr(self, *args, **kwargs):
        return self.get_python_represenaion(*args, **kwargs)

    def get_python_represenaion(self, expression, nosqrt=False, delta=False, relative_to_f=False):
        delta = 'Delta_' if delta else ''
        function_name = self.function_name
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


def mathpix(expression):
    return '\['+expression+'\]'


def warp_in_function_syntax(function_name: str, keys: List[str], return_value: str) -> str:
    return f'def {function_name}({", ".join(keys)}):\n  return {return_value}'


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


class Renderer:
    def __init__(self, expression_latex='', expression_python="") -> None:
        self.expression_latex = expression_latex
        self.expression_python = expression_python
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
