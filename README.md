# Clinical Structural Representation Framework (CSRF)

[![Zenodo](https://zenodo.org/badge/DOI/10.5281/zenodo.21296981.svg)](https://doi.org/10.5281/zenodo.21296981)
[![OSF Pre-registration](https://img.shields.io/badge/OSF-Pre--registration-blue)](https://doi.org/10.17605/osf.io/a84pq)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Official reference implementation of the **Clinical Structural Representation Framework (CSRF)**, a mathematically rigorous diagnostic layer designed to formalize, monitor, and quantify the structural fidelity and representation loss of aggregated multidimensional clinical data and Patient-Reported Outcome Measures (PROMs).

---

## Overview

In clinical trials and observational registries, multi-item multidimensional PROMs are routinely compressed into a single aggregate composite score to simplify epidemiological analysis. However, this arithmetic pooling introduces an unquantified representational cost, often flattening distinct pathological states into identical scores—creating states of representational non-equivalence.

The CSRF operates as an independent, model-agnostic quality control layer that evaluates the geometric and mathematical preservation of high-dimensional clinical matrices across four complementary dimensions:

* **Temporal Fidelity ($TF_{H1}$):** Captures individual longitudinal state-transition likelihoods using Markovian trajectory mapping to resolve pathway ambiguity.
* **Spatial Fidelity ($SF_{H2}$):** Measures the preservation of metric geometry and latent topology among multi-axis patient vectors.
* **Informational Fidelity ($IF_{H3}$):** Evaluates the retention of downstream predictive variance post-aggregation relative to external endpoints.
* **Cross-Domain Fidelity ($CF_{H4}$):** Monitors inter-construct synchrony to audit artificial couplings induced by score compression when underlying clinical domains behave asynchronously.

---

## Repository Structure

The framework is organized following professional Python production and Open Science packaging standards:

```text
CSRF/
├── Dataset_Bioinformatic_Flexible.csv  <- Anonymized PMCF clinical dataset (MDR 2017/745)
├── LICENSE                             <- MIT Open Source License
├── README.md                           <- Comprehensive documentation and verification guide
├── requirements.txt                    <- Framework environment dependencies
│
├── docs/
│   ├── H1_validation_report.md         <- Experimental & axiomatic validation logs for TF_H1
│   ├── H2_validation_report.md         <- Detailed mathematical validation logs for SF_H2
│   ├── H3_validation_report.md         <- Experimental & informational validation logs for IF_H3
│   └── H4_validation_report.md         <- Experimental & topological validation logs for CF_H4
│
├── notebooks/
│   └── csrf_orchestration_pipeline.ipynb <- End-to-end interactive validation tutorial
│
└── src/                                <- Main Source Directory
    └── csrf/                           <- Main Core Source Code Package
        ├── __init__.py
        │
        ├── common/                     <- Shared utility modules and mathematical bases
        │   ├── __init__.py
        │   ├── constants.py
        │   ├── normalization.py
        │   ├── synthesis.py
        │   └── validation.py
        │
        ├── core/                       <- Abstract framework primitives & configurations
        │   ├── __init__.py
        │   ├── base.py
        │   ├── config.py
        │   └── contracts.py
        │
        ├── cross_domain/               <- Cross-Domain Fidelity Module (H4)
        │   ├── __init__.py
        │   └── analyzer.py
        │
        ├── informational/              <- Informational Fidelity Module (H3)
        │   ├── __init__.py
        │   ├── analyzer.py
        │   └── fidelis.py
        │
        ├── io/                         <- Data ingestion layer
        │   ├── __init__.py
        │   └── loaders.py
        │
        ├── metrics/                    <- Computational distance and statistical suites
        │   ├── __init__.py
        │   ├── bootstrap.py
        │   └── distance.py
        │
        ├── spatial/                    <- Spatial Fidelity Module (H2)
        │   ├── __init__.py
        │   └── analyzer.py
        │
        ├── temporal/                   <- Temporal Fidelity Module (H1)
        │   ├── __init__.py
        │   ├── analyzer.py
        │   ├── comparators.py
        │   ├── markov.py
        │   └── operators.py
        │
        └── tests/                      <- Automated Verification & Testing Suites (Internalized)
            ├── test_core.py
            ├── test_cross_domain.py
            ├── test_informational.py
            ├── test_spatial.py
            ├── test_temporal.py
            │
            └── canonical/              <- Regression suite & reference golden outputs
                ├── diagnostic_h1_bug.py
                ├── expected_results.json
                └── run_h1.py
````

***

## Installation & Environment Setup

This framework requires Python 3.8+. It is recommended to deploy the tool within a clean virtual environment or a Google Colab instance.
1. Clone the repository

````bash

git clone https://github.com/nazariofelix-CTB/csrf.git
````

2. Install dependencies
````bash

pip install -r requirements.txt
````

***

## Quick Start Guide

To verify the installation and execute the baseline multi-fidelity diagnostic pipeline using the enclosed anonymized PMCF clinical dataset (compliant with MDR 2017/745), run the following commands from the root directory:
````bash

# 1. Add the source directory to your environment path
export PYTHONPATH=src

# 2. Run the baseline multidimensional spatial fidelity (H2) demonstration
python examples/run_h2_demo.py
````

To execute the full suite of axiomatic validation, simulation benchmarks, and stress-testing experiments across all framework dimensions (H1, H2, H3, and H4):
````bash

# Run the H1 temporal trajectory evaluation suite
python examples/canonical/run_h1.py

# Run the H2 axiomatic spatial fidelity evaluation suite
python examples/run_h2_axiomatic_tests.py

# Run the H3 informational fidelity evaluation suite
python examples/run_h3_axiomatic_tests.py

# Run the H4 cross-domain simulation pipeline
python examples/run_h4_axiomatic_tests.py
````
````text
Note for Windows users (CMD):
Replace export PYTHONPATH=src with set PYTHONPATH=src before executing the python commands.
````

## Study Pre-registration & Regulatory Compliance

* **Conceptual Protocol:** The mathematical axioms, inferential plans, and operational workflows of this framework were pre-registered on the Open Science Framework (OSF) and can be verified via https://doi.org/10.17605/osf.io/a84pq.

* **Data Availability and Ethics:** The evaluation dataset enclosed in this repository (Dataset_Bioinformatic_Flexible.csv) consists of real-world clinical metrics obtained in strict accordance with the European Medical Device Regulation (MDR 2017/745) under an official Post-Market Clinical Follow-up (PMCF) plan. All participating patients provided explicit, written informed consent prior to data collection. In compliance with the European General Data Protection Regulation (GDPR), the dataset has been subjected to a rigorous, irreversible anonymization process at the source (Centro de Tecnología Biomédica, CTB-UPM), ensuring that no protected health information (PHI) or longitudinal patient identity can be reverse-engineered. This enables full algorithmic reproducibility of the validation suites using genuine clinical trajectories while maintaining absolute patient privacy.

## Citation

If you use this framework, its mathematical operators, or the accompanying implementation in an academic publication, please cite:

````text
Felix-Gonzalez, N., Gomez-Arguelles, JM & Maestu-Unturbe, C. (2026). 
Structural Fidelity of Aggregated Patient-Reported Outcome Measures: 
Development and Validation of the Clinical Structural Representation Framework (CSRF). 
Journal of Clinical Epidemiology. 
DOI pending publication.
````
