import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from indnet.config import load_config
from indnet.network import build_association_network
from indnet.pipeline import run_pipeline


class PipelineTests(unittest.TestCase):
    def test_network_contains_each_undirected_pair_once(self):
        rng = np.random.default_rng(7)
        frame = pd.DataFrame(rng.normal(size=(50, 3)), columns=["a", "b", "c"])
        edges = build_association_network(frame, minimum_pair_size=10)
        self.assertEqual(len(edges), 3)
        self.assertEqual(set(edges.columns), {
            "source", "target", "n", "correlation", "p_value", "q_value", "significant"
        })

    def test_end_to_end_pipeline(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            rng = np.random.default_rng(11)
            count = 60
            frame = pd.DataFrame(
                {
                    "sample": [f"s{index}" for index in range(count)],
                    "a": rng.normal(size=count),
                    "b": rng.normal(size=count),
                    "c": rng.normal(size=count),
                }
            )
            frame.to_csv(root / "input.csv", index=False)
            (root / "config.toml").write_text(
                """
[data]
input = "input.csv"
sample_id = "sample"
traits = ["a", "b", "c"]
covariates = []

[preprocessing]
rank_inverse_normal = true
residualize = false

[network]
minimum_pair_size = 20
fdr_level = 0.05

[output]
directory = "output"
edge_file = "edges.csv"
""".strip(),
                encoding="utf-8",
            )
            destination = run_pipeline(load_config(root / "config.toml"))
            self.assertTrue(destination.is_file())
            self.assertEqual(len(pd.read_csv(destination)), 3)


if __name__ == "__main__":
    unittest.main()
