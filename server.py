"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, jsonify, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from flask_sqlalchemy import SQLAlchemy
import sqlalchemy

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    # a = jsonify([1,3])
    return render_template("homepage.html")


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route("/users/<user_id>")
def show_user(user_id):

    user_object = User.query.filter_by(user_id=user_id).one()
    rating_objects = Rating.query.filter_by(user_id=user_id).all()
    movie_ratings = {}

    for rating_object in rating_objects:
        movie_object = Movie.query.filter_by(movie_id=rating_object.movie_id).one()
        movie_ratings[movie_object.movie_id] = {'score': rating_object.score,
                                                'title': movie_object.title}

    return render_template("user_info.html",
                           user=user_object,
                           movie_ratings=movie_ratings)


@app.route("/movies")
def movie_list():
    """Show list of movies."""

    movies = Movie.query.order_by(Movie.title).all()

    return render_template("movie_list.html", movies=movies)


@app.route("/movies/<movie_id>")
def show_movie(movie_id):

    movie_object = Movie.query.filter_by(movie_id=movie_id).one()
    rating_objects = Rating.query.filter_by(movie_id=movie_id).all()
    movie_ratings = {}

    for rating_object in rating_objects:
        user_object = User.query.filter_by(user_id=rating_object.user_id).one()
        movie_ratings[user_object.user_id] = {'score': rating_object.score,
                                              'username': user_object.email}

    return render_template("movie_info.html",
                           movie=movie_object,
                           movie_ratings=movie_ratings)


@app.route("/sign-in")
def sign_in_form():
    if session.get('logged_in') is True:
        flash('user already signed in')
        return redirect('/')
    else:
        return render_template("sign_in.html")


@app.route("/sign-in", methods=["POST"])
def sign_in_process():
    username = request.form.get('username')
    password = request.form.get('password')

    try:
        user_object = User.query.filter_by(email=username).one()
        if password == user_object.password:
            pass   # login -- for clairty in code
        else:
            flash("Wrong Password")
            return redirect('/sign-in')

    except sqlalchemy.orm.exc.NoResultFound:
        flash("Email not found, please try again or create a new account")
        return redirect('/sign-in')

    user_id = user_object.user_id
    session['user_id'] = user_id
    session['logged_in'] = True
    print(session)
    flash("Logged In")
    return redirect("/users/" + str(user_id))


@app.route("/register")
def register_form():

    if session.get('logged_in') is True:
        flash('user already signed in')
        return redirect('/')
    else:
        return render_template("register_form.html")


@app.route("/register", methods=["POST"])
def register_process():

    username = request.form.get('username')
    password = request.form.get('password')
    age = request.form.get('age')
    zipcode = request.form.get('zipcode')

    try:
        user_object = User.query.filter_by(email=username).one()
        flash('User already exists, please sign in or use another email')
        return redirect('/register')

    except sqlalchemy.orm.exc.NoResultFound:
        # flash('user created: %s') % (username)
        user_object = User(email=username,
                           password=password,
                           age=age,
                           zipcode=zipcode)

        # We need to add to the session or it won't ever be stored
        db.session.add(user_object)

        # Once we're done, we should commit our work
        db.session.commit()

    session['user_id'] = user_object.user_id
    session['logged_in'] = True
    print(session)
    flash("Logged In")
    return redirect("/")


@app.route('/logout')
def logout_process():
    if session.get('logged_in') is True:
        del session['user_id']
        flash('logged out')
    else:
        flash('not logged in')

    return redirect('/sign-in')




if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)


    
    app.run(port=5000, host='0.0.0.0')
