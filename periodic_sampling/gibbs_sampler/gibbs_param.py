#
# Class for gibbs parameters
#

class Parameter:
    """Parameter object for Gibbs sampler.
    """

    def __init__(self, initial_value, conditional_posterior, posterior_params = None):
        """Constructor method of parameter object.
        
        Parameters
        ----------
        initial_value : float
            The initial value of the parameter
        conditional_posterior : func
            Function object that returns random sample from known distribution
        posterior_params : func
            Function object that generates parameters for the conditional_
            posterior method - returns a dictionary. Optional - if not specified,
            the params dict will be fed directly into the conditional posterior
        """
        self.value = initial_value
        self.conditional_posterior = conditional_posterior
        self.posterior_params = posterior_params

    def __str__(self) -> str:
        """String representation of object.
        
        Returns
        -------
        str
            Description of Parameter object
        """
        return (f"Parameter of value {self.value}, with {self.conditional_posterior.__name__} conditional posterior")

    def __float__(self) -> float:
        """Overload float method to return value.
        
        Returns
        -------
        float
            Current value of the parameter
        """
        return float(self.value)

    def __add__(self, other):
        """Overload addition method.
        
        Returns
        -------
        float
            Sum of both arguments, using values for Parameter instances
        """
        if isinstance(other, Parameter):
            return self.value + other.value
        else:
            return self.value + other

    def __radd__(self, other):
        """Overload addition method, reversed arguments (i.e. for
        other + self)
        
        Returns
        -------
        float
            Sum of both arguments, using values for Parameter instances
        """
        return self + other  # Result is commutative

    def __sub__(self, other):
        """Overload subtraction method.
        
        Returns
        -------
        float
            Difference of both arguments, using values for Parameter instances
        """
        if isinstance(other, Parameter):
            return self.value - other.value
        else:
            return self.value - other

    def __rsub__(self, other):
        """Overload subtraction method, reversed arguments (i.e. for
        other + self)
        
        Returns
        -------
        float
            Difference of both arguments, using values for Parameter instances
        """
        return - (self - other)  # Result is anticommutative

    def __mul__(self, other):
        """Overload multiplication method.
        
        Returns
        -------
        float
            Product of both arguments, using values for Parameter instances
        """
        if isinstance(other, Parameter):
            return self.value * other.value
        else:
            return self.value * other

    def __rmul__(self, other):
        """Overload multiplication method, reversed arguments (i.e. for
        other * self)
        
        Returns
        -------
        float
            Product of both arguments, using values for Parameter instances
        """
        return self * other  # Result is commutative

    def __pow__(self, other):
        """Overload power method.
        
        Returns
        -------
        float
            self**other, using values for Parameter instances
        """
        if isinstance(other, Parameter):
            return self.value ** other.value
        else:
            return self.value ** other

    def __rpow__(self, other):
        """Overload power method with Parameter instance in exponent.
        
        Returns
        -------
        float
            other**self, using values for Parameter instances
        """
        if isinstance(other, Parameter):
            return other.value ** self.value
        else:
            return other ** self.value

    def sample(self, sample_params):
        """Samples from the conditional posterior distribution.
        
        Parameters
        ----------
        sample_params : dict
            Dictionary of the all current parameter values, required
            to generate the shape of the posterior distribution.

        Returns
        -------
        float
            Value of parameter sampled from conditional posterior
        """
        if self.posterior_params is None:
            # Can directly feed params into conditional_posterior
            post_params = sample_params
        else:
            param_values = {}
            for k, v in sample_params.items():
                try:
                    param_values[k] = float(v)
                except TypeError:  # For non float params (such as arrays)
                    if isinstance(v, Parameter):
                        param_values[k] = v.value
                    else:
                        param_values[k] = v
            post_params = self.posterior_params(**param_values)
        self.value = self.conditional_posterior(**post_params)
        return self.value

from numpy.random import gamma

params = {
    'lambda_1': Parameter(3.0, gamma, lambda a, b, x, n, **kwargs: {'shape':a + sum(x[:int(float(n)+1)]), 'scale':(b+float(n))}),
    'lambda_2': Parameter(4, gamma, lambda a, b, x, n, **kwargs: {'shape':a + sum(x[int(float(n)+1):]), 'scale':(b+len(x)-float(n))}),
}

print(float(params['lambda_1']) - 2)
print(params['lambda_1'] - 2)
print(2 - params['lambda_1'])
print(params['lambda_1'] - params['lambda_2'])
