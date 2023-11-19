# Yalnızca String döndüren sayfalar için

from flask import Flask

app = Flask(__name__)

@app.route("/") #gidilen adres uzantısı
def index(): #belirtilen uzantıda yapılacak işlemler
    return "Ana Sayfa"


@app.route("/about")
def about():
    return "Hakkında"

@app.route("/about/kardelen")
def kardelen():
    return "Kardelen"


if __name__ == "__main__":
    app.run(debug=True) #Herhangi bir hata olması durumunda ekrana hataları yazar