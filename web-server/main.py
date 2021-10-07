from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# 없는 페이지 ERROR
@app.errorhandler(404)
def page_not_found(error):
	app.logger.error(error)
	return render_template('page_not_found.html'), 404

# 홈화면
@app.route('/')
def home_page():
	return render_template('home.html')

# YAML 업로드
@app.route('/upload')
def upload_page():
	return render_template('upload.html')

# YAML 업로드 처리
@app.route('/fileUpload', methods = ['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		f = request.files['file']
		if(os.path.splitext(f.filename)[1] == ".yaml" or os.path.splitext(f.filename)[1] == ".yml"):
			f.save('./uploads/' + secure_filename(f.filename))
			return render_template('upload_success.html')
		else:
			return render_template('upload_failed.html')
	else:
		return render_template('upload_failed.html')

# YAML 다운로드
@app.route('/downfile')
def down_page():
	files = os.listdir("./uploads")
	return render_template('filedown.html',files=files)

# YAML 다운로드 처리
@app.route('/fileDown', methods = ['GET', 'POST'])
def down_file():
	if request.method == 'POST':
		sw=0
		files = os.listdir("./uploads")
		for x in files:
			if(x==request.form['file']):
				sw=1
				path = "./uploads/" 
				return send_file(path + request.form['file'],
						attachment_filename = request.form['file'],
						as_attachment=True)
	else:
		return render_template('page_not_found.html')

# YAML 삭제
@app.route('/delete', methods = ['GET', 'POST'])
def delete():
	if request.method == 'POST':
		f = request.form['delete']
		print(f)
		os.remove('uploads/{}'.format(f))
	return render_template('delete_success.html')

# YAML 실행
@app.route('/submit', methods = ['GET', 'POST'])
def submit():
	if request.method == 'POST':
		yaml = request.form["yaml"]
		print(yaml)
		os.system('python3 /home/ec2-user/AnNaBaDa_DevSecOps_Boilerplate/pipeline-github/pipeline.py start ./uploads/{}'.format(yaml))
		return render_template('upload_success.html')
	elif request.method == 'POST':
		yml = request.form["yaml"]
		print(yml)
		os.system('python3 /home/ec2-user/AnNaBaDa_DevSecOps_Boilerplate/pipeline-github/pipeline.py start ./uploads/{}'.format(yml))
		return render_template('upload_success.html')
	else:
		return render_template('upload_failed.html')

# 서버 실행
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5500, debug = True)
