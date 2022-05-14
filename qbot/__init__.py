from qbot.interpreter import executeFile, executeTxt

__version__ = "0.0.1"

def main():
    from qbot.cli import setupParsers
    args = setupParsers()
    args.func(args)

