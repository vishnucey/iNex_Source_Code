from flask import Flask, redirect, url_for, request
app = Flask(__name__)

@app.route('/success/<name>')
def successa(name):
   return 'welcome %s' % name

@app.route('/success/<name>')
def successab(name):
   return 'welcome ha ha ha %s' % name

@app.route('/login',methods = ['POST', 'GET'])
def login():
   if request.method == 'POST':
      user = request.form['nm']
      return redirect(url_for('successa',name = user))
   else:
      user = request.args.get('nm')
      return redirect(url_for('successab',name = user))

if __name__ == '__main__':
   app.run(debug = True)