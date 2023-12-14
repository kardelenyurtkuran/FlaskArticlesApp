from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_wtf import FlaskForm
import pymysql.cursors
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length, Email
from passlib.hash import sha256_crypt
from functools import wraps #decoratorlarda kullanılan yapı

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

#Kullanıcı giriş decorator
#Flask dökümanları içinden hazır bulabilirsin

def login_required(f): #decorator ana yapı
    @wraps(f) #decorator ana yapı
    def decorated_function(*args, **kwargs): #decorator ana yapı
        if "logged_in" in session: #session içinde logged_in varsa değer True olur yani kullanıcı giriş yapmıştır. Bu durumda kullanıcı girişi yapılmadan ../dashboard uzatsına ulaşılamaz
            return f(*args, **kwargs) #decorator ana yapı
        else:
            flash("Bu sayfayı görüntülemek için lütfen giriş yapın", "danger")
            return redirect(url_for("login")) #giriş sayfasına yönlendir
    return decorated_function #decorator ana yapı


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

class LoginForm(FlaskForm):
    username = StringField("Kullanıcı Adı")
    password = PasswordField("Parola")


@app.route("/")
def index():
    return render_template("index2.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/articles")
def articles():
    cursor =connection.cursor()
    query = "SELECT * FROM articles"
    result = cursor.execute(query)

    if result>0: #eğer makale varsa
        articles = cursor.fetchall()
        return render_template("articles.html", articles = articles)
    else:
        return render_template("articles.html")


@app.route("/dashboard")
@login_required #giriş yapılmadan hemen önce decorator kontrol et, tüm giriş yaptığın fonksiyonlarda bu yapıyı kullan,
# büyük yapılarda her seferinde session kontrol edersin çok fazla if şartı yazman gerekir, decorator aktif kullan
def dashboard():
    cursor = connection.cursor()
    query = "SELECT * FROM articles WHERE author = %s"
    result = cursor.execute(query, (session["username"],))
    if result >0:
        articles = cursor.fetchall()
        return render_template("dashboard.html", articles=articles)
    else:
        return render_template("dashboard.html")

    return render_template("dashboard.html")

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
            return redirect(url_for("login")) #fonksiyon ismine göre belli bir sayfaya göndermek için, kayıt olduktan sonra giriş yap sayfasına gelir
        else:
            return render_template("register.html", form= form) #RegisterForm ile oluşturduğun formu göndermek için form=form
    except Exception as e:
        print(e)


@app.route("/article/<string:id>")
def detail(id):
    return "Article Id:" + id

#Login İşlemi
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
        username =form.username.data
        password_entered = form.password.data
        cursor = connection.cursor()
        query = "SELECT * FROM users WHERE username = %s"
        result = cursor.execute(query, (username,)) #tek elemanlı demetse eğer yanına , koymalısın yoksa demet olarak algılamıyor

        if result > 0: #girilen kullanıcı adına sahip kullanıcı varsa
            data = cursor.fetchone() # username'e sahip satırın tamamı
            real_password = data["password"]

            if sha256_crypt.verify(password_entered, real_password): #kullanıcı var ve parolası doğru
                flash("Başarıyla giriş yaptınız", "success")
                session["logged_in"] = True  #Oturum kontrolü
                session["username"] = username

                return redirect(url_for("index"))

            else: #parola yanlış
                flash("Şifre Hatalı", "danger")
                session["logged_in"] = False  # Oturum kontrolü
                return redirect(url_for("login"))

        else: #kullanıcı yok
            flash("Böyle bir kullanıcı bulunmuyor", "danger")
            session["logged_in"] = False  # Oturum kontrolü
            return redirect(url_for("login"))

        cursor.close()  # arka planda gereksiz kaynak kullanmamak için
    return render_template("login.html", form=form)  #LoginForm ile oluşturduğun formu göndermek için form=form

#Makale ekleme
@app.route("/addarticle", methods=["GET", "POST"])
def addarticle():
    form = ArticleForm(request.form)
    print(session["username"])
    if request.method == "POST" and form.validate():
        title = form.title.data
        content = form.content.data
        cursor = connection.cursor()
        query = "INSERT INTO articles(title, author, content) VALUES(%s, %s, %s)"
        cursor.execute(query, (title,session["username"], content))
        connection.commit()  # databaseden get yapılacağı zaman bunu kullanmana gerek yok
        cursor.close()
        flash("Makale Başarıyla Eklendi", "success")
        return redirect(url_for("dashboard"))
    return render_template("addarticle.html", form =form)  #LoginForm ile oluşturduğun formu göndermek için form=form

#Makale Form

class ArticleForm(FlaskForm):
    title = StringField("Makale Başlığı", validators=[Length(min=5, max=100)]) #lineedit benzeri bir alan, makale başlığı
    content = TextAreaField("Makale İçeriği", validators=[Length(min=10)]) #lineeditten daha geniş bir alan oluşturmak için, makale içeriği



# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("login"))
if __name__ == "__main__":
    app.run(debug=True)
