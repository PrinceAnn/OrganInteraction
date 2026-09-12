import unittest

import numpy as np
import pandas as pd

from indnet.preprocessing import rank_inverse_normal, residualize
from indnet.statistics import benjamini_hochberg


class StatisticsTests(unittest.TestCase):
    def test_benjamini_hochberg_matches_known_values(self):
        observed = benjamini_hochberg([0.01, 0.04, 0.03, 0.002, np.nan])
        expected = np.array([0.02, 0.04, 0.04, 0.008, np.nan])
        np.testing.assert_allclose(observed, expected, equal_nan=True)

    def test_rank_transform_preserves_missingness_and_ties(self):
        values = pd.Series([10.0, 20.0, 20.0, np.nan, 40.0])
        transformed = rank_inverse_normal(values)
        self.assertTrue(np.isnan(transformed.iloc[3]))
        self.assertAlmostEqual(transformed.iloc[1], transformed.iloc[2])
        self.assertLess(transformed.iloc[0], transformed.iloc[1])
        self.assertLess(transformed.iloc[2], transformed.iloc[4])

    def test_residualization_removes_linear_covariate_signal(self):
        covariate = pd.DataFrame({"c": np.arange(20, dtype=float)})
        trait = pd.Series(4.0 + 3.0 * covariate["c"].to_numpy())
        residuals = residualize(trait, covariate)
        self.assertLess(float(np.nanmax(np.abs(residuals))), 1e-10)


if __name__ == "__main__":
    unittest.main()
