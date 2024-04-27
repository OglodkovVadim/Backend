from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
db = SQLAlchemy(app)


class UserTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(120), unique=True, nullable=False)
    status = db.Column(db.Boolean, unique=False, nullable=False)
    user_id = db.Column(db.String(120), unique=True, nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)


class GroupTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    executor = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Boolean, unique=False, nullable=False)
    user_id = db.Column(db.String(120), unique=True, nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)


class UserSubtask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    status = db.Column(db.Boolean, unique=False, nullable=False)
    task_id = db.Column(db.Integer, nullable=False)


class GroupSubtask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    status = db.Column(db.Boolean, unique=False, nullable=False)
    executor = db.Column(db.Integer, nullable=False)
    task_id = db.Column(db.Integer, nullable=False)


@app.route('/user-task/<int:taskId>', methods=['GET', 'PATCH', 'DELETE'])
def user_task(taskId):
    try:
        response = requests.get('http://users.local/users',
                                headers={
                                    'Authorization':
                                    request.headers['Authorization']
                                    })
        if response.status_code == 200:
            match request.method:
                case 'GET':
                    task = UserTask.query.get(taskId)
                    if task:
                        return jsonify({'data': {
                            'id': task.id,
                            'title': task.title,
                            'description': task.description,
                            'status': task.status,
                            'user_id': task.user_id,
                            'deadline':
                            task.deadline.strftime('%Y-%m-%d %H:%M:%S')
                        }}), 200
                    else:
                        return jsonify({'errors': [{
                            'code': 404, 'message': "Not Found"
                            }]}), 404
                case 'PATCH':
                    data = request.json
                    task = UserTask.query.get(taskId)
                    if task:
                        task.title = data['title']
                        task.description = data['description']
                        task.deadline = data['deadline']
                        db.session.commit()
                        return jsonify({
                            'id': task.id,
                            'title': task.title,
                            'description': task.description,
                            'status': task.status,
                            'user_id': task.user_id,
                            'deadline':
                            task.deadline.strftime('%Y-%m-%d %H:%M:%S')
                        }), 200
                    else:
                        return jsonify({'errors': [{
                            'code': 404, 'message': "Not Found"
                            }]}), 404
                case 'DELETE':
                    task = UserTask.query.get(taskId)
                    if task:
                        db.session.delete(task)
                        db.session.commit()
                        return jsonify({'message': 'Task deleted'}), 200
                    else:
                        return jsonify({'errors': [{
                            'code': 404, 'message': "Not Found"
                            }]}), 404

        elif response.status_code == 404:
            return jsonify({'errors': [{
                "code": 401, 'message': "Unauthorized"
                }]}), 401
        else:
            return jsonify({'errors': [{
                "code": 500, 'message': "Server Error"
                }]}), 500

    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'errors': [{
            'code': 500, 'message': "Server Error"
                }]}), 500


@app.route('/user-task', methods=['POST'])
def create_user_task():
    try:
        response = requests.get('http://users.local/users',
                                headers={
                                    'Authorization':
                                    request.headers['Authorization']
                                    })
        if response.status_code == 200:
            match request.method:
                case 'POST':
                    data = request.json()
                    if data:
                        new_task = UserTask(
                            title=data['title'],
                            description=data['description'],
                            status=data['status'],
                            user_id=data['user_id'],
                            deadline=data['deadline']
                        )
                        db.session.add(new_task)
                        db.session.commit()
                        return jsonify({
                            'title': new_task.title,
                            'description': new_task.description,
                            'status': new_task.status,
                            'user_id': new_task.user_id,
                            'deadline':
                            new_task.deadline.strftime('%Y-%m-%d %H:%M:%S')
                        }), 200
                    else:
                        return jsonify({'errors': [{
                            'code': 400, 'message': 'Bad Request'
                            }]}), 400

        elif response.status_code == 404:
            return jsonify({'errors': [{
                "code": 401, 'message': "Unauthorized"
                }]}), 401
        else:
            return jsonify({'errors': [{
                "code": 500, 'message': "Server Error"
                }]}), 500

    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'errors': [{
            'code': 500, 'message': "Server Error"
            }]}), 500


@app.route('/user-task', methods=['POST'])
def get_user_tasks(taskId):
    try:
        response = requests.get('http://users.local/users',
                                headers={
                                    'Authorization':
                                    request.headers['Authorization']
                                    })
        if response.status_code == 200:
            match request.method:
                case 'GET':
                    user_tasks = UserTask.query.filter(
                        UserTask.user_id == int(response.json()['user_id'])
                        )
                    if user_tasks:
                        user_task_data = []
                        for item in user_tasks:
                            user_task_data.append({
                                'id': item.id,
                                'title': item.title,
                                'description': item.description,
                                'status': item.status,
                                'user_id': item.user_id,
                                'deadline':
                                    item.deadline.strftime('%Y-%m-%d %H:%M:%S')
                            })
                        return jsonify(user_task_data)
                    else:
                        return jsonify({'errors': [{
                            'code': 404, 'message': "Not Found"
                            }]}), 404

        elif response.status_code == 404:
            return jsonify({'errors': [{
                "code": 401, 'message': "Unauthorized"
                }]}), 401
        else:
            return jsonify({'errors': [{
                "code": 500, 'message': "Server Error"
                }]}), 500

    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'errors': [{
            'code': 500, 'message': "Server Error"
            }]}), 500


@app.route('/user-task/status/<int:taskId>', methods=['PATCH'])
def update_status_user_task(taskId):
    try:
        response = requests.get('http://users.local/users',
                                headers={
                                    'Authorization':
                                    request.headers['Authorization']
                                    })
        if response.status_code == 200:
            match request.method:
                case 'PATCH':
                    task = UserTask.query.get(taskId)
                    if task:
                        task.status = int(request.json()['status'])
                        return jsonify({
                            'id': task.id,
                            'title': task.title,
                            'description': task.description,
                            'status': task.status,
                            'user_id': task.user_id,
                            'deadline':
                            task.deadline.strftime('%Y-%m-%d %H:%M:%S')
                        }), 200
                    else:
                        return jsonify({'errors': [{
                            'code': 404, 'message': "Not Found"
                            }]}), 404

        elif response.status_code == 404:
            return jsonify({'errors': [{
                "code": 401, 'message': "Unauthorized"
                }]}), 401
        else:
            return jsonify({'errors': [{
                "code": 500, 'message': "Server Error"
                }]}), 500

    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'errors': [{
            'code': 500, 'message': "Server Error"
            }]}), 500


@app.route('/group-task/<int:taskId>', methods=['GET', 'PATCH', 'DELETE'])
def group_task(taskId):
    try:
        response = requests.get('http://users.local/users',
                                headers={
                                    'Authorization':
                                    request.headers['Authorization']
                                    })
        if response.status_code == 200:
            match request.method:
                case 'GET':
                    task = GroupTask.query.get(taskId)
                    if task:
                        return jsonify({'data': {
                            'id': task.id,
                            'title': task.title,
                            'description': task.description,
                            'executor': task.executor,
                            'status': task.status,
                            'user_id': task.user_id,
                            'deadline':
                            task.deadline.strftime('%Y-%m-%d %H:%M:%S')
                        }}), 200
                    else:
                        return jsonify({'errors': [{
                            'code': 404, 'message': "Not Found"
                            }]}), 404
                case 'PATCH':
                    data = request.json
                    task = GroupTask.query.get(taskId)
                    if task:
                        task.title = data['title']
                        task.description = data['description']
                        task.deadline = data['deadline']
                        db.session.commit()
                        return jsonify({
                            'id': task.id,
                            'title': task.title,
                            'description': task.description,
                            'status': task.status,
                            'user_id': task.user_id,
                            'deadline':
                            task.deadline.strftime('%Y-%m-%d %H:%M:%S')
                        }), 200
                    else:
                        return jsonify({'errors': [{
                            'code': 404, 'message': "Not Found"
                            }]}), 404
                case 'DELETE':
                    task = GroupTask.query.get(taskId)
                    if task:
                        db.session.delete(task)
                        db.session.commit()
                        return jsonify({'message': 'Task deleted'}), 200
                    else:
                        return jsonify({'errors': [{
                            'code': 404, 'message': "Not Found"
                            }]}), 404

        elif response.status_code == 404:
            return jsonify({'errors': [{
                "code": 401, 'message': "Unauthorized"
                }]}), 401
        else:
            return jsonify({'errors': [{
                "code": 500, 'message': "Server Error"
                }]}), 500

    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'errors': [{
            'code': 500, 'message': "Server Error"
            }]}), 500


@app.route('/group-task', methods=['POST'])
def create_group_task():
    try:
        response = requests.get('http://users.local/users',
                                headers={
                                    'Authorization':
                                    request.headers['Authorization']
                                    })
        if response.status_code == 200:
            match request.method:
                case 'POST':
                    data = request.json()
                    if data:
                        new_task = GroupTask(
                            title=data['title'],
                            description=data['description'],
                            executor=data['executor'],
                            status=data['status'],
                            user_id=data['user_id'],
                            deadline=data['deadline']
                        )
                        db.session.add(new_task)
                        db.session.commit()
                        return jsonify({
                            'id': new_task.id,
                            'title': new_task.title,
                            'description': new_task.description,
                            'executor': new_task.executor,
                            'status': new_task.status,
                            'user_id': new_task.user_id,
                            'deadline':
                            new_task.deadline.strftime('%Y-%m-%d %H:%M:%S')
                        }), 200
                    else:
                        return jsonify({'errors': [{
                            'code': 400, 'message': 'Bad Request'
                            }]}), 400

        elif response.status_code == 404:
            return jsonify({'errors': [{
                "code": 401, 'message': "Unauthorized"
                }]}), 401
        else:
            return jsonify({'errors': [{
                "code": 500, 'message': "Server Error"
                }]}), 500

    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'errors': [{
            'code': 500, 'message': "Server Error"
            }]}), 500


@app.route('/group-task/status/<int:taskId>', methods=['GET'])
def update_status_group_task(taskId):
    try:
        response = requests.get('http://users.local/users',
                                headers={
                                    'Authorization':
                                    request.headers['Authorization']
                                    })
        if response.status_code == 200:
            match request.method:
                case 'PATCH':
                    task = GroupTask.query.get(taskId)
                    if task:
                        task.status = int(request.json()['status'])
                        return jsonify({
                            'id': task.id,
                            'title': task.title,
                            'description': task.description,
                            'executor': task.executor,
                            'status': task.status,
                            'user_id': task.user_id,
                            'deadline':
                            task.deadline.strftime('%Y-%m-%d %H:%M:%S')
                        }), 200
                    else:
                        return jsonify({'errors': [{
                            'code': 404, 'message': "Not Found"
                            }]}), 404

        elif response.status_code == 404:
            return jsonify({'errors': [{
                "code": 401, 'message': "Unauthorized"
                }]}), 401
        else:
            return jsonify({'errors': [{
                "code": 500, 'message': "Server Error"
                }]}), 500

    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'errors': [{
            'code': 500, 'message': "Server Error"
            }]}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
