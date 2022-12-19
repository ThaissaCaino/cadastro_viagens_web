from flask import Flask, render_template, request, g, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'flask'
BANCO = 'viagens.bd'


def criar_banco():
    bd = sqlite3.connect(BANCO)
    bd.execute(
        '''CREATE TABLE IF  NOT EXISTS viagens(
            codigo INTEGER PRIMARY KEY,
            municipio TEXT NOT NULL,
            estado  TEXT NOT NULL,
            atividade  TEXT NOT NULL)'''
    )
    bd.close()


def bd():
    if 'bd' not in g:
        g.bd = sqlite3.connect(BANCO)
    return g.bd


@app.teardown_appcontext
def fechar_conexao(exeption):
    if 'bd' in g:
        g.bd.close()


@app.route("/index")
def home():
    if session.get('usuario_logado') == None or session['usuario_logado'] == None:
        return redirect(url_for('login'))
    return render_template('index.html', titulo="Memórias de uma viajante", subtitulo1="Veja a lista das Viagens",
                           subtitulo2="Cadastre uma nova viagem")


@app.route('/listar')
def listar():
    if session.get('usuario_logado') == None or session['usuario_logado'] == None:
        return redirect(url_for('login'))
    viagem = bd().execute('''SELECT * FROM viagens''').fetchall()
    return render_template('listar.html', lista_viagens=viagem, titulo="Lista das viagens")


@app.route('/novo', methods=('GET', 'POST'))
def novo():
    if session.get('usuario_logado') == None or session['usuario_logado'] == None:
        return redirect(url_for('login'))

    if request.method == 'POST':
        codigo = request.form['codigo']
        municipio = request.form['municipio']
        estado = request.form['estado']
        atividade = request.form['atividade']
        bd().execute('''INSERT INTO viagens(
        codigo, municipio, estado, atividade)
        values(?, ?, ?, ?)''', [codigo, municipio, estado, atividade])
        bd().commit()
        flash('Viagem cadastrada com sucesso', 'success')
        return redirect(url_for('home'))
    return render_template('novo.html', titulo="Adicione sua mais nova aventura")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ LOGIN ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route('/')
def login():
    proxima = request.args.get('proxima')
    return render_template('login.html', proxima=proxima, titulo='Faça seu login')


@app.route('/autenticar', methods=['POST', ])
def autenticar():
    if 'resiliencia' == request.form['senha']:
        session['usuario_logado'] = request.form['usuario']
        flash(session['usuario_logado'] + ' logado com sucesso')  # Essa concateção permite a msg de login tenha o nome do usuário logado.
        return redirect('/index')
    elif request.form['senha'] != 'resiliencia':
        flash('Senha incorreta, tente novamente.', 'warnings')
        return redirect('/')
    else:
        flash(session['Usuário não logado'], 'warnings')
        return redirect('/')


@app.route('/logout')
def logout():
    session['usuario_logado'] = None
    flash('Logout efetuado com sucesso!', 'success')
    return redirect(url_for('login'))


if __name__ == "__main__":
    criar_banco()
    app.run(debug=True)
