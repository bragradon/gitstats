class Author(object):
    def __init__(self, name):
        self.name = name
        self.commits = 0
        self.place_by_commits = 0
        self.lines_added = 0
        self.lines_removed = 0
        self.first_commit_stamp = 0
        self.last_commit_stamp = 0
        self.first_active_day = 0
        self.last_active_day = 0
        self.active_days = set()
        self.commits_frac = 0
        self.date_first = 0
        self.date_last = 0
        self.timedelta = 0
