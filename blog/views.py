import json
from . import app
from .database import session, Entry
from flask import request, redirect, url_for, render_template, flash
from flask.ext.login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from .database import User


PAGINATE_BY = 10

@app.route("/")
@app.route("/page/<int:page>")
def entries(page=1):
    # Zero-indexed page
    page_index = page - 1

    count = session.query(Entry).count()

    start = page_index * PAGINATE_BY
    end = start + PAGINATE_BY

    total_pages = (count - 1) // PAGINATE_BY + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    entries = session.query(Entry)
    entries = entries.order_by(Entry.datetime.desc())
    entries = entries[start:end]

    return render_template("entries.html",
        entries=entries,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages,
        current_user=current_user
    )
    
@app.route("/entry/add", methods=["GET"])
@login_required
def add_entry_get():
    return render_template("add_entry.html")
    

@app.route("/entry/add", methods=["POST"])
@login_required
def add_entry_post():
    title = request.form["title"]
    content = request.form["content"]
    
    if title == "" or content == "":
        # messages in a session that tell the user on the website to fill out the fields
        return redirect(url_for("add_entry_post"))
    else:
        entry = Entry(
            title=title,
            content=content,
            author=current_user
        )
        session.add(entry)
        session.commit()
        return redirect(url_for("entries"))
    

@app.route("/entry/<id>", methods=["GET"]) 
def entry_id_get(id):
    # get one entry by its id
    # hint: use queries, session.
    entry = session.query(Entry).get(id)
    return render_template("entry.html", 
        entry=entry
    ) 
    
@app.route("/entry/<id>/edit", methods=["GET"])
@login_required
def edit_entry_get(id):
    entry = session.query(Entry).get(id)
    if entry: 
        return render_template("edit_entry.html",
    entry=entry
    )
    else: 
        return redirect(url_for("entries")
        )
    
@app.route("/entry/<id>/edit", methods=["POST"])
@login_required
def edit_entry_post(id):
    entry = session.query(Entry).get(id)
    entry.title = request.form["title"]
    entry.content = request.form["content"]
    session.commit()
    return redirect(url_for("entries")
    )
    
@app.route("/entry/<id>/delete", methods=["GET"])
@login_required
def delete_entry_get(id):
    entry = session.query(Entry).get(id)
    return render_template("entry.html", entry=entry)

@app.route("/entry/<id>/delete", methods=["DELETE"])  
@login_required
def delete_entry(id):
    entry = session.query(Entry).get(id)
    session.delete(entry)
    session.commit()
    # return redirect(url_for("entries#")) # sending back JSON!!!
    # is this person authorized to delete this or not?
    return json.dumps({'status': 200})
    
@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")
    
@app.route("/login", methods=["POST"])
def login_post():
    email = request.form["email"]
    password = request.form["password"]
    user = session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))

    login_user(user)
    return redirect(request.args.get('next') or url_for("entries"))
    
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("entries"))
    
    
    
