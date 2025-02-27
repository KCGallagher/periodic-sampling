# Periodic Sampling

This folder contains methods to conduct inference on epidemiological case data with a periodic weekly bias. Each jupyter notebook contains a different model, based on different noise assumptions.

## Introductory Notebooks

### [`Data Trends`](data_trends.ipynb)

Using methods from the [analysis](analysis) folder, we characterise periodic trends in UK Covid-19 case and death data taken from the [John Hopkins Database](https://coronavirus.jhu.edu/about).

### [`Synthetic Data`](synthetic_data.ipynb)

This contains a guide to generating synthetic data based on methods in [`synthetic_data`](synthetic_data), applying periodic biases (with various noise spectra), and compares the reaulting synthetic bias to the biases observed in genuine data from the UK.

The biases are implemented through [biased reporters](synthetic_data/biased_reported.py), which have a number of possible noise spectra:
* **Unbiased Reporting** - No bias applied.
* **Daily Bias** - Scaling factor applied to each weekday.
* **Delayed Reporting** - Instead of rescaling the cases reported on each given day, distributes cases that occur on a given day to subsequent days according to a gamma distribution specific to each weekday.

For daily rescaling, there are four possible sub-methods, as documented in that [reporter](https://github.com/KCGallagher/periodic-sampling/blob/86ecaa72ddede59833d535042ea8d7e0d03bbe63/periodic_sampling/synthetic_data/biased_reporter.py#L63):
* **Scale** - Scales cases on a given day by a fixed value (the reporting factor).
* **Poisson** - Samples cases on a given day from a Poisson distribution, with a mean given by the true number of cases on that day scaled by the reporting factor for that day of the week.
* **Multinomial** - Redistributes cases within each week based on a random multinomical distribution, weighted by the reporting factors for each day.
* **Dirichlet** - Redistributes cases within each week based on a dirichlet distribution, weighted by the reporting factors for each day. This is guarenteed to preserve the true number of cases in a given week.

## Bayesian Inference

The overall framework for this, containing all custom posterior distributions, is contained within the [`periodic_model`](periodic_model.py) file. The framework (including multichain adaptations) is given in the [`inference_workflow`](inference_workflow.py), however we refer unfamiliar users to the notebooks below which will give a more complete introduction to the methods used.

### [`Constant R`](constant_R_sampler.ipynb)

The initial formalation is based on a constant, known reproduction number (R), so that only the time series and bias values (determining the reporting bias) need to be inferred. We observe good accuracy on the time series, but this is limited by the constant R value.

### [`Time-Varying R`](varying_Rt_sampler.ipynb)

This formulation is subsequently extended to infer an unknown, time-varying reproduction number, but struggles with a wide parameter space that doesn't constrain the problem to a unique solution.

### [`Fixed Bias`](fixed_bias_sampler.ipynb)

We therefore consider a deterministic reporting formulation, where all stochasticity is contained within the renewal model and the reporting bias scales the time series values linearly. However we observe compensatory divergence, whereby underreporting can be compensated by increased values of the reproduction number (and vise versa).

### [`Dirichlet Bias`](dirichlet_bias_sampler.ipynb)

To prevent this, a dirichlet prior is considered, to constrain the sum of the bias values so they cannot diverge. This notebook introduces the principal of this approach, but it is best implemented in Stan and so contained separately in [`stan_inference`](../stan_inference).
