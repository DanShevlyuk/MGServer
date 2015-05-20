import numpy


def xlogx(x):
    x = numpy.asarray(x)
    l = numpy.zeros_like(x)
    l[x > 0] = numpy.log(x[x > 0])
    return x * l

def entropy(Ps):
    Ps = numpy.asarray(Ps)
    Ps /= sum(Ps)
    Ps[numpy.isnan(Ps)] = 0
    return -sum(xlogx(Ps))  # /log(3) - constant

def entropy_after_answer(P_QA, P_XQA):
    pQA = numpy.array(P_QA.values())
    pXQA = []
    for q in P_XQA.itervalues():
        next_stuff = numpy.array(q.values())
        pXQA = numpy.append(pXQA, next_stuff)

    return sum((pQA * entropy(pXQA)).transpose())