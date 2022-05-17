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
    dniPaciente=db.Column(db.String(10))
    numHabitacion=db.Column(db.Integer)
    IDmedicamento=db.Column(db.Integer)
    IDusuario=db.Column(db.Integer)
    estado=db.Column(db.String(10))

class medicamento(db.Model):
    __tablename__ = "medicamento"
    ID=db.Column(db.Integer, primary_key=True,autoincrement=True)
    nombre=db.Column(db.String(50))
    laboratorio=db.Column(db.String(50))
    viaAdministracion=db.Column(db.String(50))
    dosis=db.Column(db.String(50))
    principioActivo=db.Column(db.String(50))
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
        med = medicamento.query.all()
        db.session.add(hacerPedido)
        db.session.commit()
        flash("Pedido registrado correctamente!")
        return render_template('hacerPedido.html', medicamentos = med)
    except:
        flash("Algo ha ido mal!!")
        return render_template('hacerPedido.html', medicamentos = med)

@app.route('/listadoPedidos')
def verListadoPedidos():
    all_pedidos=pedido.query.all()
    return render_template('listadoPedidos.html',pedidos=all_pedidos)

@app.route('/actualizarPedido/<ID>' , methods=['GET'])
def get(ID):
    rpedido=pedido.query.filter_by(numPedido=ID)
    med=medicamento.query.all()
    return render_template('actualizarPedido.html',pedidos=rpedido,medicamentos=med)

@app.route('/actualizarPedido')
def getact():
    if g.user==None:
        return redirect('/login')
    med=medicamento.query.all()
    return render_template('actualizarPedido.html',medicamentos=med)

@app.route('/actualizarPedido/<ID>', methods=['POST'])
def actualizarP(ID):
    if g.user==None:
        return redirect('/login')
    updateP=pedido.query.get_or_404(ID)
    updateP.dniPaciente=request.form['paciente']
    updateP.numHabitacion=request.form['hab']
    updateP.IDmedicamento=request.form.get('idmedicamento')
    updateP.IDusuario= g.user.ID
    updateP.estado=request.form['estado']
    try:
        db.session.commit()
        flash("Pedido actualizado correctamente!")
        rpedido=pedido.query.filter_by(numPedido=ID)
        med=medicamento.query.all()
        return render_template('actualizarPedido.html',pedidos=rpedido,medicamentos=med)
    except:
        flash("Algo ha ido mal!!")
        return render_template('actualizarPedido.html')
    
@app.route('/borrarPedido/<ID>')
def borrarpedido(ID):
    if g.user==None:
        return redirect('/login')
    borrarP=pedido.query.get_or_404(ID) 
    try:
        db.session.delete(borrarP)
        db.session.commit()
        ped = pedido.query.all()
        flash("El pedido ha sido eliminado correctamente") 
        return render_template('listadoPedidos.html', pedidos = ped)
    except: 
        flash("Algo ha ido mal!!")
        return render_template('listadoPedidos.html', pedidos = ped)

@app.route('/nuevoMedicamento' , methods=['GET'])
def addmed():
    if g.user==None:
        return redirect('/login')
    return render_template('nuevoMedicamento.html')

@app.route('/nuevoMedicamento' , methods=['POST'])
def nuevoMed():
    if g.user==None:
        return redirect('/login')
    rnombre=request.form['nombre']
    rlab=request.form['lab']
    rvia=request.form.get('via')
    rdosis=request.form.get('dosis')
    rpa=request.form.get('pa')
    rpm=request.form.get('pm')
    rstock=request.form.get('stock')
    try:
        med=medicamento(nombre=rnombre,laboratorio=rlab,viaAdministracion=rvia,dosis=rdosis,principioActivo=rpa,prescripcionMedica=rpm,stock=rstock)
        db.session.add(med)
        db.session.commit()
        flash("Medicamento registrado correctamente!")
        return render_template('nuevoMedicamento.html')
    except:
        flash("Algo ha ido mal!!")
        return render_template('nuevoMedicamento.html')

@app.route('/actualizarMedicamento/<ID>' , methods=['GET'])
def actmedget(ID):
    if g.user==None:
        return redirect('/login')
    med=medicamento.query.filter_by(ID=ID)
    return render_template('actualizarMedicamento.html', medicamentos=med)

@app.route('/actualizarMedicamento/<ID>' , methods=['POST'])
def actMed(ID):
    if g.user==None:
        return redirect('/login')
    updateMed=medicamento.query.get_or_404(ID)
    updateMed.nombre=request.form['nombre']
    updateMed.laboratorio=request.form['lab']
    updateMed.viaAdministracion=request.form['via']
    updateMed.dosis=request.form['dosis']
    updateMed.principioActivo=request.form['pa']
    updateMed.prescripcionMedica=request.form['pm']
    updateMed.stock=request.form['stock']
    try:
        db.session.commit()
        flash("Medicamento actualizado correctamente!")
        med=medicamento.query.filter_by(ID=ID)
        return render_template('actualizarMedicamento.html', medicamentos=med)
    except:
        flash("Algo ha ido mal!!")
        return render_template('actualizarMedicamento.html')
    
@app.route('/datosUsuario/<ID>' , methods=['GET'])
def datos(ID):
    if g.user==None:
        return redirect('/login')
    usu = usuarioM.query.filter_by(ID=ID)
    return render_template('datosUsuario.html', usuarios=usu)

@app.route('/datosUsuario/<ID>' , methods=['POST'])
def actUsu(ID):
    if g.user==None:
        return redirect('/login')
    updateUsu=usuarioM.query.get_or_404(ID)
    updateUsu.rol=request.form['rol']
    updateUsu.usu=request.form['usu']
    updateUsu.nombre=request.form['nombre']
    updateUsu.telefono=request.form['tel']
    if request.form['pass'] != "":
        updateUsu.password=request.form['pass']
    try:
        db.session.commit()
        flash("Usuario actualizado correctamente!")
        return render_template('datosUsuario.html')
    except:
        flash("Algo ha ido mal!!")
        return render_template('datosUsuario.html')


if __name__ == '__main__':
    app.run(debug=True)