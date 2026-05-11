from . import config


def convertToBase(s: str):
    symbol = 0
    d = {}
    for x in s:
        if x not in d.keys():
            d[x] = symbol
            symbol += 1
    return "".join([str(d[x]) for x in s])

def jump_from_to(x:int,y:int):
# how many steps (clockwise or anticlockwise) from x to y?
    if x <= y:
        return y-x if y-x < config.BASE-(y-x) else -(config.BASE-(y-x))
    else:
        return -(x-y) if x-y < config.BASE-(x-y) else config.BASE-(x-y)

def remove_duplicates(l):
    return [i for n, i in enumerate(l) if i not in l[:n]]

def substrings(s:str):
    return remove_duplicates((sorted([s[i: j] for i in range(len(s)) for j in range(i + 1, len(s) + 1)],key=len)))

# def chunks(s:str):
#     output = []
#     i = 0
#     while i<len(s):
#         j = i+1
#         while j<len(s) and s[j]==s[i]:
#             j+=1
#         output += [(i,j)]
#         i = j
#     return(output)

# def valid_range(i,j,chunks):
#     return(len([ (a,b) for (a,b) in chunks if i<=a and b<=j])>0)

def chunks_in_order(s:str):
    output = []
    i = 0
    while i<len(s):
        j = i+1
        while j<len(s) and s[j]==s[i]:
            j+=1
        output += [(i,j)]
        i = j
    # cannot remove duplicates here! Because of the inner working of the dictionary in the presence of chunks
    return ([s[a:b] for (a,b) in output])

def concatenation_of_chunks(s):
    chunks = chunks_in_order(s)
    result = []
    for i in range(len(chunks)):
        current_concatenation = ""
        for j in range(i, len(chunks)):
            current_concatenation += chunks[j]+"+"
            result.append(current_concatenation)

    def count_concat(word):
        return word.count('+')

    result = sorted(result, key=count_concat, reverse=False)
    result = [x.replace('+', '') for x in result]
    # cannot remove duplicates here! Because of the inner working of the dictionary in the presence of chunks
    return result
