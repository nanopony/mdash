rutypograph
===========

Типограф, основанный на правилах от Евгения Муравьева. Начало было форком типографа mdash, чей питоновский код (который был по сути crude портом php-шного) был переписал в виде классов и определений без eval.

Usage
-----
```python
from rutypograph import Typograph
e = Typograph()
source = '- Это типограф?\n- Да ,это он....'
print(e.process(source))
```

Result:
```
&mdash;&nbsp;Это типограф?
&mdash;&nbsp;Да, это он&hellip;
```

License
-------

The MIT License (MIT)
Copyright (c) 2016 nanopony

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#### mdash 

Public Domain
Evgeny Muravjev Typograph, http://mdash.ru
Authors: Evgeny Muravjev & Alexander Drutsa  
EMT - Evgeny Muravjev Typograph

h2. Why so fork?

