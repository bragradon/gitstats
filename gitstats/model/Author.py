import datetime
from collections import defaultdict


class Author(object):
    def __init__(self, name):
        self.name = name
        self.commits = 0
        self.commits_by_month = defaultdict(lambda: 0)
        self.commits_by_year = defaultdict(lambda: 0)
        self.lines_by_month = defaultdict(lambda: 0)
        self.lines_by_year = defaultdict(lambda: 0)
        self.lines_added = 0
        self.lines_removed = 0
        self.first_commit_stamp = 0
        self.last_commit_stamp = 0
        self.first_active_day = 0
        self.last_active_day = 0
        self.active_days = set()

    def __str__(self):
        return self.name

    def add_commit(self, yy_mm, yy, num_lines):
        self.commits += 1
        self.commits_by_month[yy_mm] += 1
        self.commits_by_year[yy] += 1
        self.lines_by_month[yy_mm] += num_lines
        self.lines_by_year[yy] += num_lines

    def get_date_first(self):
        return datetime.datetime.fromtimestamp(self.first_commit_stamp)

    def get_date_first_string(self, date_format):
        return self.get_date_first().strftime(date_format)

    def get_date_last(self):
        return datetime.datetime.fromtimestamp(self.last_commit_stamp)

    def get_date_last_string(self, date_format):
        return self.get_date_last().strftime(date_format)

    def get_commits_frac(self, total_commits):
        return (100 * float(self.commits)) / total_commits

    def get_time_delta(self):
        return self.get_date_last() - self.get_date_first()
