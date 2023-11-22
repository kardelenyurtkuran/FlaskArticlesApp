from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_wtf import FlaskForm
import pymysql.cursors
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length, Email
from passlib.hash import sha256_crypt

app = Flask(__name__)

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'blog'
app.config['MYSQL_DATABASE_CURSORCLASS'] = 'DictCursor'
app.config['SECRET_KEY'] = '112233445566' #CSRF Token

connection = pymysql.connect(
    host=app.config['MYSQL_DATABASE_HOST'],
    user=app.config['MYSQL_DATABASE_USER'],
    password=app.config['MYSQL_DATABASE_PASSWORD'],
    db=app.config['MYSQL_DATABASE_DB'],
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)


# Kullanıcı Kayıt Formu
class RegisterForm(FlaskForm):
    name = StringField("İsim Soyisim", validators=[Length(min=4, max=25)])
    username = StringField("Kullanıcı Adı", validators=[Length(min=5, max=35)])
    email = StringField("Email Adresi", validators=[Email(message="Lütfen geçerli bir email adresi girin")])
    password = PasswordField("Şifre", validators=[
        DataRequired(message="Lütfen bir parola belirleyin"),
        EqualTo(fieldname="confirm", message="Parolonız uyuşmuyor")
    ])
    confirm = PasswordField("Parola Doğrula")

@app.route("/")
def index():
    return render_template("index2.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    try:
        form = RegisterForm(request.form)
        print(form.validate(), form.errors) # form.validate() false olursa dönen hatayı ekrana yazdırmak için
        if request.method == "POST" and form.validate(): #form.validate istenen tüm şartları sağlaması halinde True döner. Formda doldurulan alanlarda bir problem olup olmadığı kontrol edilir
            name = form.name.data #formda ki name bilgisini almak
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt(form.password.data) #password bilgisini şifreli kaydetmek için

            cursor = connection.cursor()
            query = "INSERT INTO users (name, email, username, password) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (name, email, username, password))
            connection.commit() #databaseden get yapılacağı zaman bunu kullanmana gerek yok
            cursor.close() #arka planda gereksiz kaynak kullanmamak için
            flash("Başarıyla Kayıt Oldunuz", "success") #message, category
            return redirect(url_for("index")) #fonksiyon ismine göre belli bir sayfaya göndermek için
        else:
            return render_template("register.html", form= form)
    except Exception as e:
        print(e)


@app.route("/article/<string:id>")
def detail(id):
    return "Article Id:" + id

if __name__ == "__main__":
    app.run(debug=True)
