import re
from builtins import super

from gitstats.RunExternal import RunExternal
from gitstats.collector.StatisticsCollector.StatisticsCollectorStrategy import StatisticsCollectorStrategy
from gitstats.model.Author import Author


class AuthorStrategy(StatisticsCollectorStrategy):
    def __init__(self, data, conf):
        super().__init__(data, conf)

    def collect(self):
        # defined for stamp, author only if author committed at this timestamp.
        self.data.changes_by_date_by_author = {}  # stamp -> author -> lines_added
        
        if self.conf.ignore_msg_regex:
            ignore_msg_filter = '--grep="%s" --invert-grep' % self.conf.ignore_msg_regex
        else:
            ignore_msg_filter = ''
        
        # Similar to the above, but never use --first-parent
        # (we need to walk through every commit to know who
        # committed what, not just through mainline)
        lines = RunExternal.execute([
            'git log --ignore-submodules -w --shortstat --date-order --pretty=format:"%%H %%at %%aN" %s %s' % (
                ignore_msg_filter,
                self.get_log_range('HEAD')
            )
        ]).split('\n')
        
        #reverse the lines so we find the added/removed data before the author
        lines.reverse()
        
        inserted = 0
        deleted = 0
        stamp = 0
        
        for line in lines:
            if len(line) == 0:
                continue

            if re.search(r'files? changed', line) is not None:
                numbers = self.get_stat_summary_counts(line)
    
                if len(numbers) == 3:
                    (files, inserted, deleted) = [int(el) for el in numbers]
                else:
                    print('Warning: failed to handle line "%s"' % line)
                    (files, inserted, deleted) = (0, 0, 0)
            else:
                # <sha> <stamp> <author>
                parts = line.split(' ')
                if len(parts) >= 3:
                    try:
                        old_stamp = stamp
                        sha = parts[0]
                        stamp = int(parts[1])
                        author_name = ' '.join(parts[2:])
                        if sha not in self.conf.ignored_shas:
                            author_name = self.get_merged_author(author_name)
                            if old_stamp > stamp:
                                # clock skew, keep old timestamp to avoid having ugly graph
                                stamp = old_stamp
                            if author_name not in self.data.authors.keys():
                                self.data.authors[author_name] = Author(author_name)
                            author = self.data.authors[author_name]
                            self.data.add_commit(author, stamp, inserted+deleted)
                            author.lines_added += inserted
                            author.lines_removed += deleted
                            author_changes_for_date = self.data.changes_by_date_by_author.setdefault(stamp, {}).setdefault(author, {})
                            # Cumulative?
                            author_changes_for_date['lines_added'] = author.lines_added
                            author_changes_for_date['lines_changed'] = author.lines_added + author.lines_removed
                            author_changes_for_date['commits'] = author.commits
                        
                        # Reset the stats in case there's no modifications before the next commit
                        # is encountered.
                        files, inserted, deleted = 0, 0, 0
                    except ValueError:
                        print('Warning: unexpected line "%s"' % line)
                else:
                    print('Warning: unexpected line "%s"' % line)

