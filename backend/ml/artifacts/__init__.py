"""PredictIQ v2 ML Production Artifacts & Loader Module.

Provides:
- load_production_model: fail-closed loader verifying SHA-256 checksums,
  dataset integrity, and environment compatibility.
- ProductionModelBundle: container for fitted MultivariateMonotoneModel
  and MondrianConformalPredictor.
"""

from backend.ml.artifacts.loader import ProductionModelBundle, load_production_model

__all__ = ["ProductionModelBundle", "load_production_model"]
