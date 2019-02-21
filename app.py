from flask import Flask, render_template, request, session, redirect, url_for
import json
import requests
import os

app = Flask(__name__)

r = requests.Session()
cookies = {}
app.secret_key = "abignut"

authLink = 'https://hunter-todo-api.herokuapp.com/auth'

@app.route('/')
def home():
    if session.get('user', None):
        return redirect('/todos')
    else:
        return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user', None):
        return redirect('/todos')
    if request.method == 'POST':
        username = request.form['username']
        data = '{"username":"' + username + '"}'
        response = r.post(
            'https://hunter-todo-api.herokuapp.com/auth', data=data)
        if response.status_code == 200:
            session['user'] = username
            return redirect('/todos')
        else:
            return render_template('login.html', error="incorrect login, Did you register?")
    else:
        return render_template('login.html')

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        content = request.form['content']
        todo_data = {'content': content}
        todo_data = json.dumps(todo_data)
        res = r.post('https://hunter-todo-api.herokuapp.com/todo-item', data=todo_data)
        if res.status_code != 201:
            return render_template('add.html', error="ERROR")
        else:
            return redirect('/todos')
    else:
        return render_template('add.html')


@app.route('/logoff', methods=["GET"])
def logoff():
    if session.get('user', None):
        session.pop('user', None)
    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user', None):
        return redirect('/todos')
    if request.method=="POST":
        user = request.form['name']
        user_data = {'username': user}
        user_data = json.dumps(user_data)
        res = r.post('https://hunter-todo-api.herokuapp.com/user', data=user_data)
        print(res.status_code)
        print(res.content)
        if res.status_code != 201:
            return render_template('register', error="ERROR")
        else:
            return render_template('home.html')
    else:
        return render_template('register.html')


@app.route('/todos', methods=["GET"])
def main():
    if session.get('user', None):
        todos = r.get('https://hunter-todo-api.herokuapp.com/todo-item')
        todos = json.loads(todos.content)
        return render_template('index.html', todos=todos, user=session.get('user'))
    else:
        return redirect('/')

@app.route('/todos/notcomplete/<int:number>', methods=["GET"])
def notcomplete(number):
    r.put('https://hunter-todo-api.herokuapp.com/todo-item/' + str(number), data='{"completed":false}')
    todos =r.get('https://hunter-todo-api.herokuapp.com/todo-item')
    todos = json.loads(todos.content)
    return render_template('index.html', todos=todos)

@app.route('/todos/complete/<int:number>', methods=["GET"])
def complete(number):
    r.put('https://hunter-todo-api.herokuapp.com/todo-item/' + str(number), data='{"completed":true}')
    todos = r.get('https://hunter-todo-api.herokuapp.com/todo-item')
    todos = json.loads(todos.content)
    return render_template('index.html', todos=todos)

@app.route('/todos/delete/<int:number>', methods=["GET"])
def delete(number):
    r.delete('https://hunter-todo-api.herokuapp.com/todo-item/' + str(number))
    todos = r.get('https://hunter-todo-api.herokuapp.com/todo-item')
    todos = json.loads(todos.content)
    return render_template('index.html', todos=todos)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, threaded=True)

