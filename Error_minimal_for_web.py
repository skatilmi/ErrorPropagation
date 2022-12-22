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
    def __init__(self, latex_code, python_code=False):
        self.latex_code_mathpix = mathpix(latex_code)
        self.latex_code_raw = latex_code
        self.python_code = python_code
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
        raw_code = raw_code.replace('exp', 'np.exp')
        raw_code = raw_code.replace('sqrt', 'np.sqrt')

        raw_code = raw_code.replace('sin', 'np.sin')
        raw_code = raw_code.replace('cos', 'np.cos')
        raw_code = raw_code.replace('tan', 'np.tan')

        raw_code = raw_code.replace('sinc', 'np.sinc')

        raw_code = raw_code.replace('atan', 'np.arctan')
        raw_code = raw_code.replace('asin', 'np.arcsin')
        raw_code = raw_code.replace('acos', 'np.arccos')

        raw_code = raw_code.replace('tanh', 'np.tanh')
        raw_code = raw_code.replace('sinh', 'np.sinh')
        raw_code = raw_code.replace('cosh', 'np.cosh')

        raw_code = raw_code.replace('log', 'np.log')

        raw_code = raw_code.replace('abs', 'np.abs')
        raw_code = raw_code.replace('max', 'np.max')
        raw_code = raw_code.replace('min', 'np.min')
        raw_code = raw_code.replace('sign', 'np.sign')

        self.raw_code = raw_code
        self.t = sp.lambdify(x_, f_)


class Error_propagation:
    def __init__(self, func, relative_error=False, function_name='f'):
        self.function_name = function_name
        self.func = func
        self.F = sp.Symbol(self.function_name)
        self.F_err = sp.Symbol('\Delta '+self.function_name)
        self.f = sp.parse_expr(self.func)
        self._f = sp.latex(self.f)
        self.substitution = False
        self.relative_error = relative_error
        self.fields: List[Field] = []

        self.params = {"f": mathpix(self.function_name+' = '+self._f), "f_raw": self.function_name+' = '+self._f,
                       "f_raw_svg": mathpix(self.function_name+' = '+self._f).replace('\\', '\\\\')}

    def get_free_symbols_as_latex(self):
        a = ', '.join(list(map(sp.latex, self.f.free_symbols)))
        return mathpix(a)

    def k(self, symbol: str, f_: sp.Expr):
        s = sp.Symbol(symbol)
        delta = sp.Symbol('\\Delta '+symbol)
        if symbol in greek_letters:
            delta = sp.Symbol('\\Delta '+'\\'+symbol)
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

    def collect_relative_error__(self, ppp):
        arg = sp.simplify(ppp/self.f**2)
        f = 0
        for summand in arg.args:
            for symbol in self.f.free_symbols:
                if symbol in summand.free_symbols and sp.Symbol('\\Delta '+str(symbol)) in summand.free_symbols:
                    f += summand*(sp.Symbol('\\Delta '+str(symbol)+'_\\%')
                                  ** 2) * symbol**2/sp.Symbol('\\Delta '+str(symbol))**2
        return self.F*sp.simplify(sp.sqrt(f))

    def collect_relative_error(self, ppp):
        arg = sp.simplify(ppp/self.f**2)

        f = arg
        for symbol in f.free_symbols:
            f = f.subs(sp.Symbol('\\Delta '+str(symbol)) /
                       symbol, sp.Symbol('\\Delta '+str(symbol)+'_\\%'))

        f = arg
        for symbol in f.free_symbols:
            f = f.subs(sp.Symbol('\\Delta '+str(symbol)), symbol *
                       sp.Symbol('\\Delta '+str(symbol)+'_rel'))

        return self.F*sp.simplify(sp.sqrt(f))

    def do_error(self):
        self.error = sum(self.k(i, self.f)
                         for i in list(map(str, self.f.free_symbols)))
        self._err1 = sp.latex(sp.sqrt(self.error))

        if self.relative_error:
            self.err_simple = self.F*sp.simplify(sp.sqrt(self.error/self.f**2))
            err_rel = self.collect_relative_error(self.error)
            self._err1_simple = sp.latex(err_rel)
            return

        self.error_simple = self.F*sp.simplify(sp.sqrt(self.error/self.f**2))
        self._err1_simple = sp.latex(self.error_simple)

    def get_errors(self):
        errors = [self._err1, self._err1_simple]
        if self.substitution:
            errors.extend([self._err2, self._err2_simple])
        return errors

    def set_html_codes(self, zeros=[]):
        self.fields += [
            Field(self.function_name+' = '+self._f,
                  self.gpr(self.f, nosqrt=True)),
            Field(self.wrap_error(self._err1), self.gpr(self.error)),
            Field(self.wrap_error(self._err1_simple),
                  self.gpr(self.error_simple, delta=True)),
        ]

        if not self.substitution:
            return

        self.fields += [
            Field(self.wrap_error(self._err2, zeros), self.gpr(self.error_0))
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

    def get_python_represenaion(self, expression, nosqrt=False, delta=False):
        if not nosqrt:
            expression = sp.sqrt(expression)
        p = str(expression).replace('\\', '').replace('Delta ', 'Delta_')

        c = Code(sp.Symbol('xxxxxxxxxxxxxxxxxxxxxx'), p).raw_code[1:-1]
        free_symbols = ', '.join(list(map(str,
                                          list(expression.free_symbols)
                                          )
                                      )
                                 ).replace('\\', '').replace('Delta ', 'Delta_')

        c = f'def {self.function_name}(*, {free_symbols}):\n  return {c}'
        return c


def mathpix(expression):
    return '\['+expression+'\]'
