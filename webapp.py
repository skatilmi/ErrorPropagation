from flask import Flask, request, render_template

app = Flask(__name__)


@app.route("/")
def input():
    return render_template("input.html")


@app.route('/', methods=['POST'])
def my_form_post():
    import propagation_for_web as ep
    text = request.form['text']
    select = request.form.get('colors')
    represents = ep.main(text)
    s = ''
    for i, j in represents:
        s += i+' <br> '+j+'<br><br>'
    return s


app.run()
