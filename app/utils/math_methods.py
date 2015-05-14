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
    return -sum(xlogx(Ps))  # /log(2), but that is a constant

#
# def bayes(P_X_given_Y, P_Y, P_X):
#     """Given P(X|Y), P(Y) and P(X), calculate P(Y|X)."""
#     P_X_given_Y = numpy.asarray(P_X_given_Y)
#     P_Y = numpy.asarray(P_Y)
#     P_X = numpy.asarray(P_X)
#     y = P_Y.view().reshape((1, -1))
#     x = P_X.view().reshape((-1, 1))
#     xy = P_X_given_Y.view().reshape((-1, y.shape[1]))
#     yx = ((xy * y) / x).transpose()
#     yx[numpy.isnan(yx)] = 0
#     yx.shape = (P_Y.shape + P_X.shape)
#     return yx


def entropy_after_answer(P_QA, P_XQA):
    pQA = []

    for p in P_QA.values():
        pQA.append(p)

    pXQA = []
    for q in P_XQA.itervalues():
        next_stuff = []
        for p in q.itervalues():
            next_stuff.append(p)
        pXQA.append(next_stuff)

    return sum((numpy.array(pQA) * entropy(numpy.array(pXQA))).transpose())