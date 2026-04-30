from flask import Flask, render_template, url_for, request, redirect, session
import os
import plotly.graph_objects as go
import plotly.io as pio
from pripojeni import *
import mysql.connector
import bcrypt

mydb = mysql.connector.connect(
    host=HOST, user=USER, password=PASSWORD, database=DATABASE
)

app = Flask(__name__)
app.secret_key = 'Muj_tajny_klic'

@app.route("/1")
def hello():
    return "Hello World!"

@app.route("/2")
def ahoj():
    return render_template("index2.html")

@app.route("/3")
def text():
    return render_template("index3.html")

@app.route("/4")
def python():
    text = "Ahoj, světe z proměnné!"
    return render_template("index4.html", message=text)

@app.route("/5")
def obrazek():
    image_url = url_for('static', filename='images/img1.jpg')
    return render_template("index5.html", image_url=image_url)

@app.route("/6", methods=['GET', 'POST'])
def prvniFormularCislo():
    result = None
    if request.method == 'POST':
        number = request.form.get('number', type=int)
        if number is not None:
            result = number + 1 
    return render_template("index6.html", result=result)


# Vytvoření složky pro upload
app.config["UPLOAD_FOLDER"] = "static/uploadedFiles/"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

@app.route('/7', methods=['GET', 'POST'])
def nahrani_souboru():
    content = None
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.endswith('.txt'):
            # Uložení souboru na disk
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(file_path)
            
            # Čtení obsahu souboru
            file.seek(0)  # reset pozice po uložení
            content = file.read().decode('utf-8')
    return render_template('index7.html', content=content)

@app.route('/8')
def graph():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[1, 2, 3, 4], y=[10, 20, 25, 30],
                             mode='lines+markers', name='Data 1'))
    fig.add_trace(go.Scatter(x=[1, 2, 3, 4], y=[15, 18, 22, 27],
                             mode='lines+markers', name='Data 2'))

    fig.update_layout(
        title="Ukázkový interaktivní graf",
        xaxis_title="X-osa",
        yaxis_title="Y-osa",
        template="plotly_white"
    )

    graph_html = pio.to_html(fig, full_html=False) # HTML fragment
    return render_template("index8.html", graph_html=graph_html)

@app.route('/8_2')
def graph2():
    fig = go.Figure()
    fig.add_trace(go.Bar(x=[1, 2, 3, 4], y=[10, 20, 25, 30],
                             name='Data 1'))
    fig.add_trace(go.Bar(x=[1, 2, 3, 4], y=[15, 18, 22, 27],
                             name='Data 2'))

    fig.update_layout(
        title="Ukázkový interaktivní graf",
        xaxis_title="X-osa",
        yaxis_title="Y-osa",
        template="plotly_white"
    )

    graph_html = pio.to_html(fig, full_html=False) # HTML fragment
    return render_template("index8.html", graph_html=graph_html)

@app.route('/9/<int:id>/<string:name>', methods=['GET'])
def parametry(id, name):
    return render_template("index9.html", id=id, name=name)

@app.route('/10', methods=['GET', 'POST'])
def redirekting():
    result = None
    if request.method != 'POST':
        return render_template("index10.html", result=result)

    number = request.form.get('number', type=int)
    result = number

    if result == 1:
        return redirect('/1')     # přesměruj na route /1
    elif result == 2:
        return redirect('/2')     # přesměruj na route /2
    else:
        return render_template("index10.html", result=result)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['jmeno']
        mail = request.form['email']
        psw = request.form['psw']

        # Hashování hesla
        hashed_password = bcrypt.hashpw(psw.encode('utf-8'), bcrypt.gensalt())
        hesloDoDB = hashed_password.decode('utf-8')

        # Připojení k DB
        mydb = mysql.connector.connect(
            host=HOST, user=USER, password=PASSWORD, database=DATABASE
        )
        mycursor = mydb.cursor()

        # Vytvoření tabulky (pokud neexistuje)
        mycursor.execute("""CREATE TABLE IF NOT EXISTS uzivatele (
            id int AUTO_INCREMENT PRIMARY KEY,
            jmeno varchar(35) NOT NULL,
            email varchar(50) NOT NULL,
            heslo varchar(255) NOT NULL
        );""")
        mydb.commit()

        # Vložení uživatele
        sql = "INSERT INTO uzivatele (jmeno, email, heslo) VALUES (%s, %s, %s)"
        mycursor.execute(sql, (name, mail, hesloDoDB))
        mydb.commit()

        return redirect(url_for('login'))  # po registraci → přihlášení

    return render_template("register.html")

# Route /login — přihlášení uživatele
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['psw']

        mydb = mysql.connector.connect(
            host=HOST, user=USER, password=PASSWORD, database=DATABASE
        )
        mycursor = mydb.cursor()
        mycursor.execute("SELECT heslo FROM uzivatele WHERE email = %s;", (email,))
        result = mycursor.fetchone()

        if result:
            stored_hash = result[0]
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                session['email'] = email  # uložení do session
                return redirect(url_for('home_login_ukazka'))
            else:
                error_message = "Nesprávné heslo."
        else:
            error_message = "Uživatel nenalezen."

        return render_template("login.html", error=error_message)

    return render_template("login.html")

# Route /home — domovská stránka (zobrazí email přihlášeného uživatele)
@app.route('/home')
def home_login_ukazka():
    return render_template('home.html', email=session.get('email'))

# Route /logout — odhlášení uživatele
@app.route('/logout')
def logout():
    session.pop('email', None)  # odebrání ze session
    return redirect(url_for('home_login_ukazka'))

# Route /tabulka — zobrazení dat z DB (pouze pro přihlášené)
@app.route('/tabulka')
def tabulka():
    if 'email' not in session:
        return redirect(url_for('login'))  # ochrana stránky

    mydb = mysql.connector.connect(
        host=HOST, user=USER, password=PASSWORD, database=DATABASE
    )
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM uzivatele")
    result = mycursor.fetchall()

    return render_template("tabulka.html", email=session.get('email'), items=result)

if __name__ == "__main__":
    app.run(debug=True)