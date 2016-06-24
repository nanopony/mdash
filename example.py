from lxml import html
import logging

from rutypograph import Typograph

if __name__ == '__main__':

    e = Typograph()
    with open('./cases/test1.txt', 'r') as r:
        source = r.read()

    with open('./cases/test1.html', 'w') as w:
        w.write(e.process(source))


