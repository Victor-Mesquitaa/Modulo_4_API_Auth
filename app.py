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
def load_user(user_id): # Função que recebe o ID do usuário e retorna o objeto do usuário correspondente. O Flask-Login usa essa função para recuperar o usuário atual a partir do ID armazenado na sessão.
    return User.query.get(int(user_id))

@app.route('/login', methods=['POST'])
def login(): # Função que lida com a autenticação do usuário. Ela recebe os dados de login (nome de usuário e senha) via JSON, verifica se o usuário existe e se a senha está correta. Se a autenticação for bem-sucedida, o usuário é logado usando a função login_user() do Flask-Login.
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
def logout(): # Função que lida com o logout do usuário. Ela é protegida pelo decorador @login_required, garantindo que apenas usuários autenticados possam acessá-la. Quando chamada, a função realiza o logout do usuário atual usando a função logout_user()
    logout_user()
    return jsonify({'message': 'Logout successful'}), 200

@app.route('/user', methods=['POST'])
@login_required # This decorator ensures that the user must be logged in to access this route. If the user is not logged in, they will be redirected to the login page.
def create_user(): # Função que lida com a criação de um novo usuário. Ela recebe os dados do usuário (nome de usuário e senha) via JSON, verifica se o nome de usuário já existe no banco de dados e, se não existir, cria um novo usuário e o adiciona ao banco de dados. Se o nome de usuário já existir ou se os dados estiverem incompletos, a função retorna uma mensagem de erro apropriada.
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username and password:
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User created successfully'}), 201
    else:
        return jsonify({'message': 'Username and password are required'}), 400

if __name__ == '__main__':
    app.run(debug=True)
