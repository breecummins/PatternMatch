import itertools
import walllabels as wl
import preprocess as pp

def recursePattern(currentwall,match,matches,patterns,pDict):
    # THIS FUNCTION USES MEMORY INSTEAD OF CPU; walllabels_previous and walllabels_current are 
    # different indexings of the same list. dict algorithm has only one memory structure, but
    # is currently slower for the size of problems that we have.
    lastwall=match[-1]
    if len(patterns)==0:
        if pDict['stop'] in pDict['walllabels_current'][lastwall] and ((pDict['cyclic'] and match[0]==lastwall) or not pDict['cyclic']): 
            matches.append(tuple(match))
        return matches
    else:
        extremum,intermediate = patterns[0]
        for k,t in enumerate(pDict['triples'][lastwall]):
            if t[1] == currentwall:
                labels=pDict['walllabels_previous'][lastwall][k]
                if extremum in labels: # if we hit the next pattern element, reduce pattern by one
                    matches=recursePattern(t[2],match+[t[1]],matches,patterns[1:],pDict)
                if intermediate in labels: # if we hit an intermediate node, keep the same pattern
                    matches=recursePattern(t[2],match+[t[1]],matches,patterns,pDict)
        return matches

def recursePattern_firstmatchonly(currentwall,match,patterns,pDict):
    # Throwing an error is a hacky kludge. I haven't been able to figure out how to fix it.
    lastwall=match[-1]
    if len(patterns)==0:
        if pDict['stop'] in pDict['walllabels_current'][lastwall] and ((pDict['cyclic'] and match[0]==lastwall) or not pDict['cyclic']): 
            raise ValueError(str([tuple(match)]))
        else:
            return []
    else:
        extremum,intermediate = patterns[0]
        for k,t in enumerate(pDict['triples'][lastwall]):
            if t[1] == currentwall:
                labels=pDict['walllabels_previous'][lastwall][k]
                if extremum in labels: # if we hit the next pattern element, reduce pattern by one
                    recursePattern_firstmatchonly(t[2],match+[t[1]],patterns[1:],pDict)
                if intermediate in labels: # if we hit an intermediate node, keep the same pattern
                    recursePattern_firstmatchonly(t[2],match+[t[1]],patterns,pDict)
        return []

def matchPattern(pattern,paramDict,cyclic=1,findallmatches=1):
    '''
    This function finds paths in a directed graph that are consistent with a target pattern. The nodes
    of the directed graph are called walls, and each node is associated with a wall label (in walldomains)
    and a wall number (the index of the label in walldomains). The outgoing edges of a node with wall
    number w are stored in outedges at index w. Each element of outedges is a collection of wall numbers. 

    The pattern is a sequence of words from the alphabet ('u','d','m','M'), with each word containing EXACTLY
    one 'm' or 'M'. The variable locations in walldomains will be transformed in a path-dependent manner into 
    words of the same type that have AT MOST one 'm' or 'M'. There can be at most one 'm' 
    or 'M' at each wall because we assume that the input graph arises from a switching network where each 
    regulation event occurs at a unique threshold. The paths in the graph that have word labels that 
    match the pattern will be returned as sequences of wall numbers. Intermediate wall labels may be inserted 
    into the pattern as long as they do not have an 'm' or 'M' in the label, and are consistent with the next 
    word in the pattern. Example: 'uMdd' in a four dimensional system means that the first variable is 
    increasing (up), the second variable is at a maximum (Max), and the third and fourth variables are 
    decreasing (down). The character 'm' means a variable is at a minimum (min). If the words 'uMdd' then 'udmd'
    appear in a pattern, the intermediate node 'uddd' may be inserted between these two in a match.

    The following variables are produced by functions in the module preprocess in. See the code for more information.

    pattern: list of uniform-length words from the alphabet ('u','d','m','M'); exactly one 'm' or 'M' REQUIRED per string
    paramDict keywords:
        triples: list of tuples (previouswall,currentwall,nextwall) allowable from graph
        walllabels_current: list of lists of uniform-length words from the alphabet ('u','d','m','M') with at most one of 
            ['m','M'] in each word describing the possible wall labels at currentwall
        walllabels_previous: walllabels_current re-indexed according to previouswall

    cyclic=1 means only cyclic paths are sought. cyclic=0 means acyclic paths are acceptable.

    findallmatches=1 means that a list of matches will be returned. If findallmatches=0, the search aborts after finding and returning a single match.

    See functions beginning with "call" below for example calls of this function.

    '''
    # check for empty patterns
    if not pattern:
        return "None. Pattern is empty."
    # check if any word in pattern is not a wall label (it's pointless to search in that case)
    flatlabels = [a for l in paramDict['walllabels_current'] for a in l]
    if not set(pattern).issubset(flatlabels):
        return "None. No results found. Pattern contains an element that is not a wall label."
    # find all possible starting nodes for a matching path
    startwallpairs=wl.getFirstAndNextWalls(pattern[0],paramDict['triples'],paramDict['walllabels_previous'])
    firstwalls,nextwalls=zip(*startwallpairs)
    # return trivial length one patterns
    if len(pattern)==1:
        return firstwalls
    # pre-cache intermediate nodes that may exist in the wall graph
    intermediatenodes=[p.replace('m','d').replace('M','u')  if set(p).intersection(['m','M']) else '' for p in pattern[1:]] 
    patternParams = zip(pattern[1:],intermediatenodes)
    # record stopping criterion
    paramDict['stop'] = pattern[-1]
    paramDict['cyclic'] = cyclic
    # find matches
    if findallmatches:
        results=[]
        for w,n in startwallpairs:
            matches = recursePattern(n,[w],[],patternParams,paramDict) # seek match starting with w, n
            results.extend(matches) 
        # paths not guaranteed unique so use set()
        return list(set(results)) or "None. No results found."
    else:
        for w,n in startwallpairs:
            try:
                match = recursePattern_firstmatchonly(n,[w],patternParams,paramDict) # seek match starting with w, n
            except ValueError as v:
                match=eval(v.args[0])
            if match:
                break
        return match or "None. No results found."


def callPatternMatch(fname='dsgrn_output.json',pname='patterns.txt',rname='results.txt',cyclic=1,findallmatches=1, printtoscreen=0,writetofile=1):
    # output printed to screen
    print "Preprocessing..."
    patterns,paramDict=pp.preprocess(fname,pname,cyclic) 
    print "Searching..."
    if writetofile: f=open(rname,'w',0)
    for pattern in patterns:
        matches=matchPattern(pattern,paramDict,cyclic=cyclic,findallmatches=findallmatches)
        if printtoscreen:
            print "\n"
            print '-'*25
            print "Pattern: {}".format(pattern)
            print "Results: {}".format(matches)
            print '-'*25
        if writetofile and 'None' not in matches:
            f.write("Pattern: {}".format(pattern)+'\n')
            f.write("Results: {}".format(matches)+'\n')
    if writetofile: f.close()
