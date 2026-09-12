import unittest

import numpy as np
import pandas as pd

from indnet.decomposition import principal_components


class DecompositionTests(unittest.TestCase):
    def test_pca_shapes_and_variance(self):
        rng = np.random.default_rng(31)
        shared = rng.normal(size=80)
        frame = pd.DataFrame(
            {
                "a": shared + rng.normal(scale=0.1, size=80),
                "b": shared + rng.normal(scale=0.1, size=80),
                "c": rng.normal(size=80),
            }
        )
        result = principal_components(frame, ["a", "b", "c"], components=2)
        self.assertEqual(result.scores.shape, (80, 2))
        self.assertEqual(result.loadings.shape, (3, 2))
        self.assertGreater(float(result.explained_variance_ratio.iloc[0]), 0.5)

    def test_pca_keeps_complete_row_indices(self):
        frame = pd.DataFrame({"a": [1.0, np.nan, 3.0], "b": [2.0, 4.0, 8.0]})
        result = principal_components(frame, ["a", "b"], components=1)
        self.assertEqual(result.scores.index.tolist(), [0, 2])


if __name__ == "__main__":
    unittest.main()
