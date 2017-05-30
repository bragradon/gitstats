import datetime

from gitstats.RunExternal import RunExternal
from gitstats.collector.StatisticsCollector.StatisticsCollectorStrategy import StatisticsCollectorStrategy
from gitstats.model.Author import Author
from gitstats.model.Domain import Domain
from builtins import super


class RevisionStrategy(StatisticsCollectorStrategy):
    def __init__(self, data, conf):
        super().__init__(data, conf)

    def collect(self):
        # Outputs "<stamp> <date> <time> <timezone> <author> '<' <mail> '>'"
        lines = RunExternal.execute(
            ['git rev-list --pretty=format:"%%at %%ai %%aN <%%aE>" %s' % self.get_log_range('HEAD'),
             'grep -v ^commit']).split('\n')
        for line in lines:
            parts = line.split(' ', 4)

            # First and last commit stamp (may be in any order because of cherry-picking and patches)
            stamp = self._collect_revision_stamps(parts)

            date = datetime.datetime.fromtimestamp(float(stamp))

            # activity
            # hour
            self._collect_activity_by_hour(date)

            # day of week
            self._collect_activity_by_day(date)

            # domain stats
            self._collect_domain_stats(parts)

            # hour of week
            self._collect_hour_of_week(date)

            # most active hour?
            self._collect_most_active_hour(date)

            # month of year
            self._collect_month(date)

            # yearly/weekly activity
            self._collect_weekly_yearly_activity(date)

            # author stats
            author = self._collect_author(parts)

            #  commits, note again that commits may be in any date order because of cherry-picking and patches
            self._collect_author_commits(author, stamp)

            # authors: active days
            self._collect_author_active_days(date, author)

            # project: active days
            self._collect_project_active_days(date)

            # timezone
            self._collect_timezone(parts)

    def _collect_revision_stamps(self, parts):
        try:
            stamp = int(parts[0])
        except ValueError:
            stamp = 0
        if stamp > self.data.last_commit_stamp:
            self.data.last_commit_stamp = stamp
        if self.data.first_commit_stamp == 0 or stamp < self.data.first_commit_stamp:
            self.data.first_commit_stamp = stamp
        return stamp

    def _collect_activity_by_hour(self, date):
        hour = date.hour
        self.data.activity_by_hour_of_day[hour] = self.data.activity_by_hour_of_day.get(hour, 0) + 1
        # most active hour?
        if self.data.activity_by_hour_of_day[hour] > self.data.activity_by_hour_of_day_busiest:
            self.data.activity_by_hour_of_day_busiest = self.data.activity_by_hour_of_day[hour]

    def _collect_activity_by_day(self, date):
        day = date.weekday()
        self.data.activity_by_day_of_week[day] = self.data.activity_by_day_of_week.get(day, 0) + 1

    def _collect_domain_stats(self, parts):
        mail = parts[4].split('<', 1)[1]
        mail = mail.rstrip('>')
        domain_name = '?'
        if mail.find('@') != -1:
            domain_name = mail.rsplit('@', 1)[1]
        if domain_name not in self.data.domains.keys():
            self.data.domains[domain_name] = Domain(domain_name)
        domain = self.data.domains[domain_name]
        domain.commits += 1

    def _collect_hour_of_week(self, date):
        day = date.weekday()
        hour = date.hour
        if day not in self.data.activity_by_hour_of_week:
            self.data.activity_by_hour_of_week[day] = {}
        self.data.activity_by_hour_of_week[day][hour] = self.data.activity_by_hour_of_week[day].get(hour, 0) + 1

    def _collect_most_active_hour(self, date):
        day = date.weekday()
        hour = date.hour
        if self.data.activity_by_hour_of_week[day][hour] > self.data.activity_by_hour_of_week_busiest:
            self.data.activity_by_hour_of_week_busiest = self.data.activity_by_hour_of_week[day][hour]

    def _collect_month(self, date):
        month = date.month
        self.data.activity_by_month_of_year[month] = self.data.activity_by_month_of_year.get(month, 0) + 1

    def _collect_weekly_yearly_activity(self, date):
        yyw = date.strftime('%Y-%W')
        self.data.activity_by_year_week[yyw] = self.data.activity_by_year_week.get(yyw, 0) + 1
        if self.data.activity_by_year_week_peak < self.data.activity_by_year_week[yyw]:
            self.data.activity_by_year_week_peak = self.data.activity_by_year_week[yyw]

    def _collect_author(self, parts):
        author_name = parts[4].split('<', 1)[0]
        author_name = author_name.rstrip()
        author_name = self.get_merged_author(author_name)
        if author_name not in self.data.authors.keys():
            self.data.authors[author_name] = Author(author_name)
        return self.data.authors[author_name]

    @staticmethod
    def _collect_author_commits(author, stamp):
        if stamp > author.last_commit_stamp:
            author.last_commit_stamp = stamp
        if author.first_commit_stamp == 0 or stamp < author.first_commit_stamp:
            author.first_commit_stamp = stamp

    def _collect_author_active_days(self, date, author):
        yy_mm_dd = date.strftime(self.conf.date_format)
        if yy_mm_dd != author.last_active_day:
            author.last_active_day = yy_mm_dd
            author.active_days.add(yy_mm_dd)

    def _collect_project_active_days(self, date):
        yy_mm_dd = date.strftime(self.conf.date_format)
        if yy_mm_dd != self.data.last_active_day:
            self.data.last_active_day = yy_mm_dd
            self.data.active_days.add(yy_mm_dd)

    def _collect_timezone(self, parts):
        timezone = parts[3]
        self.data.commits_by_timezone[timezone] = self.data.commits_by_timezone.get(timezone, 0) + 1
