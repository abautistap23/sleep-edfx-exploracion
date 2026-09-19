import sys
from pathlib import Path
import tempfile
import unittest
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mne
import numpy as np
import pyedflib
from exploracion_sleep_edfx import epoch_labels, identity, explore


class ExplorationTests(unittest.TestCase):
    def test_names_and_stages(self):
        self.assertEqual(identity(Path('SC4001E0-PSG.edf')), identity(Path('SC4001EC-Hypnogram.edf')))
        self.assertEqual(identity(Path('ST7011JP-Hypnogram.edf'))[1], 'ST701')
        descriptions = ['Sleep stage W', 'Sleep stage 1', 'Sleep stage 2', 'Sleep stage 3', 'Sleep stage 4', 'Sleep stage R', 'Movement time', 'Sleep stage ?']
        counts, excluded, unknown = epoch_labels(mne.Annotations(np.arange(8)*30, [30]*8, descriptions), 240)
        self.assertEqual(counts, {'W': 1, 'N1': 1, 'N2': 1, 'N3': 2, 'REM': 1, 'M': 1, '?': 1})
        self.assertEqual((excluded, unknown), (0, []))

    def test_boundaries_overlap_and_unknown(self):
        ann = mne.Annotations([0, 30, 45, 90], [30, 30, 30, 30], ['Sleep stage W', 'Sleep stage 1', 'Sleep stage 2', 'other'])
        counts, excluded, unknown = epoch_labels(ann, 135)
        self.assertEqual(sum(counts.values()), 1)
        self.assertEqual(excluded, 3)
        self.assertEqual(unknown, ['other'])
        counts, excluded, _ = epoch_labels(mne.Annotations([0], [90], ['Sleep stage R']), 60, -30)
        self.assertEqual(counts['REM'], 2)
        self.assertEqual(excluded, 0)

    def test_end_to_end_synthetic_edf(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / 'data' / 'nested'
            data.mkdir(parents=True)
            start = datetime(2020, 1, 1, 22)
            with pyedflib.EdfWriter(str(data / 'SC4001E0-PSG.edf'), 2, file_type=pyedflib.FILETYPE_EDFPLUS) as writer:
                headers = []
                for label, rate in [('EEG Fpz-Cz', 100), ('EMG submental', 1)]:
                    headers.append({'label': label, 'dimension': 'uV', 'sample_frequency': rate, 'physical_min': -100, 'physical_max': 100, 'digital_min': -32768, 'digital_max': 32767, 'transducer': '', 'prefilter': ''})
                writer.setSignalHeaders(headers)
                writer.setStartdatetime(start)
                writer.writeSamples([np.zeros(9000), np.zeros(90)])
            with pyedflib.EdfWriter(str(data / 'SC4001EC-Hypnogram.edf'), 0, file_type=pyedflib.FILETYPE_EDFPLUS) as writer:
                writer.setStartdatetime(start)
                writer.writeAnnotation(0, 30, 'Sleep stage W')
                writer.writeAnnotation(30, 60, 'Sleep stage 4')
            result = explore(Path(tmp) / 'data', Path(tmp) / 'out')
            self.assertEqual(result['n_records_processed'], 1)
            self.assertEqual(result['n_epochs_labeled'], 3)
            self.assertEqual(result['n_issues'], 0)
            import pandas as pd
            profile = pd.read_csv(Path(tmp) / 'out' / 'channels.csv')
            self.assertEqual(profile.sfreq_hz.tolist(), [100, 1])
            # Duplicados se reportan y no se cuentan dos veces.
            import shutil
            shutil.copy(data / 'SC4001EC-Hypnogram.edf', data.parent / 'SC4001EC-Hypnogram.edf')
            result = explore(Path(tmp) / 'data', Path(tmp) / 'out')
            self.assertEqual(result['n_pairs'], 0)
            self.assertEqual(result['n_issues'], 1)


if __name__ == '__main__':
    unittest.main()
