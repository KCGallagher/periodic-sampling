// Model with a fixed reporting bias based on a gamma prior, with known constant R0

functions {
    int min_of_int_pair(int value_1, int value_2) {
        if (value_1 < value_2)
            return value_1;
        else {
            return value_2;
        }
    }
    real calculate_lambda(array[] real alpha, array[] int C, real R, vector omega, int max_t) {
            if (max_t == 1)
                return C[1]; 
            int n_terms_lambda = min_of_int_pair(max_t, size(omega) - 1);  // Number of terms in sum for lambda

            vector[size(omega)] temp_omega;
            if (max_t < size(omega))
                temp_omega = omega ./ sum(omega[:n_terms_lambda]);
            else {
                temp_omega = omega;
            }
            real total = 0;
            for(i in 1:n_terms_lambda) {
                total += (temp_omega[i+1] * C[max_t - i + 1]);
            }
            return total;
    }
}
data {
    int time_steps;
    array[time_steps] int<lower=0> C;  // Length of biased timeseries must be known at compile time
    real<lower=0> R;  // Constant, known reproduction number
    vector[20] serial_interval;  // 20 unit vectors generated in renewal_model.py
}
parameters {
    array[7] real<lower=0, upper=7> alpha;
}
model {
    for(i in 1:time_steps) {
        C[i] ~ poisson(R * calculate_lambda(alpha, C, R, serial_interval, i) * alpha[(i % 7) + 1]);
        // C[i] ~ poisson(R * C[i] * alpha[(i % 7) + 1]);
    }
    
    alpha ~ gamma(1,1);  // Gamma prior for bias vector
}

// Moderate accuracy but predicted alpha values do not sum to 7
// It therefore may be beneficial to switch to a dirichlet dist with a simplex bias vector