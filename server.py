"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, jsonify, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

import decimal

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

BERATEMENT_MESSAGES = [
    "I suppose you don't have such bad taste after all.",
    "I regret every decision that I've ever made that has " +
    "brought me to listen to your opinion.",
    "Words fail me, as your taste in movies has clearly " +
    "failed you.",
    "That movie is great. For a clown to watch. Idiot.",
    "Words cannot express the awfulness of your taste."
    ]


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

    user_id = session.get('user_id')

    # Get average rating of movie

    rating_scores = [r.score for r in movie_object.ratings]
    avg_rating = float(sum(rating_scores)) / len(rating_scores)

    prediction = None

    if user_id:
        user_rating = Rating.query.filter_by(
            movie_id=movie_id, user_id=user_id).first()

    else:
        user_rating = None

    if (not user_rating) and user_id:
        user = User.query.get(user_id)
        if user:
            prediction = user.predict_rating(movie_object)

    # Either use the prediction or their real rating

    if prediction:
        # User hasn't scored; use our prediction if we made one
        effective_rating = prediction

    elif user_rating:
        # User has already scored for real; use that
        effective_rating = user_rating.score

    else:
        # User hasn't scored, and we couldn't get a prediction
        effective_rating = None

    # Get the eye's rating, either by predicting or using real rating

    the_eye = (User.query.filter_by(email="eye@judgeyou.com")
                         .one())
    eye_rating = Rating.query.filter_by(
        user_id=the_eye.user_id, movie_id=movie_object.movie_id).first()

    if eye_rating is None:
        eye_rating = the_eye.predict_rating(movie_object)

    else:
        eye_rating = eye_rating.score

    if eye_rating and effective_rating:
        difference = abs(eye_rating - effective_rating)

    else:
        # We couldn't get an eye rating, so we'll skip difference
        difference = None
        print 'hello'

    if difference is not None:
        beratement = BERATEMENT_MESSAGES[int(difference)]
        print beratement

    else:
        beratement = None

    for rating_object in rating_objects:
        user_object = User.query.filter_by(user_id=rating_object.user_id).one()
        movie_ratings[user_object.user_id] = {'score': rating_object.score,
                                              'username': user_object.email}

    return render_template("movie_info.html",
                           movie=movie_object,
                           user_rating=user_rating,
                           average=avg_rating,
                           prediction=prediction,
                           beratement=beratement,
                           eye_rating=eye_rating,
                           movie_ratings=movie_ratings)


@app.route("/movies/<movie_id>", methods=['POST'])
def process_rating(movie_id):

    score = request.form.get('score')

    user_id = session.get('user_id')

    rating_object = Rating.query.filter_by(user_id=user_id).filter_by(movie_id=int(movie_id)).first()
    if rating_object is None:
        rating_object = Rating(movie_id=int(movie_id),
                               user_id=user_id,
                               score=score)
        db.session.add(rating_object)

    else:
        rating_object.score = score

    db.session.commit()
    return redirect("/movies/" + movie_id)


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
        del session['logged_in']
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
