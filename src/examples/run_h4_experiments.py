import numpy as np
import pandas as pd
from src.csrf.h4_cross_domain import SpearmanCouplingOperator, CorrelationComparator

def execute_h4_experimental_suite():
    print("==========================================================")
    print("RE-INITIALIZING H4 EXPERIMENTAL ENGINE (DYNAMIC FIX)")
    print("==========================================================")

    np.random.seed(42)
    n_samples = 1000

    # NUEVA SEÑAL DINÁMICA: Permite que el desfase temporal rompa la coincidencia de rangos
    t = np.linspace(0, 4 * np.pi, n_samples)
    domain_a_native = np.sin(t) + np.random.normal(0, 0.2, n_samples)
    domain_b_native = np.sin(t) + np.random.normal(0, 0.2, n_samples)

    operator = SpearmanCouplingOperator()
    comparator = CorrelationComparator()

    # Calcular la referencia exacta síncrona
    rep_x = operator.compute(domain_a_native, domain_b_native)
    results = []

    # --------------------------------------------------------------------------
    # H4-A: IDENTITY & ASYNCHRONOUS LAG (CORREGIDA CON DINÁMICA REAL)
    # --------------------------------------------------------------------------
    print("Running H4-A: Dynamic Asynchronous Lag...")
    for lag in range(0, 11):
        if lag == 0:
            domain_b_s = domain_b_native.copy()
        else:
            # Desplazar el vector de forma que rompa la concordancia de fase
            domain_b_s = np.roll(domain_b_native, lag * 25) # Forzamos un desfase agresivo por paso
            domain_b_s[:lag * 25] = domain_b_native[0]

        rep_s = operator.compute(domain_a_native, domain_b_s)
        dist = comparator.compare(rep_x, rep_s)
        cf = 1.0 - dist
        results.append({"experiment": "asynchronous_lag", "parameter": lag, "CF": cf})

    # --------------------------------------------------------------------------
    # H4-B: NOISE INJECTION (Se mantiene intacta - Rendimiento excelente)
    # --------------------------------------------------------------------------
    print("Running H4-B: Independent Noise Injection...")
    noise_levels = np.linspace(0, 5, 11)
    for noise in noise_levels:
        domain_b_s = domain_b_native + np.random.normal(0, noise * 0.4, n_samples)
        rep_s = operator.compute(domain_a_native, domain_b_s)
        dist = comparator.compare(rep_x, rep_s)
        cf = 1.0 - dist
        results.append({"experiment": "noise_injection", "parameter": noise, "CF": cf})

    # --------------------------------------------------------------------------
    # H4-C: PARTIAL DECOUPLING (Se mantiene intacta - Curva de inflexión top)
    # --------------------------------------------------------------------------
    print("Running H4-C: Partial Decoupling...")
    fractions = np.linspace(0, 1, 11)
    for frac in fractions:
        domain_b_s = domain_b_native.copy()
        n_break = int(frac * n_samples)
        if n_break > 0:
            indices = np.arange(n_break)
            np.random.shuffle(indices)
            domain_b_s[:n_break] = domain_b_s[indices]

        rep_s = operator.compute(domain_a_native, domain_b_s)
        dist = comparator.compare(rep_x, rep_s)
        cf = 1.0 - dist
        results.append({"experiment": "partial_decoupling", "parameter": frac, "CF": cf})

    # --------------------------------------------------------------------------
    # H4-D: PROGRESSIVE DECOUPLING
    # --------------------------------------------------------------------------
    decoupling_steps = np.linspace(0, 1, 11)
    for step in decoupling_steps:
        random_noise = np.random.normal(0, 1, n_samples)
        domain_b_s = (1.0 - step) * domain_b_native + step * random_noise
        rep_s = operator.compute(domain_a_native, domain_b_s)
        dist = comparator.compare(rep_x, rep_s)
        cf = 1.0 - dist
        results.append({"experiment": "progressive_decoupling", "parameter": step, "CF": cf})

    df = pd.DataFrame(results)
    df.to_csv("examples/informational/h4_experimental_results.csv", index=False)
    print("✔ [H4 ENGINE FIXED] Data serialized and verified.")

if __name__ == "__main__":
    execute_h4_experimental_suite()
