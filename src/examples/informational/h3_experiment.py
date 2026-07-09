import numpy as np
import pandas as pd
from csrf.temporal.markov import MarkovTransitionOperator, FrobeniusTemporalComparator
from csrf.temporal.analyzer import TemporalFidelityAnalyzer

def generate_base_clinical_trajectory(n_patients=100, n_timepoints=52, seed=42):
    np.random.seed(seed)
    P_base = np.array([
        [0.85, 0.10, 0.05],  # Desde Remisión
        [0.10, 0.75, 0.15],  # Desde Estable
        [0.20, 0.30, 0.50]   # Desde Brote
    ])

    all_trajectories = []
    for _ in range(n_patients):
        current_state = np.random.choice([0, 1, 2], p=[0.3, 0.6, 0.1])
        patient_track = []
        for _ in range(n_timepoints):
            if current_state == 0:
                val = np.random.normal(2.0, 0.5)
            elif current_state == 1:
                val = np.random.normal(5.0, 0.6)
            else:
                val = np.random.normal(8.5, 0.7)

            patient_track.append(max(0.0, min(10.0, val)))
            current_state = np.random.choice([0, 1, 2], p=P_base[current_state])
        all_trajectories.append(patient_track)

    return np.array(all_trajectories)

def run_h3_experiments():
    X = generate_base_clinical_trajectory()

    operator = MarkovTransitionOperator(n_states=3, min_val=0.0, max_val=10.0)
    # CALIBRACIÓN: Elevamos gamma a 3.0 para estirar el espacio métrico de Frobenius
    # y penalizar severamente la pérdida de estructura markoviana.
    comparator = FrobeniusTemporalComparator(gamma=3.0)
    analyzer = TemporalFidelityAnalyzer(operator, comparator)

    results = []

    # A: Temporal Smoothing
    for window in [1, 3, 5, 7, 11, 15]:
        if window == 1:
            S = X.copy()
        else:
            S = np.array([pd.Series(row).rolling(window, min_periods=1, center=True).mean().values for row in X])
        tf = analyzer.analyze_fidelity(X, S)
        results.append({"experiment": "temporal_smoothing", "parameter": window, "TF": tf})

    # B: Phase Delay
    for delay in [0, 1, 2, 3, 4, 5]:
        if delay == 0:
            S = X.copy()
        else:
            S = np.zeros_like(X)
            for i in range(X.shape[0]):
                S[i, delay:] = X[i, :-delay]
                S[i, :delay] = X[i, 0]
        tf = analyzer.analyze_fidelity(X, S)
        results.append({"experiment": "phase_delay", "parameter": delay, "TF": tf})

    # C: Transition Corruption
    for rate in [0.0, 0.1, 0.2, 0.4, 0.6, 0.8]:
        S = X.copy()
        mask = np.random.rand(*S.shape) < rate
        S[mask] = np.random.uniform(0.0, 10.0, size=np.sum(mask))
        tf = analyzer.analyze_fidelity(X, S)
        results.append({"experiment": "transition_corruption", "parameter": rate, "TF": tf})

    df = pd.DataFrame(results)
    df.to_csv("examples/informational/h3_experimental_results.csv", index=False)
    print("✔ Experimentos H3 re-calibrados con éxito.")

if __name__ == "__main__":
    run_h3_experiments()
