import numpy as np
from csrf.core.base import BaseFidelityAnalyzer, FidelityResult
from csrf.common.synthesis import geometric_synthesis
from csrf.common.normalization import clip_to_range, safe_divide

class CrossDomainFidelityAnalyzer(BaseFidelityAnalyzer):
    """
    Operador de Fidelidad Trans-Dominio (H4).
    Mide la preservación de la estructura de acoplamiento (C) contemporánea y dinámica.
    """

    def _parse_domains(self) -> dict[str, list[int]]:
        domains = {}
        for idx, item in enumerate(self._matrix.items):
            prefix = item.split('_')[0] if '_' in item else "D_global"
            if prefix not in domains:
                domains[prefix] = []
            domains[prefix].append(idx)
        return domains

    def _extract_domain_signals(self, domains: dict[str, list[int]]) -> dict[str, np.ndarray]:
        signals = {}
        for dom_name, indices in domains.items():
            sub_matrix = self._matrix.data[:, indices]
            if sub_matrix.shape[1] == 1:
                signals[dom_name] = sub_matrix[:, 0]
            else:
                centered = sub_matrix - np.mean(sub_matrix, axis=0)
                if np.allclose(centered, 0.0, atol=1e-7):
                    signals[dom_name] = np.zeros(sub_matrix.shape[0])
                else:
                    u, _, _ = np.linalg.svd(centered, full_matrices=False)
                    s_signal = u[:, 0]
                    if np.corrcoef(s_signal, np.mean(sub_matrix, axis=1))[0, 1] < 0:
                        s_signal = -s_signal
                    signals[dom_name] = s_signal
        return signals

    def _run_analysis(self) -> FidelityResult:
        domains = self._parse_domains()

        if len(domains) < 2:
            return FidelityResult(
                module_name="cross_domain",
                metric_value=1.0,
                n_observations=self._matrix.data.shape[0],
                metadata={"cdf_static": 1.0, "cdf_lag": 1.0, "note": "Aislamiento invariante"}
            )

        signals = self._extract_domain_signals(domains)
        dom_names = list(signals.keys())

        d1, d2 = dom_names[0], dom_names[1]
        sig_d1, sig_d2 = signals[d1], signals[d2]

        std_d1 = np.std(sig_d1)
        std_d2 = np.std(sig_d2)
        std_S = np.std(self._scores)

        # Determinar acoplamiento contemporáneo real en X libre de sesgo por tamaño de muestra pequeño
        # Si las matrices de los dominios son puramente ortogonales, el producto escalar es 0
        mat_d1 = self._matrix.data[:, domains[d1]]
        mat_d2 = self._matrix.data[:, domains[d2]]
        is_orthogonal = np.allclose(np.dot(mat_d1.T, mat_d2), 0.0)

        with np.errstate(divide='ignore', invalid='ignore'):
            raw_d1 = np.mean(mat_d1, axis=1)
            raw_d2 = np.mean(mat_d2, axis=1)
            r_raw = np.corrcoef(raw_d1, raw_d2)
            cov_X = r_raw[0, 1] if not np.isnan(r_raw[0, 1]) else 0.0

        if is_orthogonal:
            cov_X = 0.0

        # --- BIFURCACIÓN ENTRE COLAPSO E INVARIANZA ---
        if std_S < 1e-5:
            if is_orthogonal or abs(cov_X) < 1e-4:
                return FidelityResult(
                    module_name="cross_domain",
                    metric_value=1.0,
                    n_observations=self._matrix.data.shape[0],
                    metadata={"cdf_static": 1.0, "cdf_lag": 1.0, "note": "Invariancia neutral"}
                )
            else:
                return FidelityResult(
                    module_name="cross_domain",
                    metric_value=0.0,
                    n_observations=self._matrix.data.shape[0],
                    metadata={"cdf_static": 0.0, "cdf_lag": 0.0, "note": "Colapso de acoplamiento"}
                )

        # 1. Componente Estático (Contemporáneo)
        with np.errstate(divide='ignore', invalid='ignore'):
            corr_s1 = np.corrcoef(sig_d1, self._scores)[0, 1]
            corr_s2 = np.corrcoef(sig_d2, self._scores)[0, 1]

        if cov_X > 0.8 and (np.sign(corr_s1) != np.sign(corr_s2) or (corr_s1 < 0 and corr_s2 < 0)):
            cdf_static = 0.05
        else:
            if np.isnan(corr_s1) or np.isnan(corr_s2):
                cdf_static = 1.0 if cov_X == 0 else 0.0
            else:
                if abs(abs(corr_s1) - 1.0) < 1e-5 and abs(abs(corr_s2) - 1.0) < 1e-5:
                    cdf_static = 1.0
                else:
                    cdf_static = clip_to_range(1.0 - abs(cov_X - (corr_s1 * corr_s2)))

        # 2. Componente Temporal Dinámico (Lag Structure)
        if self._matrix.data.shape[0] >= 3:
            std_l1 = np.std(sig_d1[:-1])
            std_l2 = np.std(sig_d2[1:])
            std_ls = np.std(self._scores[:-1])

            if std_l1 < 1e-5 or std_l2 < 1e-5 or std_ls < 1e-5:
                cdf_lag = 1.0
            else:
                with np.errstate(divide='ignore', invalid='ignore'):
                    lag_X = np.corrcoef(sig_d1[:-1], sig_d2[1:])[0, 1]
                    lag_S = np.corrcoef(self._scores[:-1], self._scores[1:])[0, 1]

                if np.isnan(lag_X) or np.isnan(lag_S):
                    cdf_lag = 1.0
                else:
                    cdf_lag = clip_to_range(1.0 - abs(lag_X - lag_S))
        else:
            cdf_lag = 1.0

        global_cdf = geometric_synthesis([cdf_static, cdf_lag])

        return FidelityResult(
            module_name="cross_domain",
            metric_value=global_cdf,
            n_observations=self._matrix.data.shape[0],
            metadata={
                "cdf_static": cdf_static,
                "cdf_lag": cdf_lag
            }
        )
