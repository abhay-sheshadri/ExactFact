from flask import Flask, request, jsonify, render_template, flash, redirect, url_for, session
from flask_cors import CORS
from flask_bcrypt import Bcrypt

import json
from datetime import date

with open("config.json", "r") as f:
    config = json.load(f)

from app.parsing.parser import parse_into_sentences, Misinformation
from app.database.utils import get_similar_misinformation, load_structures, trees, construct_trees_from_database
from app.website.forms import RegistrationForm, LoginForm, PostForm, CommentForm
from app.website.db import conn, open_database, add_user_to_database, get_user_info, add_post_to_database, get_post_from_id, set_post, get_all_posts

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
bcrypt = Bcrypt(app)

app.config["SECRET_KEY"] = 'd49af5cebe80eb62333ff9b8639825c2'


@app.route("/api", methods=["POST"])
def api():
    """
    Endpoint for the factchecking api
    """
    # If the ANN trees are not loaded in, load them in
    if trees == None:
        load_structures()
    # Parse the innerText for sentences and encode them
    article_arr = request.get_json()
    sentences = []
    for article in article_arr:
        sentences += parse_into_sentences(article)
    # Return result
    res = []
    for sentence in sentences:
        search = get_similar_misinformation(sentence)
        if len(search) > 0:
            res.append({
                "sentence": str(sentence),
                "results": search
            })
    return jsonify(res)


@app.route("/")
def homepage():
    return render_template("home.html", logged="user" in session)


@app.route("/posts")
def posts():
    if "user" in session:
        if not conn:
            open_database()
        user = session["user"]
        posts = get_all_posts()
        return render_template("posts.html", posts=posts, logged=True)
    return redirect(url_for("signin"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if "user" in session:
        return redirect(url_for("homepage"))
    # Open database in thread
    if not conn:
        open_database()
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        add_user_to_database(form.username.data, form.email.data, hashed)
        flash("Account created for {}. You can now sign in!".format(form.username.data), "success")
        return redirect(url_for("signin"))
    return render_template("signup.html", form=form, logged="user" in session)


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if "user" in session:
        return redirect(url_for("homepage"))
    # Open database in thread
    if not conn:
        open_database()
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user_info(form.email.data)
        if user and bcrypt.check_password_hash(user[2], form.password.data):
            session['user'] = user
            return redirect(url_for("homepage"))
        else:
            flash("Login Unsuccessful. Please check email and password.", "danger")
    return render_template("signin.html", form=form, logged="user" in session)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("homepage"))


@app.route("/posts/new", methods=["GET", "POST"])
def new_post():
    if not "user" in session:
        return redirect(url_for("signin"))
    if not conn:
        open_database()
    form = PostForm()
    if form.validate_on_submit():
        post = {
            "poster": session["user"][0],
            "date": date.today().strftime("%b-%d-%Y"),
            "title": form.title.data,
            "misinfo": form.misinfo.data,
            "link": form.link.data,
            "info": form.info.data,
            "additional": form.additional.data,
            "agree": 0,
            "disagree": 0,
            "comments": []
        }
        add_post_to_database(post)
        flash("Your post has been created!", "success")
        return redirect(url_for("posts")) 
    return render_template("createpost.html", form=form, logged=True)


@app.route("/posts/view/<post_id>", methods=["GET", "POST"])
def view_post(post_id):
    if not "user" in session:
        return redirect(url_for("signin"))
    if not conn:
        open_database()
    post = get_post_from_id(int(post_id))
    form = CommentForm()
    if form.validate_on_submit():
        # Checks if the user has already commented on this post before
        already = False
        for comment in post["comments"]:
            if session["user"][0] == comment["username"]:
                already = True
                break
        # Post comment if not already posted
        if not already:
            post["comments"].append({
                "username": session["user"][0],
                "select": form.select.data,
                "content": form.content.data
            })
            post[form.select.data.lower()] += 1
            set_post(int(post_id), post)
            flash("Your comment has been posted!", "success")
        else:
            flash("You have already commented!", "danger")
    return render_template("post.html", post=post, form=form, current_post_id=int(post_id), logged=True)


@app.route("/posts/add/<post_id>")
def add_to_database(post_id):
    if not "user" in session:
        return redirect(url_for("signin"))
    if session["user"][0] != "admin":
        flash("Sorry, you do not have permission to perform this action", "danger")
    else:
        if not conn:
            open_database()
        post = get_post_from_id(int(post_id))
        Misinformation(post['misinfo'], post["link"], post["info"])
        construct_trees_from_database()
        flash("Added to post information to misinformation database", "success")
    return redirect(url_for("homepage"))    
