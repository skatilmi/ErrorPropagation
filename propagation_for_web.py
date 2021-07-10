import sympy as sp
import inspect


class Errorpropagator:
    def __init__(self, func, name='func'):
        self.name = name
        self.F = sp.Symbol('f')
        self.f = sp.parse_expr(func)
        symbols = list(map(str, list(self.f.free_symbols)))
        self.x__ = sp.Symbol('x')
        self.symbols = []
        self.represents = []
        for symbol in symbols:
            self.symbols.append(
                [sp.Symbol(f'{symbol}'), sp.Symbol('\Delta ' + symbol)])

        df_sim = 0
        df = 0
        for i, di in self.symbols:
            df_sim += sp.simplify((sp.diff(self.f, i)*di/self.f)**2)
            df += (sp.diff(self.f, i)*di)**2

        self.df_sim = self.F*sp.sqrt(df_sim)
        for i in range(3):
            self.df_sim = sp.simplify(self.df_sim)
        self.latex_sim = sp.latex(self.df_sim)

        self.df = sp.sqrt(df)
        self.latex = sp.latex(self.df)

        ### get source code ###
        self.symbols_d = []
        for symbol in symbols:
            self.symbols_d.append(
                [sp.Symbol(f'{symbol}'), sp.Symbol('d' + symbol)])

        df = 0
        for i, di in self.symbols_d:
            df += (sp.diff(self.f, i)*di)**2
        self.df_d = sp.sqrt(df)

    def showme(self):
        class Code:
            def __init__(self, x_, f_):
                raw_code = inspect.getsource(
                    sp.lambdify(x_, f_)).split('return')[-1]
                raw_code = raw_code.replace('exp', 'np.exp')
                raw_code = raw_code.replace('sqrt', 'np.sqrt')
                raw_code = raw_code.replace('log', 'np.log')
                raw_code = raw_code.replace('ln', 'np.log')

                raw_code = raw_code.replace('sin(', 'np.sin(')
                raw_code = raw_code.replace('cos(', 'np.cos(')
                raw_code = raw_code.replace('tan(', 'np.tan(')

                raw_code = raw_code.replace('sinh(', 'np.sinh(')
                raw_code = raw_code.replace('cosh(', 'np.cosh(')
                raw_code = raw_code.replace('tanh(', 'np.tanh(')

                raw_code = raw_code.replace('atan(', 'np.arctan(')
                raw_code = raw_code.replace('asin(', 'np.arcsin(')
                raw_code = raw_code.replace('acos(', 'np.arccos(')

                raw_code = raw_code.replace('atanh(', 'np.arctanh(')
                raw_code = raw_code.replace('asinh(', 'np.arcsinh(')
                raw_code = raw_code.replace('acosh(', 'np.arccosh(')
                self.raw_code = raw_code
                t = sp.lambdify(x_, f_)

        self.free_f = sorted(list(map(str, list(self.f.free_symbols))))
        self.free_f = ['x'] + sorted([i for i in self.free_f if i != 'x'])
        self.free_df = list(map(str, list(self.df.free_symbols)))
        self.free_df = [i.replace('\\Delta ', 'd') for i in self.free_df]
        self.free_df1 = sorted(
            [i for i in self.free_df if 'd' not in i and i != 'x'])
        self.free_df2 = sorted(
            [i for i in self.free_df if 'd' in i and i != 'dx'])
        self.free_df = ['x']+self.free_df1+['dx']+self.free_df2

        self.free_df = ','.join(self.free_df)
        self.free_f = ','.join(self.free_f)

        self.represents.append(['LaTeX input function', sp.latex(self.f)])

        self.represents.append(['LaTeX error function', sp.latex(self.df)])

        self.represents.append(
            ['LaTeX error function simple', sp.latex(self.df_sim)])

        self.represents.append(
            ['LaTeX simple error expanded', sp.latex(self.df_sim.expand())]
        )

        self.represents.append(
            ['python code of input function:',
                'def '+self.name+'('+self.free_f+'):\treturn' + Code(self.x__, self.f).raw_code]

        )
        self.represents.append(
            ['python code of error function:',
                'def '+self.name+'('+self.free_df+'):\treturn' + Code(self.x__, self.df_d).raw_code]

        )


def main(expression, name='func'):
    '''
    this little script gives you the followings things:
        1) python code for the expression you can copy directly into your python script
        2) python code for the propagated error you can copy directly into your python script
        2) on top, you get various latex code for the expressions stated above
    params:
        :expression: enter your expression like you would in python. you can use <variable>_<index>, to index your variables. You can not use ^
        :name: optional, for easier copy and paste, give the function a name
        call Errorpropagator(<expression>).showme()
        translation table:
            np.arcsin -> asin
            np.sinh -> sinh


    '''
    E = Errorpropagator(expression, name)
    E.showme()
    return E.represents


if __name__ == '__main__':
    a = input('Enter Expression here (hit enter for example):\n\t')
    if a == '':
        main('A*exp(-1/(2*s*s)*log(1-Y)**2-s*s/2)', 'func_novosibirsk')
    else:
        main(a)
