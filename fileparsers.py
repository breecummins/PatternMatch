# The MIT License (MIT)

# Copyright (c) 2015 Breschine Cummins

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import json

def parsePatterns(fname="patterns.txt"):
    f=open(fname,'r')
    maxmin=[]
    varnames=[]
    originalpatterns=[]
    for l in f:
        if l[-1]=='\n':
            l=l[:-1]
        originalpatterns.append(l)
        L=l.replace(',',' ').split()
        varnames.append(L[::2])
        maxmin.append(L[1::2])
    return varnames, maxmin, originalpatterns

def parseJSONFormat(fname='dsgrn_output.json'):
    parsed = json.load(open(fname),strict=False)
    varnames = [ x[0] for x in parsed["network"] ]
    threshnames = [ [parsed["network"][i][2][j] for j in parsed["parameter"][i][2]] for i in range(len(parsed["network"])) ]
    return varnames,threshnames,parsed["graph"],parsed["cells"]

