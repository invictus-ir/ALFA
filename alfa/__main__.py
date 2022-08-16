import pandas as pd
from .cmdline import Parser
from .config import CONFIG_DIR

pd.set_option('display.max_colwidth', None)

with open(f'{CONFIG_DIR}/logo') as f:
    logo = f.read()

def main():
    print(logo)
    parser = Parser()
    args = parser.parser.parse_args()
    args.func(args)
    pass

if __name__ == '__main__':
    main()
