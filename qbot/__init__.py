import os
import argparse
import qbot.interpreter as executeFile

__version__ = "0.0.1"

#modified version of help formatter which only prints args once in help message
class ArgsOnce(argparse.HelpFormatter):
    def __init__(self,prog):
        super().__init__(prog,max_help_position=40)

    def _format_action_invocation(self, action):
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
            return metavar
        else:
            parts = []

            if action.nargs == 0:
                parts.extend(action.option_strings)

            else:
                default = action.dest.upper()
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    parts.append('%s' % option_string)
                parts[-1] += ' %s'%args_string
            return ', '.join(parts)

def getFilePath(file):
    if os.path.isabs(file):
        return file

    cwd = os.getcwd()
    file = file.strip('/')
    return f"{cwd}/{file}"

def setupParsers():
    description = (
        "an esoteric language for analysis quamtum algorithms using the quantum circuit model and probabilistic computing.\n" \
        "paradigms: quantum, probabilistic, imperative, interpreted"
    )

    parser = argparse.ArgumentParser(description=description,formatter_class=ArgsOnce)
    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('file', type=str, help='the path to the file to execute (relative or absolute)')
    parser.set_defaults(func = lambda args: baseHandler(args, parser))

    args = parser.parse_args()
    return args

def baseHandler(args,_):
    filePath = getFilePath(args.FILE)
    if not os.path.exists(filePath):
        print(f"File Not Found at Path: \n{filePath}")
    executeFile(open(filePath, 'r'))
    #parser.print_help()


def main():
    args = setupParsers()
    args.func(args)

