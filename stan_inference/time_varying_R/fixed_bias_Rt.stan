//
// Model with a fixed reporting bias based on a dirichlet prior,
// as well as an unknown, time-varying Rt value
//

functions {
    int min_of_int_pair(int value_1, int value_2) {
        if (value_1 < value_2)
            return value_1;
        else {
            return value_2;
        }
    }
    real calculate_lambda(vector alpha, array[] int C, vector omega, int max_t) {
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
    int Rt_window;
    array[time_steps] int<lower=0> C;  // Length of biased timeseries must be known at compile time
    vector[20] serial_interval;  // 20 unit vectors generated in renewal_model.py
    vector[7] alpha_prior;
}
parameters {
    simplex[7] alpha;
    array[time_steps] real<lower=0> R;  // Time-varying, unknown reproduction number
}
transformed parameters {
   vector[7] bias;
   bias = 7 * alpha;
}
model {
    // P(C_t | a_i, R_t)
    for(i in 1:time_steps) {
        int window_width;
        if (i < Rt_window)
            window_width = i;
        else {
            window_width = Rt_window;
        }

        for(j in 1:window_width){
            C[i-(j-1)] ~ poisson(R[i] * calculate_lambda(alpha, C, serial_interval, i-(j-1)) * bias[((i-(j-1)) % 7) + 1]);
        }
    }
    
    alpha ~ dirichlet(alpha_prior); 
    R ~ gamma(1,1);
}