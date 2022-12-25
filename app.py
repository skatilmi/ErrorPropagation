from lxml import html
import requests
from markupsafe import escape
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from Error_minimal_for_web import greek_letters, mathpix, Field, Demo, inline_rep, Ableiter, Renderer, Error_Propagation
app = Flask(__name__)


params_home = {"greek_letters": mathpix(
    ', '.join(['\\'+i for i in greek_letters]))}


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


def get_all_latex_from_wiki(website_link):
    r = requests.get(website_link)
    tags = ['//img[@class="mwe-math-fallback-image-display"]', '//img[@class="mwe-math-fallback-image-inline"]']
    images = []
    for tag in tags:
        images.extend(html.fromstring(r.content).xpath(tag))
    images = list(set(images))

    images = [i.attrib['alt'] for i in images]
    return images


@app.route('/wikiscraper', methods=['POST', 'GET'])
def page_wikiscraperr():
    if request.method == 'GET':
        return render_template('wikiscraper.html')
    else:
        fields = [Field(latex_code=i) for i in get_all_latex_from_wiki(request.form['wikilink'])]
        return render_template('wikiscraper.html', fields=fields)


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
    field = renderer.field
    return render_template('renderer.html', field=field)


class pp:
    def __init__(self, form):
        self.form = form


@ app.route('/error', methods=['POST', 'GET'])
def page_error():
    if request.method == 'POST':
        print('post')

    if request.method == 'GET':
        print('get')
        if request.args.get('from_database') == 'True':
            r = pp({'expression': request.args.get('expression'), 'fname': request.args.get('fname'), 'description': request.args.get('description')})
            return render_template('error.html', request=r)
        else:
            return render_template('error.html', **params_home)

    e: Error_Propagation = Error_Propagation(request.form)
    return render_template('comm.html',  fields=e.fields)


@ app.route('/database/<entry_id>', methods=['POST', 'GET'])
def database_error_id(entry_id):
    fname, description, expression = get_database_entry(int(entry_id))
    return redirect(url_for('page_error', expression=expression, fname=fname, description=description, from_database=True))


def get_database_entry(entry):
    with open('database.csv', 'r') as f:
        f.readline()
        data = f.readlines()
    data = data[entry-1]
    data = data.strip()
    data = data.split(';')
    return data


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
    app.run(host='0.0.0.0')
    # app.run(host='0.0.0.0', debug=True)
