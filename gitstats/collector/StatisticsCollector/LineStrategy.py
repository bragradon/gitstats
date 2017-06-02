import datetime
import re
from builtins import super

from gitstats.RunExternal import RunExternal
from gitstats.collector.StatisticsCollector.StatisticsCollectorStrategy import StatisticsCollectorStrategy


class LineStrategy(StatisticsCollectorStrategy):
    def __init__(self, data, conf):
        super().__init__(data, conf)

    def collect(self):
        # outputs:
        #  N files changed, N insertions (+), N deletions(-)
        # <stamp> <author>
        self.data.changes_by_date = {}  # stamp -> { files, ins, del }
        # computation of lines of code by date is better done
        # on a linear history.
        
        if self.conf.ignore_msg_regex:
            ignore_msg_filter = '--grep="%s" --invert-grep' % self.conf.ignore_msg_regex
        else:
            ignore_msg_filter = ''
        
        extra = ''
        if self.conf.linear_line_stats:
            extra = '--first-parent -m'
        
        lines = RunExternal.execute([
            'git log --shortstat %s --pretty=format:"%%H %%at %%aN" %s %s' % (
                extra,
                ignore_msg_filter,
                self.get_log_range('HEAD')
            )
        ]).split('\n')

        # reverse the lines so we find the added/removed data before the author
        lines.reverse()
        
        files = 0
        inserted = 0
        deleted = 0
        total_lines = 0
        
        for line in lines:
            if len(line) == 0:
                continue

            line = str(line)

            if re.search('files? changed', line) is not None:
                numbers = self.get_stat_summary_counts(line)
    
                if len(numbers) == 3:
                    (files, inserted, deleted) = [int(el) for el in numbers]
                    total_lines += inserted
                    total_lines -= deleted
                    self.data.total_lines_added += inserted
                    self.data.total_lines_removed += deleted
    
                else:
                    print('Warning: failed to handle line "%s"' % line)
                    (files, inserted, deleted) = (0, 0, 0)
                    # self.data.changes_by_date[stamp] = { 'files': files, 'ins': inserted, 'del': deleted }
            else:
                # <sha> <stamp> <author>
                parts = line.split(' ')
                if len(parts) >= 3:
                    try:
                        sha = parts[0]
                        stamp = int(parts[1])
                        author_name = ' '.join(parts[2:])
                        if sha not in self.conf.ignored_shas:
                            self.data.changes_by_date[stamp] = {
                                'files': files,
                                'ins': inserted,
                                'del': deleted,
                                'lines': total_lines,
                            }
    
                            date = datetime.datetime.fromtimestamp(stamp)
                            yy_mm = date.strftime('%Y-%m')
                            self.data.lines_added_by_month[yy_mm] = self.data.lines_added_by_month.get(yy_mm, 0) + inserted
                            self.data.lines_removed_by_month[yy_mm] = self.data.lines_removed_by_month.get(yy_mm, 0) + deleted
    
                            yy = date.year
                            self.data.lines_added_by_year[yy] = self.data.lines_added_by_year.get(yy, 0) + inserted
                            self.data.lines_removed_by_year[yy] = self.data.lines_removed_by_year.get(yy, 0) + deleted

                        # Reset the stats in case there's no modifications before the next commit
                        # is encountered.
                        files, inserted, deleted = 0, 0, 0
                    except ValueError:
                        print('Warning: unexpected line "%s"' % line)
                else:
                    print('Warning: unexpected line "%s"' % line)
         
        self.data.total_lines += total_lines
