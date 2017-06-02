import datetime
import time


class Data(object):
    def __init__(self):
        self.stamp_created = time.time()
        self.cache = {}

        self.project_name = None

        self.activity_by_hour_of_day = {}  # hour -> commits
        self.activity_by_day_of_week = {}  # day -> commits
        self.activity_by_month_of_year = {}  # month [1-12] -> commits
        self.activity_by_hour_of_week = {}  # weekday -> hour -> commits
        self.activity_by_hour_of_day_busiest = 0
        self.activity_by_hour_of_week_busiest = 0
        self.activity_by_year_week = {}  # yy_wNN -> commits
        self.activity_by_year_week_peak = 0

        # name
        self.authors = {}

        self.total_commits = 0
        self.total_files = 0
        self.authors_by_commits = 0

        # domains
        self.domains = {}

        # author of the month
        self.months = set()
        self.years = set()
        self.lines_added_by_month = {}  # month -> lines added
        self.lines_added_by_year = {}  # year -> lines added
        self.lines_removed_by_month = {}  # month -> lines removed
        self.lines_removed_by_year = {}  # year -> lines removed
        self.first_commit_stamp = 0
        self.last_commit_stamp = 0
        self.last_active_day = None
        self.active_days = set()

        # lines
        self.total_lines = 0
        self.total_lines_added = 0
        self.total_lines_removed = 0

        # size
        self.total_size = 0

        # timezone
        self.commits_by_timezone = {}  # timezone -> commits

        # tags
        self.tags = {}

        self.files_by_stamp = {}  # stamp -> files

        # extensions
        self.extensions = {}  # extension -> files, lines

        # line statistics
        self.changes_by_date = {}  # stamp -> { files, ins, del }
        
        # fame statistics
        self.current_line_owners = {
            'total' : 0,
            'authors' : {},
        }

    def get_activity_by_day_of_week(self):
        return self.activity_by_day_of_week

    def get_activity_by_hour_of_day(self):
        return self.activity_by_hour_of_day

    def get_active_days(self):
        return self.active_days

    ##
    # Get a list of authors
    def get_authors(self, limit=None):
        res = self.get_authors_sorted_by_commits(reverse=True)
        return res[:limit]

    def get_authors_of_month(self, yy_mm, top=None):
        result = []
        for author in self.authors.values():
            if yy_mm in author.lines_by_month.keys():
                result.append(author)
        result = sorted(result, key=lambda k: k.lines_by_month[yy_mm], reverse=True)
        if top:
            result = result[:top]
        return result

    def get_total_commits_by_month(self, yy_mm):
        authors = self.get_authors_of_month(yy_mm)
        total_commits = 0
        for author in authors:
            total_commits += author.commits_by_month[yy_mm]
        return total_commits
    
    def get_total_lines_by_month(self, yy_mm):
        authors = self.get_authors_of_month(yy_mm)
        total_lines = 0
        for author in authors:
            total_lines += author.lines_by_month[yy_mm]
        return total_lines
    
    def get_authors_of_year(self, year, top=None):
        result = []
        for author in self.authors.values():
            if year in author.lines_by_year.keys():
                result.append(author)
        result = sorted(result, key=lambda k: k.lines_by_year[year], reverse=True)
        if top:
            result = result[:top]
        return result

    def get_total_commits_by_year(self, year):
        authors = self.get_authors_of_year(year)
        total_commits = 0
        for author in authors:
            total_commits += author.commits_by_year[year]
        return total_commits
    
    def get_total_lines_by_year(self, year):
        authors = self.get_authors_of_year(year)
        total_lines = 0
        for author in authors:
            total_lines += author.lines_by_year[year]
        return total_lines

    def get_first_commit_date(self):
        return datetime.datetime.fromtimestamp(self.first_commit_stamp)

    def get_last_commit_date(self):
        return datetime.datetime.fromtimestamp(self.last_commit_stamp)

    def get_commit_delta_days(self):
        return (self.last_commit_stamp / 86400 - self.first_commit_stamp / 86400) + 1

    def get_stamp_created(self):
        return self.stamp_created

    def get_tags(self):
        return list(self.tags.keys()).sort()

    def get_total_authors(self):
        return len(self.authors)

    def get_total_commits(self):
        return self.total_commits

    def get_total_files(self):
        return self.total_files

    def get_total_loc(self):
        return self.total_lines

    def get_total_size(self):
        return self.total_size

    def get_authors_sorted_by_commits(self, reverse=False):
        return sorted(self.authors.values(), key=lambda k: k.commits, reverse=reverse)

    def get_domains_sorted_by_commits(self, reverse=False):
        return sorted(self.domains.values(), key=lambda k: k.commits, reverse=reverse)

    @staticmethod
    def get_keys_sorted_by_values(d):
        return [el[1] for el in sorted([(el[1], el[0]) for el in list(d.items())])]

    def add_commit(self, author, stamp, num_lines):
        date = datetime.datetime.fromtimestamp(float(stamp))
        yy_mm = date.strftime('%Y-%m')
        yy = date.year

        self.months.add(yy_mm)
        self.years.add(yy)
        author.add_commit(yy_mm, yy, num_lines)
