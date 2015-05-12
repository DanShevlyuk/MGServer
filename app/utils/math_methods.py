import numpy

def xlogx(x):
    x = numpy.asarray(x)
    l = numpy.zeros_like(x)
    l[x > 0] = numpy.log(x[x > 0])
    return x * l


def entropy(Ps):
    Ps = numpy.asarray(Ps)
    print "Ps sum: %s" % sum(Ps)
    Ps /= sum(Ps)
    Ps[numpy.isnan(Ps)] = 0
    return -sum(xlogx(Ps))  # /log(2), but that is a constant


def bayes(P_X_given_Y, P_Y, P_X):
    """Given P(X|Y), P(Y) and P(X), calculate P(Y|X)."""
    P_X_given_Y = numpy.asarray(P_X_given_Y)
    P_Y = numpy.asarray(P_Y)
    P_X = numpy.asarray(P_X)
    y = P_Y.view().reshape((1, -1))
    x = P_X.view().reshape((-1, 1))
    xy = P_X_given_Y.view().reshape((-1, y.shape[1]))
    yx = ((xy * y) / x).transpose()
    yx[numpy.isnan(yx)] = 0
    yx.shape = (P_Y.shape + P_X.shape)
    return yx


def entropy_after_answer(self, P_QA, P_XQA):
    # There might be a more transparent formula.
    # Use .sum(axes=) instead of sum(.transpose) ?
    return sum((P_QA * self.entropy(P_XQA)).transpose())