functions {
    real calculate_lambda(array[] real alpha, array[] int C, real R, vector omega, int max_t) {
            if (max_t == 0)
                return (C[1] / alpha[1]);
            else
                return C[max_t];
            // int n_terms_lambda = min(max_t + 1, size(omega));  // Number of terms in sum for lambda

            // vector[size(omega)] temp_omega;
            // if (max_t < size(omega))
            //     temp_omega = omega ./ sum(omega[:n_terms_lambda]);
            // else {
            //     temp_omega = omega;
            // }

            // real total = 0;
            // for(i in 1:n_terms_lambda) {
            //     total += (temp_omega[i] * C[max_t - i + 1]);
            // }
            // return total;
    }
}
data {
    array[100] int<lower=0> C;  // Length of biased timeseries must be known at compile time
    real<lower=0> R;  // Constant, known reproduction number
    vector[20] serial_interval;  // 20 unit vectors generated in renewal_model.py
}
parameters {
    array[7] real<lower=0> alpha;
}
model {
    for(i in 1:100) {
        C[i] ~ poisson(R * calculate_lambda(alpha, C, R, serial_interval, i) * alpha[(i % 7) + 1]);
        // C[i] ~ poisson(R * C[i] * alpha[(i % 7) + 1]);
    }
    // print(C);

    
    alpha ~ gamma(1,1);  // Gamma prior for bias vector
}