import os
import platform
import subprocess
import sys
import time
import six


class RunExternal(object):
    exec_time_external = 0.0

    @staticmethod
    def is_linux():
        return platform.system() == 'Linux'

    @staticmethod
    def execute(cmds, quiet=False):
        start = time.time()
        if not quiet and RunExternal.is_linux() and os.isatty(1):
            six.print_('>> ' + ' | '.join(cmds), end=' ')
            sys.stdout.flush()
        p = subprocess.Popen(cmds[0], stdout=subprocess.PIPE, shell=True)
        processes = [p]
        for x in cmds[1:]:
            p = subprocess.Popen(x, stdin=p.stdout, stdout=subprocess.PIPE, shell=True)
            processes.append(p)
        output = p.communicate()[0].decode('utf8')
        for p in processes:
            p.wait()
        end = time.time()
        if not quiet:
            if RunExternal.is_linux() and os.isatty(1):
                six.print_('\r', end=' ')
            print('[%.5f] >> %s' % (end - start, ' | '.join(cmds)))
        RunExternal.exec_time_external += (end - start)
        return output.rstrip('\n')
