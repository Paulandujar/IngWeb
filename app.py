from flask import Flask ,render_template,request,url_for,redirect,flash,session,g
from flask_restful import reqparse, abort, Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields

app = Flask(__name__)
api = Api(app)
app.secret_key = "super secret key"

SQLALCHEMY_ECHO = False 
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'.format(DB_USER="root", DB_PASS="", DB_HOST="localhost", DB_NAME="trabajofinal") 

# Configure the SqlAlchemy part of the app instance
app.config["SQLALCHEMY_ECHO"] = SQLALCHEMY_ECHO
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS

db = SQLAlchemy()
db.init_app(app)
ma = Marshmallow(app)

class usuarioM(db.Model):
    __tablename__ = "usuario"
    ID=db.Column(db.Integer, primary_key=True,autoincrement=True)
    rol=db.Column(db.String(10))
    usuario=db.Column(db.String(20))
    password=db.Column(db.String(20))
    nombre=db.Column(db.String(20))
    telefono=db.Column(db.Integer)

class pedido(db.Model):
    __tablename__ = "pedido"
    numPedido=db.Column(db.Integer, primary_key=True,autoincrement=True)
    dniPaciente=db.Column(db.String(9))
    numHabitacion=db.Column(db.Integer)
    IDmedicamento=db.Column(db.Integer)
    IDusuario=db.Column(db.Integer)
    estado=db.Column(db.String(10))

class medicamento(db.Model):
    __tablename__ = "medicamento"
    ID=db.Column(db.Integer, primary_key=True,autoincrement=True)
    nombre=db.Column(db.String(20))
    laboratorio=db.Column(db.String(20))
    viaAdministracion=db.Column(db.String(10))
    dosis=db.Column(db.String(10))
    principioActivo=db.Column(db.String(20))
    prescripcionMedica=db.Column(db.String(5))
    stock=db.Column(db.Integer)

@app.before_request
def before_request():
    if 'user' in session:
        all_users=usuarioM.query.filter_by(ID=session['user'])
        for user in all_users:
            if user.ID==session['user']:
                 g.user=user
    else:
        g.user=None     

@app.route('/')
def index():
    if g.user==None:
        return redirect('/login')
    return render_template('index.html')

@app.route('/login')
def logintem():
    session.pop('user',None)
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    all_users=usuarioM.query.all()
    user=request.form["user"]
    pwd=request.form["pass"]
    for usuario in all_users:
        if(user==usuario.usuario and pwd==usuario.password and usuario.rol=="medico"):
            session['user']=usuario.ID
            return redirect('/')
        if(user==usuario.usuario and pwd==usuario.password and usuario.rol=="farmacia"):
            session['user']=usuario.ID
            return redirect('/')
    if((str(request.form["rname"])!="") and  (str(request.form["rpass"])!="")):
            rusername=request.form["rusername"]
            rname=request.form["rname"]
            rtelefono=request.form["rtelefono"]
            rpass=request.form["rpass"]
            rconfirmation=request.form["cpass"]
            rRol=request.form["rol"]
            if(rpass==rconfirmation):
                adduser=usuarioM(usuario=rusername,password=rpass,rol=rRol,nombre=rname,telefono=rtelefono)
                db.session.add(adduser)
                db.session.commit()
                flash("Register succesfully!") 
    return render_template('login.html')

@app.route('/listadoMedicamentos')
def verListadoMedicamentos():
    all_medicamentos=medicamento.query.all()
    return render_template('listadoMedicamentos.html',medicamentos=all_medicamentos)

@app.route('/hacerPedido' , methods=['GET'])
def add():
    if g.user==None:
        return redirect('/login')
    med=medicamento.query.all()
    return render_template('hacerPedido.html',medicamentos=med)

@app.route('/hacerPedido' , methods=['POST'])
def hacerPedido():
    if g.user==None:
        return redirect('/login')
    rdniPaciente=request.form['paciente']
    rnumhab=request.form['hab']
    rIDmed=request.form.get('idmedicamento')
    rIDusuario= g.user.ID
    restado="Pendiente"
    try:
        hacerPedido=pedido(dniPaciente=rdniPaciente,numHabitacion=rnumhab,IDmedicamento=rIDmed,IDusuario=rIDusuario, estado=restado)
        db.session.add(hacerPedido)
        db.session.commit()
        flash("Pedido registrado correctamente!")
        return redirect('/listadoMedicamentos')
    except:
        "Algo ha ido mal!!"

@app.route('/listadoPedidos')
def verListadoPedidos():
    all_pedidos=pedido.query.all()
    return render_template('listadoPedidos.html',pedidos=all_pedidos)

@app.route('/listadoPedidos/<ID>' , methods=['GET'])
def get(ID):
    rpedido=pedido.query.filter_by(ID=ID)
    return render_template('actualizarPedido.html',pedidos=rpedido)

if __name__ == '__main__':
    app.run(debug=True)