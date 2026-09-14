import os, sqlite3, secrets
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import qrcode
BASE=os.path.dirname(os.path.abspath(__file__)); DB=os.path.join(BASE,'escuela177.db')
app=Flask(__name__); app.secret_key=os.environ.get('SECRET_KEY',secrets.token_hex(32))
ADMIN_USER=os.environ.get('ADMIN_USER','admin'); ADMIN_PASSWORD=os.environ.get('ADMIN_PASSWORD','CAMBIAR-ESTA-CLAVE')
def db():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init_db():
 c=db(); c.executescript('''CREATE TABLE IF NOT EXISTS personal(id INTEGER PRIMARY KEY AUTOINCREMENT,nombre TEXT NOT NULL,dni TEXT NOT NULL UNIQUE,celular TEXT NOT NULL,cargo TEXT NOT NULL,turno TEXT NOT NULL,pin_hash TEXT NOT NULL,creado TEXT NOT NULL);CREATE TABLE IF NOT EXISTS registros(id INTEGER PRIMARY KEY AUTOINCREMENT,personal_id INTEGER NOT NULL,entrada TEXT NOT NULL,salida TEXT,FOREIGN KEY(personal_id) REFERENCES personal(id));'''); c.commit(); c.close()
def now(): return datetime.now().astimezone()
def iso(): return now().isoformat(timespec='seconds')
def admin_required(f):
 @wraps(f)
 def w(*a,**k): return f(*a,**k) if session.get('admin') else redirect(url_for('admin_login'))
 return w
@app.route('/')
def home(): return render_template('home.html')
@app.route('/registro',methods=['GET','POST'])
def registro():
 if request.method=='POST':
  d={k:request.form[k].strip() for k in ('nombre','dni','celular','cargo','turno','pin')}
  if not all(d.values()) or len(d['pin'])!=6 or not d['pin'].isdigit(): flash('Completá todos los datos y usá un PIN de 6 dígitos.','error'); return render_template('registro.html')
  c=db()
  try: c.execute('INSERT INTO personal(nombre,dni,celular,cargo,turno,pin_hash,creado) VALUES(?,?,?,?,?,?,?)',(d['nombre'],d['dni'],d['celular'],d['cargo'],d['turno'],generate_password_hash(d['pin']),iso())); c.commit()
  except sqlite3.IntegrityError: c.close(); flash('Ese DNI ya está registrado.','error'); return render_template('registro.html')
  c.close(); flash('Registro creado. Guardá tu PIN.','ok'); return redirect(url_for('home'))
 return render_template('registro.html')
def marcar(tipo):
 dni=request.form['dni'].strip(); pin=request.form['pin'].strip(); c=db(); p=c.execute('SELECT * FROM personal WHERE dni=?',(dni,)).fetchone()
 if not p or not check_password_hash(p['pin_hash'],pin): c.close(); return render_template('marcar.html',tipo=tipo,error='DNI o PIN incorrectos.')
 openr=c.execute('SELECT * FROM registros WHERE personal_id=? AND salida IS NULL ORDER BY id DESC LIMIT 1',(p['id'],)).fetchone()
 if tipo=='entrada':
  if openr: c.close(); return render_template('marcar.html',tipo=tipo,error='Ya tenés una entrada abierta.')
  c.execute('INSERT INTO registros(personal_id,entrada) VALUES(?,?)',(p['id'],iso())); msg='Ingreso registrado'
 else:
  if not openr: c.close(); return render_template('marcar.html',tipo=tipo,error='No existe una entrada abierta.')
  c.execute('UPDATE registros SET salida=? WHERE id=?',(iso(),openr['id'])); msg='Salida registrada'
 c.commit(); c.close(); return render_template('confirmacion.html',mensaje=msg,nombre=p['nombre'],momento=iso())
@app.route('/entrada',methods=['GET','POST'])
def entrada(): return marcar('entrada') if request.method=='POST' else render_template('marcar.html',tipo='entrada')
@app.route('/salida',methods=['GET','POST'])
def salida(): return marcar('salida') if request.method=='POST' else render_template('marcar.html',tipo='salida')
@app.route('/qr/<tipo>.png')
def qr(tipo):
 if tipo not in ('entrada','salida'): return 'QR inválido',404
 base=os.environ.get('BASE_URL',request.url_root.rstrip('/')); path=os.path.join(BASE,f'qr_{tipo}.png'); qrcode.make(f'{base}/{tipo}').save(path); return send_file(path,mimetype='image/png')
@app.route('/admin/login',methods=['GET','POST'])
def admin_login():
 if request.method=='POST' and request.form['usuario']==ADMIN_USER and secrets.compare_digest(request.form['clave'],ADMIN_PASSWORD): session['admin']=True; return redirect(url_for('admin'))
 if request.method=='POST': flash('Usuario o contraseña incorrectos.','error')
 return render_template('admin_login.html')
@app.route('/admin/logout')
def logout(): session.clear(); return redirect(url_for('home'))
@app.route('/admin')
@admin_required
def admin():
 c=db(); rows=c.execute('SELECT r.*,p.nombre,p.dni,p.cargo FROM registros r JOIN personal p ON p.id=r.personal_id ORDER BY r.id DESC').fetchall(); presentes=c.execute('SELECT COUNT(*) n FROM registros WHERE salida IS NULL').fetchone()['n']; total=c.execute('SELECT COUNT(*) n FROM personal').fetchone()['n']; c.close(); return render_template('admin.html',rows=rows,presentes=presentes,total_personal=total)
@app.route('/admin/personal')
@admin_required
def personal():
 c=db(); people=c.execute('SELECT * FROM personal ORDER BY nombre').fetchall(); c.close(); return render_template('personal.html',people=people)
@app.route('/admin/export.csv')
@admin_required
def export():
 import csv,io
 c=db(); rows=c.execute('SELECT p.nombre,p.dni,p.cargo,p.turno,r.entrada,r.salida FROM registros r JOIN personal p ON p.id=r.personal_id ORDER BY r.entrada DESC').fetchall(); c.close(); out=io.StringIO(); w=csv.writer(out,delimiter=';'); w.writerow(['Nombre','DNI','Cargo','Turno','Entrada','Salida']); [w.writerow([r['nombre'],r['dni'],r['cargo'],r['turno'],r['entrada'],r['salida'] or '']) for r in rows]; from flask import Response; return Response('\ufeff'+out.getvalue(),mimetype='text/csv',headers={'Content-Disposition':'attachment; filename=registro_escuela_177.csv'})
init_db()
if__name__=='__main__': init_db(); app.run(host='0.0.0.0',port=int(os.environ.get('PORT','5000')))
