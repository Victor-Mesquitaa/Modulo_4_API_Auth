from flask import Flask, jsonify, request
from models.user import User
from database import db
from auth import login_manager, login_user, current_user, logout_user, login_required

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@localhost:3306/flask-crud'

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

@app.route('/user/<int:user_id>', methods=['GET'])
@login_required # This decorator ensures that the user must be logged in to access this route. If the user is not logged in, they will be redirected to the login page.
def get_user(user_id): # Função que lida com a recuperação de informações de um usuário específico. Ela recebe o ID do usuário como parâmetro na URL, consulta o banco de dados para encontrar o usuário correspondente e retorna as informações do usuário em formato JSON. Se o usuário não for encontrado, a função retorna uma mensagem de erro apropriada.
    user = User.query.get(user_id)

    if user:
        return jsonify({"username": user.username})
    else:
        return jsonify({"message": "user not found"}), 404

@app.route('/user/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id): 
    data = request.json
    user = User.query.get(user_id)

    if user and data.get("password"):
        user.password = data.get("password")
        db.session.commit()
        return jsonify({"message": f"User {user_id} updated sucessfuly"})
    else:
        return jsonify({"message": "user not found"}), 404
    

@app.route('/user/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found!"}), 404
    
    if user_id == current_user.id:
        return jsonify({"message": "You cannot delete your own account!"}), 403
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
