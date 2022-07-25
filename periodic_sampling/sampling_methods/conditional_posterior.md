# Conditional Posteriors

## Delay Distribution Formulation

The latent process is that:

$$
I_{t} \sim Po \left(R_{t}\sum_{s=1}^{\infty} \omega_{s} I_{t-s} \right)
$$

where our observation of $I_{t}$ at some later time $t'$ is given by:

$$
I_{t, t'} \sim B(I_{t}, P_{t, t'})
$$

In other words the observed cases $C(t)$ at a given time count be written as $C_{t} = f(I_{1}, I_{2}, ..., I_{t}, a ,b)$ for some unknown function $f$, where $a$ and $b$ are the vectors giving the shape of the gama distribution for each day.

We could also write $P_{t, t'}$ (the probability of an event occurring at time $t$ being recorded at time $t'$) as $P_{w[t], \Delta t}$, where $w[t]$ determines the weekday index of the recording date, and $\Delta t = t' - t$ is the delay between the event occurance and recording.

We must require that:

$$
I_{t < t', t'} = \sum_{t < t'} I_{t, t'}
$$

i.e. the number of observed cases on a given day $t'$ from all prior days $t < t'$ is equal to the number of true cases from each prior day that were delayed until $t'$. Using the formulation above, it is equivalent to simply requiring $\Sigma C_{t} = \Sigma I_{t}$. While this seems trivial to describe, it is difficult to imagine how this condition might be included in the conditional posterior, beyond simply as a delta function.

The overall joint probability distribution (for the most recent true case value $I_{t}$ and weekday gamma distribution parameters $a_{w}, b_{w}$, based on observed case data $I_{t<t', t'}$, prior ground truth data $T_{<t}$ and time-dependant reproduction number $R_{t}$) may be written as:

$$
P (I_{t}, a_{w}. b_{w} | I_{t<t', t'}, T_{<t}, R_{t}) = \prod_{s=1}^{\infty} P(I_{s} | I_{<s}, R_{s}) \times \prod_{t'< t} B(I_{t', t} | I_{t}, P_{t', t}(a_{w}, b_{w})) \times P(a_{w}, b_{w}) \times \delta \left(I_{t < t', t'} - \sum_{t < t'} I_{t, t'} \right)
$$

However this is fairly intractable (primarily due to the $I_{t, t'}$ matrix), and so cannot easily be simplified into confitional posterior probabilities.

We could consider representing the observed cases $C_{t}$ as a Poisson process itself:

$$
C_{t} \sim Po \left(R\alpha_{w[t]} I_{t} \right)
$$

based on the weekday reporting rate $\alpha_{w[t]}$. We may then write the conditional posterior distributions as:

$$
P(C_{t}, I_{<t} | I_{t}, \alpha_{w[t]}) = P(C_{t} | I_{t}, \alpha_{w[t]}) \times P(I_{t} | I_{<t})
$$

$$
P(I_{t}, \alpha_{w[t]} | C_{t}, I_{<t}) \propto P(C_{t}, I_{t} | I_{<t}) \times P(\alpha_{w[t]} | C_{t})
$$

However this suffers from a similar issue of intractability without any obvious simplification through conjugate priors.

## Fixed Bias Formulation

We therefore adopt a similar approach, but with a different assumption on the periodic bias of the data - a fixed (scalar) bias.

The simplest form of this formulation is when $C_{t} = \alpha_{w[t]} I_{t}$ - i.e. the ground truth cases are scaled by some weekday-dependant scalar constant to give the observed cases. To generate sufficient noise in the periodicity of the observed (recorded) data however, we use $C_{t} \sim Po(\alpha_{w[t]} I_{t})$, while the true cases are still given by the renewal equation $I_{t} \sim Po(R_{t} \Lambda_{t})$.

The parameters are then updated in two steps. First $I_{t}$ is updated via Metropolis-Hastings according to the following conditional probability:

$$
P(I_{t} | C_{t}, \alpha_{i}, R_{t}) = \prod Po(I_{t} | R_{t} \Lambda_{t}) \times Po(C_{t} | \alpha_{i}I_{t})
$$

Secondly, $\alpha_{i}$ are updated using Gibbs sampling from the following conditional probability:

$$
P(\alpha_{i} | I_{t} , C_{t}) = \prod_{1, 8, 15, ...} Po(C_{t} | \alpha_{i} I_{t} ) \times Gamma(\alpha_{i} | a, b)
$$

summing over all days of that given weekday (monday indicies illustrated). This may be simplified to a single Gamma distribution using a known conditional prior relation (noting that the rates of the two processes differ by a scalar $I_{t}$ and so this is not quite equal to the standard relation). The prior of $\alpha_{i}$ is given by a Gamma distribution $Gamma(a, b)$.
