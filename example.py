from lxml import html
import logging

from rutypograph import Typograph

if __name__ == '__main__':
    # logging.basicConfig(level=logging.INFO)
    e = Typograph()

    with open('./cases/test1.txt', 'r') as r:
        source = r.read()
    print(e.process(source))

    with open('./cases/test2.txt', 'r') as r:
        source = r.read()
    print(e.process_html(source))
