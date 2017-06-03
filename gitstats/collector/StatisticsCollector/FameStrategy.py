import re
from builtins import super

from gitstats.RunExternal import RunExternal
from gitstats.collector.StatisticsCollector.StatisticsCollectorStrategy import \
    StatisticsCollectorStrategy


class FameStrategy(StatisticsCollectorStrategy):
    def __init__(self, data, conf):
        super().__init__(data, conf)
    
    def _add_to_stats(self, author, file_name):
        stats = self.data.current_line_owners
        stats['total'] += 1
        try:
            author_stats = stats['authors'][author]
        except KeyError:
            author_stats = stats['authors'][author] = {'total' : 0, 'files' : {}}
        author_stats['total'] += 1
        author_stats['files'][file_name] = author_stats['files'].get(file_name, 0) + 1
    
    def collect(self):
        self.data.current_line_owners = {
            'total' : 0,
            'authors' : {},
        }

        lines = RunExternal.execute([
            'git ls-files',
            r'''sed -e 's/\(.*\)/"\1"/' ''',
            'xargs -n1 git blame -w -C --line-porcelain'
        ]).split('\n')
        
        while lines:
            hash_line = lines.pop(0)
            
            # Author
            author_line = lines.pop(0)
            if not author_line.startswith('author '):
                raise Exception('Not Author: %s' % author_line)
            author_name = author_line[7:].strip()

            author_name = self.get_merged_author(author_name)
            
            author_mail_line = lines.pop(0)
            author_time_line = lines.pop(0)
            author_tz_line = lines.pop(0)
    
            # Committer
            committer_line = lines.pop(0)
            committer_mail_line = lines.pop(0)
            committer_time_line = lines.pop(0)
            committer_tz_line = lines.pop(0)
    
            # Misc
            summary_line = lines.pop(0)
            previous_file_name_line = lines.pop(0)
            if previous_file_name_line.startswith('boundary'):
                previous_file_name_line = lines.pop(0)
    
            if previous_file_name_line.startswith('previous'):  # previous is optional
                file_name_line = lines.pop(0)  # file_name
            else:
                file_name_line = previous_file_name_line
            file_name = file_name_line[9:].strip()
    
            line_content = lines.pop(0).strip()
            if line_content:
                self._add_to_stats(author_name, file_name)

