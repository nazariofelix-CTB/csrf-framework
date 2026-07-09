# Clinical Structural Representation Framework (CSRF)

https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg](https://doi.org/10.5281/zenodo.XXXXXXX)
https://img.shields.io/badge/OSF-Pre--registration-blue](https://doi.org/10.17605/osf.io/a84pq)
https://img.shields.io/badge/License-MIT-yellow.svg](https://opensource.org/licenses/MIT)

Official reference implementation of the **Clinical Structural Representation Framework (CSRF)**, a mathematically rigorous diagnostic layer designed to formalize, monitor, and quantify the structural fidelity and representation loss of aggregated multidimensional clinical data and Patient-Reported Outcome Measures (PROMs).

---

## Overview

In clinical trials and observational registries, multi-item multidimensional PROMs are routinely compressed into a single aggregate composite score to simplify epidemiological analysis. However, this arithmetic pooling introduces an unquantified *representational cost*, often flattening distinct pathological states into identical scores—creating states of **representational non-equivalence**.

The **CSRF** operates as an independent, model-agnostic quality control layer that evaluates the geometric and mathematical preservation of high-dimensional clinical matrices across four complementary dimensions:

* **Spatial Fidelity ($SF_{H1}$):** Measures the preservation of metric geometry and latent topology among multi-axis patient vectors.
* **Informational Fidelity ($IF_{H2}$):** Evaluates the retention of downstream predictive variance post-aggregation relative to external endpoints.
* **Temporal Fidelity ($TF_{H3}$):** Captures individual longitudinal state-transition likelihoods using Markovian trajectory mapping to resolve pathway ambiguity.
* **Cross-Domain Fidelity ($CF_{H4}$):** Monitors inter-construct synchrony to audit artificial couplings induced by score compression when underlying clinical domains behave asynchronously.

---

## Repository Structure

```text
CSRF/
├── LICENSE
├── README.md
├── requirements.txt
├── Dataset_Bioinformatic_Flexible.csv
│
├── src/
│   └── csrf/
│       ├── core/
│       ├── spatial/
│       ├── informational/
│       ├── temporal/
│       ├── cross_domain/
│       ├── metrics/
│       └── io/
│
├── examples/
│   ├── run_h2_demo.py
│   ├── run_h2_axiomatic_tests.py
│   ├── run_h3_axiomatic_tests.py
│   └── run_h4_experiments.py
│
└── tests/
    └── test_core.py
````

***

## Installation & Environment Setup

This framework requires **Python 3.8+**. It is recommended to deploy the tool within a clean virtual environment or a Google Colab instance.

### 1. Clone the repository

```bash
git clone https://github.com/your-username/csrf.git
cd csrf
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

***

## Quick Start Guide

To verify the installation and execute the baseline multi-fidelity diagnostic pipeline using the enclosed synthetic validation dataset, run:

```bash
export PYTHONPATH=src
python examples/run_h2_demo.py
```

To execute the full suite of validation and stress-testing experiments:

```bash
python examples/run_h3_axiomatic_tests.py
```

***

---

## Study Pre-registration & Regulatory Compliance

* **Conceptual Protocol:** The mathematical axioms, inferential plans, and operational workflows of this framework were pre-registered on the Open Science Framework (OSF) and can be verified via [https://doi.org/10.17605/osf.io/a84pq](https://doi.org/10.17605/osf.io/a84pq).
* **Data Availability and Ethics:** The evaluation dataset enclosed in this repository (`Dataset_Bioinformatic_Flexible.csv`) consists of real-world clinical metrics obtained in strict accordance with the European Medical Device Regulation (MDR 2017/745) under an official Post-Market Clinical Follow-up (PMCF) plan. All participating patients provided explicit, written informed consent prior to data collection. In compliance with the European General Data Protection Regulation (GDPR), the dataset has been subjected to a rigorous, irreversible anonymization process at the source (Centro de Tecnología Biomédica, CTB-UPM), ensuring that no protected health information (PHI) or longitudinal patient identity can be reverse-engineered. This enables full algorithmic reproducibility of the validation suites using genuine clinical trajectories while maintaining absolute patient privacy.

---

## Citation

If you use this framework, its mathematical operators, or the accompanying implementation in an academic publication, please cite:

```text
Felix-Gonzalez, N., Gomez-Arguelles, JM & Maestu-Unturbe, C. (2026).
Structural Fidelity of Aggregated Patient-Reported Outcome Measures:
Development and Validation of the Clinical Structural Representation Framework (CSRF).
Journal of Clinical Epidemiology.
DOI pending publication.
```

***

## License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.
