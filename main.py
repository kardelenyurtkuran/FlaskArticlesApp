from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_wtf import FlaskForm
import pymysql.cursors
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length, Email
from passlib.hash import sha256_crypt
from functools import wraps #structure used in decorators

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

#user login decorator
#You can find it ready in Flask documentation.

def login_required(f): #decorator main structure
    @wraps(f) #decorator main structure
    def decorated_function(*args, **kwargs): #decorator main structure
        if "logged_in" in session: #If there is logged_in in the session, the value is True, meaning the user is logged in. In this case, the ../dashboard extension cannot be accessed without user login.
            return f(*args, **kwargs) #decorator main structure
        else:
            flash("Please log in to view this page", "danger")
            return redirect(url_for("login")) #redirect to login page
    return decorated_function #decorator main structure


#Register User Form
class RegisterForm(FlaskForm):

    name = StringField("Name Surname", validators=[Length(min=4, max=25)])
    username = StringField("Username", validators=[Length(min=5, max=35)])
    email = StringField("Email Address", validators=[Email(message="Please enter a valid email address")])
    password = PasswordField("Password", validators=[
        DataRequired(message="Please set a password"),
        EqualTo(fieldname="confirm", message="Your password does not match")
    ])
    confirm = PasswordField("Verify password")

class LoginForm(FlaskForm):
    username = StringField("Username")
    password = PasswordField("Password")

class CommentForm(FlaskForm):
    commentTitle = StringField("Comment Title")
    comment = TextAreaField("Comment")

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
@login_required #Check the decorator just before logging in, use this structure in all your logged in functions,
# In large structures, you check the session every time, you have to write a lot of if conditions, use decorator active.
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

@app.route('/profile/<username>')
@login_required
def profile(username):
    cursor = connection.cursor()
    query = "SELECT * FROM users WHERE username = %s"
    result = cursor.execute(query, (username,))
    if result > 0:
        user = cursor.fetchone()
        return render_template("profile.html", user=user)
    else:
        return render_template("profile.html")

@app.route('/profile/edit/username', methods = ["GET", "POST"])
@login_required
def edit_username(id):
    cursor = connection.cursor()
    if request.method == "POST":
        query = "UPDATE users SET "

@app.route("/register", methods=["GET", "POST"])
def register():
    try:
        form = RegisterForm(request.form)
        #print(form.validate(), form.errors) # If form.validate() is false, it also prints the error on the project to the screen.
        if request.method == "POST" and form.validate(): #form.validate returns True if all required conditions are met. It is checked whether there is a problem in the fields filled in the form.
            name = form.name.data #get the name information in the form
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt(form.password.data) #To save password information encrypted

            cursor = connection.cursor()
            query = "INSERT INTO users (name, email, username, password) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (name, email, username, password))
            connection.commit() #You do not need to use this when getting from the database.
            cursor.close() #To avoid using unnecessary resources in the background
            flash("You have successfully registered", "success") #message, category
            return redirect(url_for("login")) #To send to a certain page according to the function name, after registering, it comes to the login page.
        else:
            return render_template("register.html", form= form) #To send the form you created with RegisterForm, use form=form.
    except Exception as e:
        print(e)

#Login
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
        username =form.username.data
        password_entered = form.password.data
        cursor = connection.cursor()
        query = "SELECT * FROM users WHERE username = %s"
        result = cursor.execute(query, (username,)) #If it is a single element tuple, you must put "," next to it, otherwise it will not be detected as a tuple.

        if result > 0: #If there is a user with the entered username
            data = cursor.fetchone() # the entire row with username
            real_password = data["password"]
            session["id"] = data["id"]
            if sha256_crypt.verify(password_entered, real_password): #The user exists and the password is correct
                flash("You have successfully logged in", "success")
                session["logged_in"] = True  #Session control
                session["username"] = username

                return redirect(url_for("index"))

            else: #incorrect password
                flash("Password is incorrect", "danger")
                session["logged_in"] = False  # Session control
                return redirect(url_for("login"))

        else: #no users
            flash("There is no such user", "danger")
            session["logged_in"] = False  #Session control
            return redirect(url_for("login"))

        cursor.close()  #To avoid using unnecessary resources in the background
    return render_template("login.html", form=form)  #To send the form you created with LoginForm, use form=form

#Add Article
@app.route("/addarticle", methods=["GET", "POST"])
def addarticle():
    form = ArticleForm(request.form)
    if request.method == "POST" and form.validate():
        title = form.title.data
        content = form.content.data
        cursor = connection.cursor()
        query = "INSERT INTO articles(title, author, content) VALUES(%s, %s, %s)"
        cursor.execute(query, (title,session["username"], content))
        connection.commit()  # You do not need to use this when getting from the database.
        cursor.close()
        flash("Article Added Successfully", "success")
        return redirect(url_for("dashboard"))
    return render_template("addarticle.html", form =form)  #To send the form you created with LoginForm, use form=form

#Update Article
@app.route("/edit/<string:id>", methods = ["GET", "POST"])
@login_required #To check whether the user is logged in or not
def update(id):
    if request.method == "GET":
        cursor = connection.cursor()
        query = "SELECT * FROM articles WHERE id= %s AND author= %s"
        result = cursor.execute(query, (id, session["username"]))
        if result == 0: #If it is not an article belonging to the user or the article does not exist at all, result = 0
            flash("No such article exists or you are not authorized for this action", "danger")
            return redirect(url_for("index"))
        else:
            article = cursor.fetchone()
            form = ArticleForm()
            form.title.data = article["title"] #so that the update page is full of content
            form.content.data = article["content"] #so that the title is full on the update page
            return render_template("update.html", form=form)

    else: #POST REQUEST
        form = ArticleForm(request.form)
        newTitle = form.title.data #new posts
        newContent = form.content.data #new posts
        query2 = "UPDATE articles SET title = %s , content = %s WHERE id = %s"
        cursor = connection.cursor()
        cursor.execute(query2, (newTitle, newContent, id))
        connection.commit()
        flash("Article Updated Successfully", "success")
        return redirect(url_for("dashboard"))

#Delete Article
@app.route("/delete/<string:id>") #dynamic url
@login_required #To delete an article, you must first check if there is user login.
def delete(id):
    cursor = connection.cursor()
    query = "SELECT * FROM articles WHERE author = %s AND id = %s"
    result = cursor.execute(query, (session["username"],id))
    if result>0:
        query2 = "DELETE FROM articles WHERE id = %s"
        cursor.execute(query2, (id,))
        connection.commit() #If you are making a query where the sql table changes (CRUD)
        return redirect(url_for("dashboard"))
    else:
        flash("No such article exists or you are not authorized for this action", "danger")
        return redirect(url_for("index"))

#Article Form
class ArticleForm(FlaskForm):
    title = StringField("Article title", validators=[Length(min=5, max=100)]) #lineedit-like area, article title
    content = TextAreaField("Article Content", validators=[Length(min=10)]) #To create a larger area than lineedit, article content


#Detail Page
@app.route("/article/<string:id>", methods=["GET", "POST"])
def article(id):
    form = CommentForm(request.form)
    if request.method == "GET":
        cursor = connection.cursor()
        query = "SELECT * FROM articles WHERE id = %s"
        result = cursor.execute(query,(id,))
        if result>0:
            article = cursor.fetchone()
            query2 = "SELECT comments.*, users.name FROM comments INNER JOIN users ON comments.user = users.id WHERE comments.article_id = %s;"
            result2 = cursor.execute(query2, (id,))
            if result2>0:
                comments = cursor.fetchall()
                print(comments)
                cursor.close()
                return render_template("article.html", article = article, form=form, comments= comments)
            else:
                cursor.close()
                return render_template("article.html", article=article, form=form)
    else:
        cursor = connection.cursor()
        commentTitle = form.commentTitle.data
        comment = form.comment.data
        query3 = "INSERT INTO comments (user, article_id, comment, comment_title) VALUES (%s, %s, %s, %s)"
        cursor.execute(query3, (session["id"], id, comment, commentTitle))
        connection.commit()
        cursor.close()
        flash("Your comment has been added successfully", "success")  # message, category
        return redirect(url_for("article", id=id)) #PRG Pattern (POST-Redirect-GET). This pattern prevents problems that occur if the user hits their browser's reload button after submitting a form.
    return render_template("article.html")

#search URL
@app.route("/search", methods = ["GET", "POST"])
def search():
    if request.method == "GET":
        return redirect(url_for("index")) #Do not accept any get request, for example, if you type http://127.0.0.1:5000/search directly into the search, you will be directed to the starting page.
    else:
        keyword = request.form.get("keyword") #Written in input field = keyword
        cursor = connection.cursor()
        query = "SELECT * FROM articles WHERE title LIKE '%" + keyword + "%' " #To sort the keywords in the title, while doing a search
        result = cursor.execute(query)
        if result==0:
            flash("No article was found matching the search term.", "warning")
            return redirect(url_for("articles"))
        else:
            articles = cursor.fetchall()
            return render_template("articles.html", articles = articles)
            pass
# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)