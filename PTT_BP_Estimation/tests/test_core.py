import unittest
import numpy as np

from ptt_bp.config import PipelineConfig
from ptt_bp.data_loading import UnsupportedTimingSourceError, validate_manifest_entry
from ptt_bp.timing import extract_pat, extract_ptt


class TimingPipelineTests(unittest.TestCase):
    def setUp(self):
        self.fs = 125.0
        self.n = 20 * int(self.fs)
        self.peaks = np.arange(150, self.n - 100, int(self.fs))

    def test_pat_synthetic_delay(self):
        ecg, ppg = np.zeros(self.n), np.zeros(self.n)
        for peak in self.peaks:
            ecg[peak] = 3
            ppg[peak + 25] = -1
            ppg[peak + 45] = 1
        result = extract_pat(ecg, ppg, self.fs, (100, 450))
        self.assertGreater(len(result.timings_ms), 10)
        self.assertAlmostEqual(np.median(result.timings_ms), 200.0, delta=16.0)

    def test_ptt_synthetic_delay(self):
        proximal, distal = np.zeros(self.n), np.zeros(self.n)
        for peak in self.peaks:
            proximal[peak] = -1
            proximal[peak + 20] = 1
            distal[peak + 15] = -1
            distal[peak + 35] = 1
        result = extract_ptt(proximal, distal, self.fs, (20, 300))
        self.assertGreater(len(result.timings_ms), 10)
        self.assertAlmostEqual(np.median(result.timings_ms), 120.0, delta=16.0)

    def test_rejects_facial_roi_pair(self):
        with self.assertRaises(UnsupportedTimingSourceError):
            validate_manifest_entry({"record_id": "bad", "mode": "facial_roi_pair", "signals": {}}, PipelineConfig())


if __name__ == "__main__":
    unittest.main()
