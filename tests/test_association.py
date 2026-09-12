import unittest

import numpy as np
import pandas as pd
from scipy.special import expit

from indnet.association import binary_associations, linear_associations


class AssociationTests(unittest.TestCase):
    def test_linear_model_recovers_exposure_effect(self):
        rng = np.random.default_rng(21)
        exposure = rng.normal(size=400)
        covariate = rng.normal(size=400)
        outcome = 2.0 * exposure + 0.7 * covariate + rng.normal(scale=0.4, size=400)
        frame = pd.DataFrame({"y": outcome, "x": exposure, "c": covariate})
        result = linear_associations(frame, "y", ["x"], ["c"])
        self.assertAlmostEqual(float(result.loc[0, "estimate"]), 2.0, delta=0.08)
        self.assertLess(float(result.loc[0, "p_value"]), 1e-20)

    def test_binary_model_returns_finite_positive_effect(self):
        rng = np.random.default_rng(22)
        exposure = rng.normal(size=600)
        covariate = rng.normal(size=600)
        probability = expit(-0.2 + 1.1 * exposure + 0.3 * covariate)
        outcome = rng.binomial(1, probability)
        frame = pd.DataFrame({"y": outcome, "x": exposure, "c": covariate})
        result = binary_associations(frame, "y", ["x"], ["c"])
        self.assertTrue(np.isfinite(result.loc[0, "estimate"]))
        self.assertGreater(float(result.loc[0, "estimate"]), 0.5)
        self.assertLess(float(result.loc[0, "p_value"]), 1e-8)


if __name__ == "__main__":
    unittest.main()
