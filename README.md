rutypograph
===========
Инструмент для предпубликационной обработки текста для веба.

Типограф, основанный на правилах от Евгения Муравьева. Начало было форком типографа mdash, чей питоновский код (который был по сути crude портом php-шного) был переписан в виде классов и определений без eval.

Тесты проходят не все, так как не все правила переписаны.


Usage
-----
```python
from rutypograph import Typograph, get_default_environment

settings = get_default_environment()
settings.convert_html_entities_to_unicode = True
print(Typograph.process("- Это \"типограф? \"Вторые кавычки\"\"\n- Да, это он...."))

settings.convert_html_entities_to_unicode = False
print(Typograph.process("- Это \"типограф? \"Вторые кавычки\"\"\n- Да, это он...."))

```

Result in unicode:
```
— Это «типограф? „Вторые кавычки“»
— Да, это он…
```
Result in HTML Enitites:
```
&mdash;&nbsp;Это &laquo;типограф? &bdquo;Вторые кавычки&ldquo;&raquo;
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

