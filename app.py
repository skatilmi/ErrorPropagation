from markupsafe import escape
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from Error_minimal_for_web import Error_propagation, greek_letters, mathpix, Field, Demo, inline_rep, Ableiter, Renderer
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
         '4*E_1*E_2*sin(theta/2)**2', 'inspiration', fname='q^2'),
    Demo('\\frac{d^2 \\sigma}{dxdq^2} = \\frac{2 \\pi N_{\gamma} \\alpha^{2} \\left(- y^{2} \\operatorname{F_{L}}{\\left(x,q^{2} \\right)} + \\left(\\left(1 - y\\right)^{2} + 1\\right) \\operatorname{F_{2}}{\\left(x,q^{2} \\right)}\\right)}{q^{4} x} ',
         'N_gamma*(2*pi*alpha**2)/(x*q**4)*((1+(1-y)**2)*F_2(x,q**2)-y**2*F_L(x,q**2))', 'hadronic_photon_structure', fname='\\frac{d^2 \\sigma}{dxdq^2}'),





]


class Coockie:
    def __init__(self) -> None:
        self.fname = 'f'
        self.expression = 'a*x**2'
        self.zeros = 'a'


params_home = {"coockie": Coockie(), "greek_letters": mathpix(
    ', '.join(['\\'+i for i in greek_letters]))}

params_demos = {"fields": demo_fields}


@app.route('/')
def page_index():
    return render_template('index.html')


@app.route('/demos')
def page_demos():
    return render_template('demos.html', **params_demos)


@app.route('/ableiter')
def page_ableiter():
    return render_template('ableiter.html')


@app.route('/ableiter', methods=['POST'])
def page_ableiter_post():
    ableiter = Ableiter(request.form['expression'])
    return render_template('ableiter.html', ableiter=ableiter)


@app.route('/renderer')
def page_renderer():
    return render_template('renderer.html')


@app.route('/renderer', methods=['POST'])
def page_renderer_post():
    expression_python = request.form['expression_python']
    expression_latex = request.form['expression_latex']
    renderer = Renderer(expression_python=expression_python,
                        expression_latex=expression_latex)
    return render_template('renderer.html', renderer=renderer)


@ app.route('/demos/<demo_name>')
def page_demos_list(demo_name):
    for demo in demo_fields:
        print(demo.demo_name)
        if demo.demo_name == demo_name:
            E = Error_propagation(
                demo.python_code, False, demo.fname)
            E.do_error()
            zeros = []
            E.set_error_to_zero(zeros)
            a = E.get_errors()
            E.set_html_codes(zeros)
            return render_template('comm.html', coockie=Coockie(), fields=E.fields)
    return render_template('comm.html', coockie=Coockie(), fields=demo_fields)


@ app.route('/error')
def page_home():
    return render_template('error.html', **params_home)


@ app.route('/error', methods=['POST'])
def page_home_post():
    E = Error_propagation(
        request.form['expression'], get_relative_error_checkbox(), request.form['fname'])
    E.do_error()
    zeros = []
    if request.form['zeros'] != '':
        zeros = list(request.form['zeros'].split(','))
        E.set_error_to_zero(zeros)
    a = E.get_errors()
    E.set_html_codes(zeros)
    return render_template('comm.html', coockie=Coockie(), fields=E.fields)


@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    return f'User {username}'


def get_relative_error_checkbox():
    try:
        relative_error = request.form['relative_error'] == 'on'
    except:
        relative_error = False
    return relative_error


if __name__ == '__main__':
    # app.run(host='192.168.178.125', port=5000)
    app.run(host='0.0.0.0', debug=True)
