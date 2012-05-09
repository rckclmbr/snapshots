from flask import Flask, request, render_template, redirect, url_for, request
from flask_celery import Celery
from flask_sqlalchemy import SQLAlchemy
from worker import make_screenshot, make_thumbnail, combine_images
import tempfile
import shutil
import uuid

def create_app():
    return Flask("snapshots")

app = create_app()
app.config.from_pyfile('config.py')
celery = Celery(app)
db = SQLAlchemy(app)

from models import Snapshot, BrowserSnapshot
db.create_all()

@celery.task(name="snapshots.make_screenshot")
def mk_screenshot(args):
    guid, browser = args
    snapshot = db.session.query(Snapshot).get(guid)
    browser_snapshot = snapshot.get_browser_snapshot(browser)
    try:
        url = snapshot.url
        filename = browser_snapshot.filename()
        thumbnail = browser_snapshot.thumbnail_filename()
        print "GUID: %s" % guid
        browser_snapshot.status = "INPROGRESS"
        db.session.commit()
        res = make_screenshot(url, filename, browser)
        make_thumbnail(filename, thumbnail)
        snapshot = db.session.query(Snapshot).get(guid)
        browser_snapshot.status = "COMPLETE"
        db.session.commit()
        return res, guid
    except Exception, e:
        print e
        browser_snapshot.status = "ERROR"
        browser_snapshot.message = str(e)
        db.session.commit()

@app.route("/result/<guid>/")
def snapshot_result(guid):
    snapshot = db.session.query(Snapshot).get(guid)
    return render_template("snapshot_result.html", snapshot=snapshot, recent=Snapshot.get_recent())

DEFAULT_BROWSERS = ["firefox", "internetexplorer 7", "chrome", "internetexplorer 7"]

@app.route("/submit/", methods=["POST"])
def submit():
    url = request.form.get("url")
    browsers = request.form.getlist("browsers")

    if not url:
        raise Exception("You must provide a url")

    if not browsers:
        browsers = DEFAULT_BROWSERS

    guid = str(uuid.uuid4())
    snapshot = Snapshot(guid=guid, url=url)
    db.session.add(snapshot)
    db.session.add_all([BrowserSnapshot(browser, snapshot, status="INQUEUE", message="") for browser in browsers])
    db.session.commit()

    for b in snapshot.browser_snapshots:
        ret = mk_screenshot.delay((guid, b.browser))
    return redirect(url_for("snapshot_result", guid=guid))


@app.route("/")
def home():
    return render_template("index.html", recent=Snapshot.get_recent())

#@app.route("/result/<guid>")
#def show_result(task_id):
#    retval, guid = mk_screenshot.AsyncResult(task_id).get(timeout=0.5)
#    return "/"+retval

if __name__ == "__main__":
    app.run(debug=True)
