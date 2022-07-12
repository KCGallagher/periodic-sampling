#
# Class for gibbs parameters
#

class Parameter:
    """Parameter object for Gibbs sampler.
    """

    def __init__(self, initial_value, conditional_posterior, posterior_params):
        """Constructor method of parameter object
        
        Parameters
        ----------
        initial_value : float
            The initial value of the parameter
        conditional_posterior : func
            Function object that returns random sample from known distribution
        posterior_params : func
            Function object that generates parameters for the conditional_
            posterior method - returns a dictionary
        """
        self.value = initial_value
        self.conditional_posterior = conditional_posterior
        self.posterior_params = posterior_params

    def __float__(self):
        """Overload float method to return value
        
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
        param_values = {k: float(v) for k, v in sample_params.items()}
        post_params = self.posterior_params(**param_values)
        self.value = self.conditional_posterior(**post_params)
        return self.value