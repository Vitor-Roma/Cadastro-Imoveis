from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user
from forms import LoginForm

app = Flask(__name__, template_folder='templates')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///imoveis.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123@127.0.0.1:3310/imoveis'
app.config['SECRET_KEY'] = '123'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Imovel(db.Model):
    __tablename__ = "Imoveis"
    id = db.Column(db.Integer, primary_key=True)
    endereço = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(100), nullable=False)
    preço = db.Column(db.Numeric(10, 2), nullable=False)

    def __init__(self, endereço, estado, preço):
        self.endereço = endereço
        self.estado = estado
        self.preço = preço


class Users(db.Model, UserMixin):
    __tablename__ = "Users"
    _id = db.Column('id', db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), nullable=False, unique=True)
    senha = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)

    @property
    def login_required(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self._id)

    def __init__(self, usuario, senha, email):
        self.usuario = usuario
        self.senha = senha
        self.email = email


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastrar():
    if request.method == 'POST':
        imoveis = Imovel(request.form['endereço'], request.form['estado'], request.form['preço'])
        db.session.add(imoveis)
        db.session.commit()
        return redirect(url_for('listar'))
    return render_template('cadastrar.html')


@app.route('/listar', methods=['GET', 'POST'])
@login_required
def listar():
    termo = request.args.get('termo')

    if termo:
        imoveis = Imovel.query.filter(
            Imovel.endereço.contains(termo) | Imovel.estado.contains(termo) | Imovel.preço.contains(termo))
    else:
        imoveis = Imovel.query.all()
    return render_template("listar.html", imoveis=imoveis)


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    imovel = Imovel.query.get(id)
    db.session.delete(imovel)
    db.session.commit()
    return redirect(url_for('listar'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    imoveis = Imovel.query.get(id)
    if request.method == "POST":
        imoveis.endereço = request.form['endereço']
        imoveis.estado = request.form['estado']
        imoveis.preço = request.form['preço']
        db.session.commit()
        return redirect(url_for('listar'))
    return render_template('edit.html', imoveis=imoveis)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(usuario=form.usuario.data).first()
        if user and user.senha == form.senha.data:
            login_user(user)
            return render_template('logged.html')

    return render_template('login.html', form=form)


@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        email = request.form['email']

        user = Users(usuario, senha, email)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('registrar.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
