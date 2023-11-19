#template inheritance, blocks
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/") #gidilen adres uzantısı
def index(): #belirtilen uzantıda yapılacak işlemler
    return render_template("index1.html") #index1.html dosyası layout.html dosyasından miras almıştır


@app.route("/about")
def about():
    return "Hakkında"

@app.route("/about/kardelen")
def kardelen():
    return "Kardelen"


if __name__ == "__main__":
    app.run(debug=True) #Herhangi bir hata olması durumunda ekrana hataları yazar