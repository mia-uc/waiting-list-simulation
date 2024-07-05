from scipy import stats


class RandomVar:
    def __init__(self, *dist_params):
        self.dist_params = dist_params
        self.factor = 1

    def __mul__(self, other):
        self.factor = other
        return self

    def __rmul__(self, other):
        self.factor = other
        return self

    def generate(self, *dist_params):
        return self.factor * self.__generate__(*dist_params)

    def __generate__(self, *dist_params):
        pass


class ExponentialRandomVar(RandomVar):
    """
    Stats Doc:
      A common parameterization for expon is in terms of the rate parameter lambda,
      such that pdf = lambda * exp(-lambda * x). This parameterization corresponds
      to using scale = 1 / lambda.
    """

    def __generate__(self):
        return stats.expon.rvs(*self.dist_params, size=1)[0]


class Chi2RandomVar(RandomVar):
    def __generate__(self):
        return stats.chi2.rvs(*self.dist_params, size=1)[0]


class UniformRandomVar(RandomVar):
    """
    Stats Doc:
      In the standard form, the distribution is uniform on [0, 1].
      Using the parameters loc and scale, one obtains the uniform
      distribution on [loc, loc + scale].
    """

    def __generate__(self):
        return stats.uniform.rvs(*self.dist_params, size=1)[0]


class LogNormRandomVar(RandomVar):
    """
    Stats Doc:
      Suppose a normally distributed random variable X has mean mu and standard
      deviation sigma. Then Y = exp(X) is lognormally distributed with
      s = sigma and scale = exp(mu).
    """

    def __generate__(self):
        return stats.lognorm.rvs(*self.dist_params, size=1)[0]


class MultiModalRandomVar(RandomVar):
    def __init__(self, weights):
        super().__init__()
        self.weights = weights
        self.selection_dist = stats.rv_discrete(
            values=(range(len(weights)), weights)
        )

    def __generate__(self):
        selected_index = self.selection_dist.rvs()

        return selected_index + 1


class ConstantRandomVar(RandomVar):
    def __init__(self, constant):
        super().__init__(constant)

    def __generate__(self):
        return self.dist_params[0]


class GeometricRandomVar(RandomVar):
    def __generate__(self, t):
        return 1 - stats.geom.cdf(t, self.dist_params[0])
