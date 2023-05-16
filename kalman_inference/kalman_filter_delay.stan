functions {
  real v_k_f(real y_k, row_vector H, vector m_k_bar) {
    return(y_k - H * m_k_bar);
  }
  vector m_k_bar_f(matrix A, vector m_k) {
    return(A * m_k);
  }
  real S_k_f(row_vector H, matrix P_k_bar, real sigma) {
    return(H * P_k_bar * H' + sigma^2);
  }
  matrix P_k_bar_f(matrix A, matrix P_k, matrix Sigma) {
    return(A * P_k * A' + Sigma);
  }
  matrix P_k_f(matrix P_k_bar, vector K_k, real S_k) {
    return(P_k_bar - K_k * S_k * K_k');
  }
  vector K_k_f(matrix P_k_bar, row_vector H, real S_k) {
    return(P_k_bar * H' * S_k^-1);
  }
  vector m_k_f(vector m_k_bar, vector K_k, real v_k) {
    return(m_k_bar + K_k * v_k);
  }
  real mu_f(row_vector H, vector m_k_bar) {
    return(H * m_k_bar);
  }
}

data {
  int N; // number of data points
  int K; // number of R segments
  int window[N]; // assigns a time point to a given segment
  vector[N] C; // case series
  int wmax; // max day of generation time distribution
  row_vector[wmax] w;
  vector[wmax] I_history; // note the order for this should be most recent cases first
}

transformed data {
  matrix[wmax, wmax] A = rep_matrix(0.0, wmax, wmax);
  row_vector[wmax] H = rep_row_vector(0.0, wmax);
  H[1] = 1.0;
  A[1, ] = to_row_vector(w);
  for(i in 2:wmax)
    A[i, i - 1] = 1.0;
}

parameters {
  real<lower=0> R[K];
  real<lower=0> sigma;
  simplex[3] delay[7];
}

model {
  vector[wmax] m_k = I_history;
  matrix[wmax, wmax] P_k = rep_matrix(0.0, wmax, wmax);
  vector[wmax] m_k_bar;
  matrix[wmax, wmax] P_k_bar;
  real v_k;
  real S_k;
  vector[wmax] K_k;
  matrix[wmax, wmax] Sigma = rep_matrix(0.0, wmax, wmax);
  real E_cases;
  real sigma_n;
  real mu;
  vector[wmax] I_temp;
  matrix[wmax, wmax] A_k = A;
  
  row_vector[wmax] H_t;
  
  // initial guess at covariance matrix: not sure about this
  P_k[1, 1] = R[window[1]] * w * I_history;
  
  for(t in 1:N) {
    // Get H for this day
    H_t = rep_row_vector(0.0, wmax);
    for (n in 1:3) {
      H_t[n] = delay[((((t-n+1) % 7) + 7 ) % 7) + 1, n];
    }
    
    // update first row of A
    A_k[1, ] = A[1, ] * R[window[t]];
    
    // prediction step
    m_k_bar = m_k_bar_f(A_k, m_k);
    
    // since m_k_bar is estimate of I, use that in place of I
    if(t == 1) {
      I_temp = I_history;
    } else if(t < wmax) {
      int kk = wmax - t;
      for(i in 1:kk)
        I_temp[i] = m_k_bar[i];
      for(i in 1:t)
        I_temp[i + kk] = I_history[i];
    } else {
      I_temp = m_k_bar;
    }
    E_cases = R[window[t]] * w * I_temp;
    Sigma[1, 1] = E_cases;
    sigma_n = sigma * sqrt(m_k_bar[1]);
    
    // prediction continued
    P_k_bar = P_k_bar_f(A_k, P_k, Sigma);
    
    // update step
    v_k = v_k_f(C[t], H_t, m_k_bar);
    S_k = S_k_f(H, P_k_bar, sigma_n);
    K_k = K_k_f(P_k_bar, H_t, S_k);
    m_k = m_k_f(m_k_bar, K_k, v_k);
    P_k = P_k_f(P_k_bar, K_k, S_k);
    
    mu = mu_f(H_t, m_k_bar);
    C[t] ~ normal(mu, sqrt(S_k));
  }
  R ~ normal(2, 5);
  sigma ~ normal(0, 10);
  for (j in 1:7) {
    delay[j] ~ dirichlet(rep_vector(1.0, 3));
  }
}
