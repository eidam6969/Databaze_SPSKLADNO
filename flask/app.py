from flask import Flask, render_template, url_for

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run()