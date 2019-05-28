from flask import Flask, render_template
import sass
import stubs

app = Flask('FitzroyFrontend', static_url_path='')
sass.compile(dirname=("static/assets/scss", 'static/css'))

@app.route('/')
def index():
    return render_template('welcome.html')

@app.route('/playground')
def playground():
    return render_template('playground.html')

@app.route('/course')
def course():
	data = {
		'students': stubs.students
	}
	return render_template('course.html', **data)

@app.route('/lessons')
def lessons():
    return render_template('lesson_chart.html')

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=5000)