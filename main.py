from crypt import methods
from flask import Flask, flash, redirect, render_template, request, session
import mysql.connector as mysql
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = "SECRETPASSWORDYIFVVIYUGYSVSRFV"
db = mysql.connect(host="localhost", user='root',passwd="obama", auth_plugin='mysql_native_password', db= "onlycoolers")
cursor = db.cursor()

@app.route("/")
def home():

    if "user" not in session:
        return redirect("/login")

    username = session['user']

    posts = []
    cursor.execute("select * from posts")
    for i in cursor:
        posts.append(i)

    for i in range(len(posts)):
        posts[i] = list(posts[i])
        un = posts[i][0]
        cursor.execute("select pfp_path from users where username='{}'".format(un))
        _pfp = cursor.fetchone()[0]
        posts[i].append(_pfp)

    print(posts)

    return render_template("home.html", posts=posts)





@app.route("/profile", methods= ["GET", "POST"])
def profile():

    if "user" not in session:
        return redirect("/login")

    
    username = session["user"]

    if request.method == "POST":
        file = request.files['img']
        if file:
            path = "./static/pfps/" + username + "." + file.filename.split(".")[1]

            file.save(path)
            cursor.execute("update users set pfp_path = '{}' where username= '{}'".format(path, username))
            db.commit()


    cursor.execute("select pfp_path from users where username= '{}'".format(username))

    pfp = cursor.fetchone()
    print(pfp)
    has_pfp = True

    if pfp[0] is None:
        has_pfp = False
    else:
        pfp = pfp[0]

    posts = []
    cursor.execute("select * from posts where username= '{}'".format(username))
    for i in cursor:
        posts.append(i)

    for i in range(len(posts)):
        posts[i] = list(posts[i])
        un = posts[i][0]
        cursor.execute("select pfp_path from users where username='{}'".format(un))
        _pfp = cursor.fetchone()[0]
        posts[i].append(_pfp)

    return render_template("profile.html", username= username, has_pfp= has_pfp, path=pfp, posts= posts, len= len)


@app.route("/post-img", methods=["POST"])
def post():

    username = session["user"]
    data = request.form

    cursor.execute("select * from users where username='{}'".format(username))
    user = cursor.fetchone()

    file = request.files['img']
    if file:
        num_posts = len(os.listdir("./static/posts"))

        path = "./static/posts/" + username + "_" + str(num_posts) + "." + file.filename.split(".")[1]

        file.save(path)

    
        cursor.execute("insert into posts values ('{}', '{}', '{}')".format(username, path, data["desc"]))

        db.commit()


    return redirect("/profile")


@app.route("/login", methods=["GET", "POST"])
def login():


    if "user" in session:
        return redirect("/")

    if request.method == "POST":
        data = request.form

        cursor.execute("select * from users where username = '{}'".format(data['username']))
        user = cursor.fetchone()
        
        if user is None:
            flash("User does not exist.")
            return redirect("/login")

        if data["pwd"] != user[1]:
            flash("Innocrect password.")
            return redirect("/login")

        session["user"] = data["username"]
        return redirect("/")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():

    if "user" in session:
        return redirect("/")

    if request.method == "POST":
        data = request.form
        
        cursor.execute("select * from users where username = '{}'".format(data['username']))

        if cursor.fetchone() is None:
            
            if len(data['pwd']) < 5:
                flash("Password must have more then 5 charecters.", "info")
                return redirect("/signup")

            try:
                cursor.execute("insert into users values ('{}', '{}', null)".format(data["username"], data["pwd"]))
                session["user"] = data["username"]
                db.commit()
                return redirect("/")

            except Exception as e:
                print(e)
                return "THERE WAS SOME ERROR TRY AGAIN LATER"

        else:
            flash("Account with that username aldredy exists.", "info")
            return redirect("/signup")

    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


@app.route("/delete-acc")
def delAcc():
    username = session['user']

    cursor.execute("delete from users where username= '{}'".format(username))
    cursor.execute("delete from posts where username= '{}'".format(username))
    db.commit()

    session.pop("user", None)

    return redirect("/login")



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

db.close()