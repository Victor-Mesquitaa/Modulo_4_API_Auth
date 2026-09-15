from flask import Flask, jsonify, request
from models.user import User
from database import db
from auth import login_manager, login_user, current_user, logout_user, login_required

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login' # Faz com que o Flask-Login redirecione para a rota de login quando um usuário não autenticado tenta acessar uma rota protegida.

@login_manager.user_loader # Funciona como um callback que o Flask-Login usa para carregar um usuário a partir do seu ID armazenado na sessão.
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username and password:
        user = User.query.filter_by(username=username).first() # check if user exists

        if user and user.password == password:
            login_user(user)
            print(current_user.is_authenticated)  # Check if the user is authenticated
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'message': 'Invalid username or password'}), 401

@app.route('/logout', methods=['GET'])
@login_required # This decorator ensures that the user must be logged in to access this route. If the user is not logged in, they will be redirected to the login page.
def logout():
    logout_user()
    return jsonify({'message': 'Logout successful'}), 200



if __name__ == '__main__':
    app.run(debug=True)
