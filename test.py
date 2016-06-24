#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import sys
import re
import base64
import types
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from EMT import EMTypograph
import json

tests = json.loads(open('../tests/tests.json').read(100000000))

#main
def main():
    
    total = 0
    passed = 0
    for test in tests:
        EMT = EMTypograph()
        if test['title'] == 'Минус в диапозоне чисел':
            x = 1
        if 'params' in test:
            EMT.setup(test['params'])
        if test.get('safetags'):
            x = test.get('safetags')
            if isinstance(x, str):
                x = [x]
            for s in x:
                EMT.add_safe_tag(s)
        EMT.set_text(test['text'])
        
        passx = 0
        result = EMT.apply()
        if result == test['result']:
            r = "OK     "            
            passx += 1
        else:
            r = "FAIL   "
        print((r + test['title'] + '' ))
        if result != test['result']:
            print(("    GOT:   "+result + ''))
            print(("    NEED:  "+test['result'] + ''))
        
        del EMT
                
        total +=1
        if passx>=1:
            passed += 1
        
    print('Total tests : '+str(total))
    print('Passed tests: '+str(passed))
    print('Failed tests: '+str(total-passed))
    return

if __name__=="__main__":
    main()