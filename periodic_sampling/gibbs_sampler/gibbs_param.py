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