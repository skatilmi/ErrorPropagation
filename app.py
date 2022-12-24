from markupsafe import escape
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from Error_minimal_for_web import greek_letters, mathpix, Field, Demo, inline_rep, Ableiter, Renderer, Error_Propagation
app = Flask(__name__)


demo_fields = [
    Demo('y = a x + b ', 'a*x+b', 'linear', fname='y'),

    Demo(r'V = \frac{4\pi}{3}r^3', '4*pi/3*r**3', 'sphere', fname='V'),

    Demo('I = \\frac{A - B}{C - D} ', '(A-B)/(C-D)',
         'intensiy_of_refelected_light_beam', fname='I'),
    Demo(r'\frac{2 a^{2}}{\cos^{n}{\left(\frac{x}{b} -\varphi \right)}} ',
         '2*a*a/cos(x/b-varphi)**n', 'dunno'),
    Demo(inline_rep('a*b*x'), 'a*b*x', 'x'),
    Demo('q^2 = 4 E_1 E_2 sin^2(\\theta/2)',
         '4*E_1*E_2*sin(theta/2)**2',
         'inspiration', fname='q**2'),
    Demo(latex_code='\\frac{d^2 \\sigma}{dxdq^2} = \\frac{2 \\pi N_{\gamma} \\alpha^{2} \\left(- y^{2} \\operatorname{F_{L}}{\\left(x,q^{2} \\right)} + \\left(\\left(1 - y\\right)^{2} + 1\\right) \\operatorname{F_{2}}{\\left(x,q^{2} \\right)}\\right)}{q^{4} x} ',
         # python_code='N_gamma*(2*pi*alpha**2)/(x*q**4)*((1+(1-y)**2)*F_2(x,q**2)-y**2*F_L(x,q**2))',
         python_code='N_gamma*(2*pi*alpha**2)/(x*q**4)*((1+(1-y)**2)*F_2(x,q**2)-y**2*F_L(x,q**2))',
         demo_name='hadronic_photon_structure',
         # fname='\\frac{d^2 \\sigma}{dxdq^2}'
         ),
]
__demo_fields = {
    'dunno': Demo(r'\frac{2 a^{2}}{\cos^{n}{\left(\frac{x}{b} -\varphi \right)}} ', '2*a*a/cos(x/b-varphi)**n', 'dunno'),
    'x': Demo(inline_rep('a*b*x'), 'a*b*x', 'x'),
    'q2': Demo('q^2 = 4 E_1 E_2 sin^2(\\theta/2)', '4*E_1*E_2*sin(theta/2)**2', 'inspiration', fname='q**2'),

    'hadronic_photon_structure': Demo(latex_code='\\frac{d^2 \\sigma}{dxdq^2} = \\frac{2 \\pi N_{\gamma} \\alpha^{2} \\left(- y^{2} \\operatorname{F_{L}}{\\left(x,q^{2} \\right)} + \\left(\\left(1 - y\\right)^{2} + 1\\right) \\operatorname{F_{2}}{\\left(x,q^{2} \\right)}\\right)}{q^{4} x} ',
                                      # python_code='N_gamma*(2*pi*alpha**2)/(x*q**4)*((1+(1-y)**2)*F_2(x,q**2)-y**2*F_L(x,q**2))',
                                      python_code='N_gamma*(2*pi*alpha**2)/(x*q**4)*((1+(1-y)**2)*F_2(x,q**2)-y**2*F_L(x,q**2))',
                                      demo_name='hadronic_photon_structure',
                                      # fname='\\frac{d^2 \\sigma}{dxdq^2}'
                                      ),
}


params_home = {"greek_letters": mathpix(
    ', '.join(['\\'+i for i in greek_letters]))}

params_demos = {"fields": demo_fields}


@app.route('/')
def page_index():
    return render_template('index.html')


@app.route('/ableiter', methods=['POST', 'GET'])
def page_ableiter():
    if request.method == 'GET':
        return render_template('ableiter.html')
    ableiter = Ableiter(request.form['expression'])
    fields = [Field(False, ableiter.params['input_function'])]
    for latex, python in zip(ableiter.params['free_symbols_deriv_raw'], ableiter.params['derivatives_python_as_function']):
        fields.append(Field(latex_code=latex, python_code=python))
    return render_template('ableiter.html', fields=fields)


@app.route('/renderer', methods=['POST', 'GET'])
def page_renderer():
    if request.method == 'GET':
        return render_template('renderer.html')
    expression_python = request.form['expression_python'].replace(
        'np.', '').replace('math.', '').replace('sp.', '')
    expression_latex = request.form['expression_latex']
    renderer = Renderer(expression_python=expression_python,
                        expression_latex=expression_latex)
    field = Field(expression_latex, expression_python)
    field.latex_code_raw = renderer.latex
    field.latex_code_mathpix = renderer.params['rendered']

    return render_template('renderer.html', field=field)


@app.route('/demos')
def page_demos():
    return render_template('demos.html', **params_demos)


@ app.route('/demos/<demo_name>')
def page_demos_list(demo_name):
    _demo = demo_fields[demo_name] if demo_name in demo_fields else None

    for demo in demo_fields:
        if demo.demo_name == demo_name:
            form = {'zeros': '', 'relative_error': 'off', 'expression': demo.python_code, 'fname': demo.fname}
            e = Error_Propagation(form)
            return render_template('comm.html', fields=e.fields)
    return render_template('comm.html', fields=demo_fields)


@ app.route('/error', methods=['POST', 'GET'])
def page_error():
    if request.method == 'GET':
        return render_template('error.html', **params_home)
    e: Error_Propagation = Error_Propagation(request.form)
    return render_template('comm.html',  fields=e.fields)


@ app.route('/database/<entry_id>', methods=['POST', 'GET'])
def database_error_id(entry_id):
    if request.method == 'GET':
        return render_template('database.html')
    fields = [Field('a b')]
    return render_template('database.html', fields=fields)


@ app.route('/database')
def database_error():
    with open('database.csv', 'r') as f:
        f.readline()
        data = f.readlines()
        data = [i.strip() for i in data]
        data = [i.split(';') for i in data]
    fields = []
    for i in data:
        fname = i[0]
        description = i[1]
        python_code = i[2]
        fields.append(Field(python_code=python_code, fname=fname, description=description))
    return render_template('database.html', fields=fields)


def get_relative_error_checkbox():
    try:
        relative_error = request.form['relative_error'] == 'on'
    except:
        relative_error = False
    return relative_error


@app.errorhandler(500)
@app.errorhandler(404)
def internal_error(error):
    return render_template('catch_error_page.html'), 500


if __name__ == '__main__':
    # app.run(host='0.0.0.0')
    app.run(host='0.0.0.0', debug=True)
