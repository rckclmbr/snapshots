from snapshots import db

def _slugify(data):
    """ Super simple slugify, since we're restricting where it's used """
    return data.replace(" ", "-")

class Snapshot(db.Model):

    guid = db.Column(db.String(80), primary_key=True)
    status = db.Column(db.String(32))
    url = db.Column(db.String(1024))
    date = db.Column(db.DateTime(), server_default=db.text('CURRENT_TIMESTAMP'))

    def __init__(self, guid, url, status="INQUEUE"):
        self.guid = guid
        self.status = status
        self.url = url

    @classmethod
    def get_recent(cls):
        return cls.query.order_by(cls.date.desc()).limit(20)

    def short_url(self):
        if len(self.url) < 30:
            return self.url
        else:
            return self.url[:12] + "..." + self.url[-13:]

    def get_browser_snapshot(self, browser):
        for b in list(self.browser_snapshots):
            if browser == b.browser:
                return b

    def __repr__(self):
        return '<Snapshot %r>' % self.guid + self.short_url()

class BrowserSnapshot(db.Model):

    id = db.Column(db.Integer(80), primary_key=True)
    browser = db.Column(db.String(32))
    status = db.Column(db.String(32)) # INQUEUE INPROGRESS ERROR COMPLETE
    message = db.Column(db.String(1024))
    snapshot_guid = db.Column(None, db.ForeignKey("snapshot.guid"))
    snapshot = db.relationship(Snapshot, primaryjoin=(snapshot_guid==Snapshot.guid), backref=db.backref("browser_snapshots"), lazy="subquery")

    def __init__(self, browser, snapshot, status="INQUEUE", message=""):
        self.browser = browser
        self.status = status
        self.message = ""
        self.snapshot = snapshot

    def __repr__(self):
        return '<BrowserSnapshot %r>' % self.id

    def thumbnail_filename(self):
        return _slugify("static/t/%s/snapshot-%s-small.png" % (self.snapshot.guid, self.browser))

    def filename(self):
        return _slugify("static/t/%s/snapshot-%s.png" % (self.snapshot.guid, self.browser))

    def thumbnail_url(self):
        return _slugify("/static/t/%s/snapshot-%s-small.png" % (self.snapshot.guid, self.browser))

    def image_url(self):
        return _slugify("/static/t/%s/snapshot-%s.png" % (self.snapshot.guid, self.browser))

    def is_displayable(self):
        return self.status == "COMPLETE"

    def status_human(self):
        s = dict(
            INQUEUE="In Queue",
            INPROGRESS="In Progress",
            ERROR="Error",
            COMPLETE="Complete"
        )
        return s.get(self.status, "None")
