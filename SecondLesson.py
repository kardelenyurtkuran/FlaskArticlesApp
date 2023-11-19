#template döndüren sayfalar
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/") #gidilen adres uzantısı
def index(): #belirtilen uzantıda yapılacak işlemler
    sayi = 10
    sayi2 = 20
    article = dict()
    article["title"] = "Deneme"
    article["body"] = "Deneme123"
    article["author"] = "Kardelen"
    return render_template("index.html", number=sayi, number2=sayi2, article=article) #belirtilen uzantıda ki dönmesi gereken template dosyası


@app.route("/about")
def about():
    return "Hakkında"

@app.route("/about/kardelen")
def kardelen():
    return "Kardelen"


if __name__ == "__main__":
    app.run(debug=True) #Herhangi bir hata olması durumunda ekrana hataları yazar