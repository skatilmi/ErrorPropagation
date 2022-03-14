import sympy as sp
import numpy as np
from IPython.display import display
from sympy.utilities.lambdify import lambdastr
import inspect
import matplotlib.pyplot as plt
from typing import List


class Code:
    def __init__(self, x_, f_):
        raw_code = inspect.getsource(
            sp.lambdify(x_, f_)).split('return')[-1]
        raw_code = raw_code.replace('exp', 'np.exp')
        raw_code = raw_code.replace('sqrt', 'np.sqrt')

        raw_code = raw_code.replace('sin', 'np.sin')
        raw_code = raw_code.replace('cos', 'np.cos')
        raw_code = raw_code.replace('tan', 'np.tan')

        raw_code = raw_code.replace('atan', 'np.arctan')
        raw_code = raw_code.replace('asin', 'np.arcsin')
        raw_code = raw_code.replace('acos', 'np.arccos')

        raw_code = raw_code.replace('tanh', 'np.tanh')
        raw_code = raw_code.replace('sinh', 'np.sinh')
        raw_code = raw_code.replace('cosh', 'np.cosh')
        self.raw_code = raw_code
        self.t = sp.lambdify(x_, f_)


class Error_propagation:
    def __init__(self, func):
        self.func = func
        self.F = sp.Symbol('f')
        self.F_err = sp.Symbol('\Delta f')

        self.f = sp.parse_expr(self.func)
        print('input expression:')

        print('#'*20)
        print('INPUT')
        self._f = sp.latex(self.f)

        display(self.f)
        print('python rep:')
        display(Code(sp.Symbol('x'), self.f).raw_code.strip())
        print('#'*20)
        print('OUTPUT')
        self.substitution = False
        self.do_error()

    def k(self, symbol: str, f_: sp.Expr):
        a = sp.diff(f_, sp.Symbol(symbol))*sp.Symbol('\\Delta '+symbol)
        a = a**2
        return a

    def set_error_to_zero(self, params: List[str]):
        print('-'*20)
        p = self.error
        for param in params:
            var = '\\Delta '+param
            p = p.subs(var, 0)

        print('substituted params\' error with 0: '+', '.join(params))

        self.error_0 = p
        display(sp.sqrt(self.error_0))
        self._err2 = sp.latex(sp.sqrt(self.error_0))

        err_simple = self.F*sp.simplify(sp.sqrt(self.error_0/self.f**2))
        display(err_simple)
        self._err2_simple = sp.latex(err_simple)

        self.substitution = True

    def do_error(self):

        self.error = sum(self.k(i, self.f)
                         for i in list(map(str, self.f.free_symbols)))
        display(sp.sqrt(self.error))
        self._err1 = sp.latex(sp.sqrt(self.error))

        err_simple = self.F*sp.simplify(sp.sqrt(self.error/self.f**2))
        display(err_simple)
        self._err1_simple = sp.latex(err_simple)

    def print_errors(self):
        print(self._err1)
        print(self._err1_simple)
        if self.substitution:
            print(self._err2)
            print(self._err2_simple)

    def get_errors(self):
        errors = [self._err1, self._err1_simple]
        if self.substitution:
            errors.extend([self._err2, self._err2_simple])
        return errors
