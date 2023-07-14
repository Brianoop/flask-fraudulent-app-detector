from flask import (
    current_app,
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    session,
)
from flask_login import login_required, current_user
from .models import (
    MobileApplication,
    User,
    MobileApplicationReview,
    MobileApplicationLike,
    MobileApplicationRating,
)
from . import db
from werkzeug.security import (
    generate_password_hash,
)
from werkzeug.utils import secure_filename
import os
import string
import random
from sqlalchemy.orm import aliased
from sqlalchemy import func
import nltk

nltk.download("vader_lexicon")
from nltk.sentiment.vader import SentimentIntensityAnalyzer


def simple_sentiment_analysis(review):
    sid = SentimentIntensityAnalyzer()
    score = ((sid.polarity_scores(str(review))))["compound"]
    return score


# ML STUFF


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


routes = Blueprint("routes", __name__)


# query on all our Mobile Application data
@routes.route("/dashboard")
@login_required
def Index():
    total_users = (
        db.session.query(func.count(User.id))
        # .filter_by(mobile_application_id=mobile_app.id)
        .scalar()
    )
    total_apps = (
        db.session.query(func.count(MobileApplication.id))
        # .filter_by(mobile_application_id=mobile_app.id)
        .scalar()
    )
    total_reviews = (
        db.session.query(func.count(MobileApplicationReview.id))
        # .filter_by(mobile_application_id=mobile_app.id)
        .scalar()
    )
    total_ratings = (
        db.session.query(func.count(MobileApplicationRating.id))
        # .filter_by(mobile_application_id=mobile_app.id)
        .scalar()
    )
    return render_template(
        "dashboard/home.html",
        total_users=total_users,
        total_apps=total_apps,
        total_reviews=total_reviews,
        total_ratings=total_ratings,
    )


# this route is for inserting data to mysql database via html forms
@routes.route("/insert", methods=["POST"])
@login_required
def insert():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]

        mobile_application = MobileApplication.query.filter_by(
            name=name
        ).first()  # if this returns an app, then the app already exists in database

        if "logo" not in request.files:
            flash("You must chose an app logo!", "danger")
            return redirect(url_for("routes.ManageApps"))
        logo = request.files["logo"]

        file_name = secure_filename(logo.filename)

        unique_name = id_generator() + "_" + file_name

        path = os.path.join(current_app.config["UPLOAD_PATH"], unique_name)

        logo.save(path)

        logo_path = current_app.config["UPLOAD_FOLDER"] + "/" + unique_name

        if (
            mobile_application
        ):  # if a user is found, we want to redirect back to signup page so user can try again
            flash("App name already exists!", "danger")
            return redirect(url_for("routes.ManageApps"))

        my_new_mobile_application = MobileApplication(
            name=name, description=description, logo_path=logo_path
        )
        db.session.add(my_new_mobile_application)
        db.session.commit()

        flash("Mobile Application Inserted Successfully!", "success")

        return redirect(url_for("routes.ManageApps"))


# this is our update route where we are going to update our Mobile Application
@routes.route("/update", methods=["GET", "POST"])
@login_required
def update():
    if request.method == "POST":
        my_data = MobileApplication.query.get(request.form.get("id"))
        my_data.name = request.form["name"]
        my_data.description = request.form["description"]

        db.session.commit()
        flash("Mobile Application Updated Successfully!", "success")

        return redirect(url_for("routes.ManageApps"))


# This route is for deleting our Mobile Application
@routes.route("/delete/<id>/", methods=["GET", "POST"])
@login_required
def delete(id):
    my_mobile_application = MobileApplication.query.get(id)
    db.session.delete(my_mobile_application)
    db.session.commit()
    flash("Mobile Application Deleted Successfully!", "success")

    return redirect(url_for("routes.ManageApps"))


# query on all our Mobile Application data
@routes.route("/manage-apps")
@login_required
def ManageApps():
    page = request.args.get("page", 1, type=int)
    pagination = MobileApplication.query.order_by(MobileApplication.id).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template("dashboard/manage_apps.html", pagination=pagination)


####### USER LOGIC START


@routes.route("/manage-users")
@login_required
def ManageUsers():
    page = request.args.get("page", 1, type=int)
    pagination = User.query.order_by(User.id).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template("dashboard/manage_users.html", pagination=pagination)


# this route is for inserting data to mysql database via html forms
@routes.route("/insert-user", methods=["POST"])
@login_required
def insert_user():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        role = request.form["role"]
        password = request.form["password"]

        user = User.query.filter_by(
            email=email
        ).first()  # if this returns a user, then the email already exists in database

        if (
            user
        ):  # if a user is found, we want to redirect back to signup page so user can try again
            flash("Email is taken!", "danger")
            return redirect(url_for("routes.ManageUsers"))

        new_user = User(
            email=email,
            name=name,
            role=role,
            password=generate_password_hash(password, method="sha256"),
        )

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        flash("User Created Successfully!", "success")

        return redirect(url_for("routes.ManageUsers"))


# this is our update route where we are going to update our User
@routes.route("/update-user", methods=["GET", "POST"])
@login_required
def update_user():
    if request.method == "POST":
        my_data = User.query.get(request.form.get("id"))
        my_data.name = request.form["name"]
        my_data.email = request.form["email"]
        my_data.role = request.form["role"]

        db.session.commit()
        flash("User Updated Successfully!", "success")

        return redirect(url_for("routes.ManageUsers"))


# This route is for deleting our User
@routes.route("/delete-user/<id>/", methods=["GET", "POST"])
@login_required
def delete_user(id):
    my_user_data = User.query.get(id)
    if my_user_data.email == session["user_email"]:
        flash("Deleting own account not allowed!", "danger")
        return redirect(url_for("routes.ManageUsers"))
    db.session.delete(my_user_data)
    db.session.commit()
    flash("User Deleted Successfully!", "success")
    return redirect(url_for("routes.ManageUsers"))


# query on all our Mobile Application data
@routes.route("/see-apps")
@login_required
def SeeApps():
    page = request.args.get("page", 1, type=int)
    pagination = MobileApplication.query.order_by(MobileApplication.id).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template("dashboard/see_apps.html", pagination=pagination)


@routes.route("/insert-review", methods=["POST"])
@login_required
def insert_mobile_application_review():
    if request.method == "POST":
        app_id = request.form["id"]
        user_id = request.form["user_id"]
        review = request.form["review"]
        score = simple_sentiment_analysis(review)
        if score > 0:
            label = "positive"
        elif score == 0:
            label = "neutral"
        else:
            label = "negative"
        # label = analyse_review(review)

        # if label == "negative_of_fraud":
        #   score = 70
        # if label == "positive_of_fraud":
        #    score = 70

        my_data = MobileApplicationReview(
            user_id=user_id,
            mobile_application_id=app_id,
            text=review,
            sentiment=label,
            sentiment_ratio=score,
        )
        db.session.add(my_data)
        db.session.commit()

        flash(
            "Your review was saved successfully! "
            + "Score: "
            + str(score)
            + ", Label: "
            + label,
            "success",
        )

        # return redirect(url_for("routes.SeeApps"))
        return redirect(request.referrer or "/dashboard")


@routes.route("/insert-like", methods=["POST"])
@login_required
def insert_mobile_application_like():
    if request.method == "POST":
        app_id = request.form["id"]
        user_id = request.form["user_id"]

        mobile_application_like = MobileApplicationLike.query.filter_by(
            user_id=user_id, mobile_application_id=app_id
        ).first()

        if (
            mobile_application_like
        ):  # if a user is found, we want to redirect back to signup page so user can try again
            db.session.delete(mobile_application_like)
            db.session.commit()
            flash("You unliked the app 😌!", "info")
            # return redirect(url_for("routes.SeeApps"))
            return redirect(request.referrer or "/dashboard")

        my_data = MobileApplicationLike(
            user_id=user_id,
            mobile_application_id=app_id,
        )
        db.session.add(my_data)
        db.session.commit()

        flash("Your like was saved successfully 🤩!", "success")

        # return redirect(url_for("routes.SeeApps"))
        return redirect(request.referrer or "/dashboard")


@routes.route("/insert-rating", methods=["POST"])
@login_required
def insert_mobile_application_rating():
    if request.method == "POST":
        app_id = request.form["id"]
        user_id = request.form["user_id"]
        rating_out_of_five = request.form["rating_out_of_five"]

        mobile_application_rating = MobileApplicationRating.query.filter_by(
            user_id=user_id, mobile_application_id=app_id
        ).first()

        if mobile_application_rating:
            mobile_application_rating.rating_out_of_five = rating_out_of_five
            db.session.commit()
            flash("Your app rating is saved successfully!", "info")
            # return redirect(url_for("routes.SeeApps"))
            return redirect(request.referrer or "/dashboard")

        my_data = MobileApplicationRating(
            user_id=user_id,
            mobile_application_id=app_id,
            rating_out_of_five=rating_out_of_five,
        )
        db.session.add(my_data)
        db.session.commit()

        flash("Your rating was saved successfully!", "success")

        # return redirect(url_for("routes.SeeApps"))
        return redirect(request.referrer or "/dashboard")


# This route is for loading mobile app details
@routes.route("/app-detail", methods=["GET", "POST"])
@login_required
def show_app_detail():
    id = request.args.get("id")
    page = request.args.get("page", 1, type=int)

    mobile_app = MobileApplication.query.get(id)

    user = aliased(User)
    mobile_application_review = aliased(MobileApplicationReview)

    pagination = (
        db.session.query(user, mobile_application_review)
        .join(mobile_application_review, user.id == mobile_application_review.user_id)
        .filter_by(mobile_application_id=mobile_app.id)
        .order_by(mobile_application_review.id.desc())
        .paginate(page=page, per_page=10, error_out=False)
    )

    avg_rating = (
        db.session.query(
            func.coalesce(
                func.round(func.avg(MobileApplicationRating.rating_out_of_five), 1), 0.0
            )
        )
        .filter_by(mobile_application_id=mobile_app.id)
        .scalar()
    )

    total_likes = (
        db.session.query(func.count(MobileApplicationLike.id))
        .filter_by(mobile_application_id=mobile_app.id)
        .scalar()
    )

    total_positive_reviews  = (
        db.session.query(func.count(MobileApplicationReview.id))
        .filter_by(mobile_application_id=mobile_app.id)
        .filter_by(sentiment="positive")
        .scalar()
    )

    total_negative_reviews  = (
        db.session.query(func.count(MobileApplicationReview.id))
        .filter_by(mobile_application_id=mobile_app.id)
        .filter_by(sentiment="negative")
        .scalar()
    )

    total_neutral_reviews  = (
        db.session.query(func.count(MobileApplicationReview.id))
        .filter_by(mobile_application_id=mobile_app.id)
        .filter_by(sentiment="neutral")
        .scalar()
    )

    general_app_review = ""
    safe = False
    if(total_positive_reviews < total_negative_reviews):
        general_app_review = "This app is fraudulent!"
        safe = False
    else:
        general_app_review = "This app is safe"
        safe = True

    # for s, f in stmt:
    # print(f"{s.name} ({s.email}): {f.text}")

    return render_template(
        "dashboard/app_detail.html",
        mobile_app=mobile_app,
        pagination=pagination,
        # reviews=stmt,
        average_rating=avg_rating,
        total_likes=total_likes,
        total_negative_reviews=total_negative_reviews,
        total_neutral_reviews=total_neutral_reviews,
        total_positive_reviews=total_positive_reviews,
        general_app_review=general_app_review,
        safe=safe
    )


import re
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import numpy as np
import pickle


nltk.download("stopwords")


# CODE TO PERFORM SENTIMENT ANALYSIS
def analyse_review(review_text):
    sentiment_model_name = "my_logistic_regression_model.pickle"
    words_model_name = "words.pkl"

    model_path = os.path.join(current_app.config["MODEL_PATH"], sentiment_model_name)
    words_path = os.path.join(current_app.config["WORDS_PATH"], words_model_name)

    words = pickle.load(open(words_path, "rb"))
    model = pickle.load(open(model_path, "rb"))

    pstem = PorterStemmer()

    text = review_text
    text = re.sub("[^a-zA-Z]", " ", text)
    text = text.lower()
    text = text.split()
    text = [
        pstem.stem(word) for word in text if not word in set(stopwords.words("english"))
    ]
    text = " ".join(text)

    query = []
    for word in words:
        if word in text:
            query.append(1)
        else:
            query.append(0)

    prediction = list(model.predict(np.asarray(query).reshape(1, -1)))[0]

    msg = ""

    if prediction == 1:
        msg = "negative"
    else:
        msg = "positive"
    return msg
