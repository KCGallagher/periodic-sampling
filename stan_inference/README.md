# Stan Inference

This folder contains stan scripts to conduct inference on epidemiological case data with a periodic weekly bias. Each directory contains a different model, based on different noise assumptions.

## [`Fixed Bias`](fixed_bias)

The simplest model is based on a deterministic reporting formulation, where all stochasticity is contained within the renewal model and the reporting bias scales the time series values linearly. This script also assumes a constant, known reproduction number, so that only the reporting biases are inferred.

## [`Time-Varying R`](time_varying_R)

This formulation is subsequently extended to infer an unknown, time-varying reproduction number, again with deterministic reporting so that the reproduction number at each timestep is inferred alongside the reporting biases. Again, the ground truth time series is calculated from the biased time series and the inferred reporting biases, and so is not inferred separately.

## [`Full Model`](full_model)

We introduce poisson noise in the reporting process, so that it is no longer stochastic and the time series data must be inferred separately. The bias values are formulated as a scaled simplex with a dirichlet prior, to constrain the sum of the bias values so case numbers are conserved across the reporting process.
