//
// Model with a stochastic reporting bias based on a dirichlet prior,
// therefore requiring inference of the timeseries as well as an
// unknown, time-varying Rt value
// Includes a time to death delay based on a gamma dist
//

functions {
    int min_of_int_pair(int value_1, int value_2) {
        if (value_1 < value_2)
            return value_1;
        else {
            return value_2;
        }
    }
    real calculate_lambda(vector alpha, array[] real I, vector omega, int max_t) {
            if (max_t == 1)
                return I[1];
            int n_terms_lambda = min_of_int_pair(max_t, size(omega) - 1);  // Number of terms in sum for lambda

            vector[size(omega)] temp_omega;
            if (max_t < size(omega)) {
                temp_omega = omega ./ sum(omega[:n_terms_lambda+1]);
            }
            else {
                temp_omega = omega;
            }
            real total = 0;
            for(i in 1:n_terms_lambda) {
                total += (temp_omega[i+1] * I[max_t - i + 1]);
            }
            return total;
    }
}
data {
    int time_steps;
    int Rt_window;
    array[time_steps] int<lower=0> C;  // Length of biased timeseries must be known at compile time
    vector[20] serial_interval;  // 20 unit vectors generated in renewal_model.py
    vector[60] gamma_delay;
    vector[7] alpha_prior;
    real death_time_dist_alpha;
    real death_time_dist_beta;
}
transformed data {
   array[time_steps] real I_prior_stdev;
   for(i in 1:time_steps){
       I_prior_stdev[i] = floor(sqrt(C[i]));
   }
}
parameters {
    real m;  // Mortality ratio
    simplex[7] alpha;
    array[time_steps] real<lower=0> I;
    array[time_steps] real<lower=0> R;  // Time-varying, unknown reproduction number
    // array[time_steps] real<lower=0> D;
}
transformed parameters {
   vector[7] bias;
   bias = 7 * alpha;
}
model {
    
    for(i in 1:time_steps) {
        // P(I_t | R_t, Lambda_t) - Renewal Model
        int window_width;
        if (i < Rt_window)
            window_width = i;
        else {
            window_width = Rt_window;
        }

        for(j in 1:window_width){
            real mu = R[i] * calculate_lambda(alpha, I, serial_interval, i-(j-1));
            I[i-(j-1)] ~ normal(mu, sqrt(mu));
        }
        
        // Determine D_t from I_t
        // int delay_window;
        // vector[size(gamma_delay)] temp_delay;

        // if (i < size(gamma_delay)){
        //     delay_window = i;
        //     temp_delay = gamma_delay ./ sum(temp_delay[:i]);
        // }
        // else {
        //     delay_window = size(gamma_delay);
        //     temp_delay = gamma_delay;
        // }

        real D_i = 0;
        // for(j in 1:delay_window) {
        //     D_i += (temp_delay[j] * I[i - j + 1]);
        // }
        // D[i] = D_i;

        if(i<size(gamma_delay))
            D_i = I[i];
        else {
            // D_i = I[i-7];
            for(j in 1:size(gamma_delay)) {
                D_i += (gamma_delay[j] * m * I[i - j + 1]);
            }
        }

        // P(C_t | a_i, I_t) - Reporting Process
        C[i] ~ poisson(D_i * bias[(i % 7) + 1]);
    }

    alpha ~ dirichlet(alpha_prior); 
    R ~ gamma(1,1);
    m ~ gamma(1,1);
    I ~ normal(C, sqrt(C));
    // D ~ normal(C, sqrt(C));
}