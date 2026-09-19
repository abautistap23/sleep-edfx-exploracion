#!/usr/bin/env python3
"""Exploración local Sleep-EDFx: cabeceras EDF y anotaciones, sin descargar datos."""
import argparse
from collections import defaultdict
import json
import os
from pathlib import Path
import re

os.environ.setdefault('MPLCONFIGDIR', str(Path(__file__).resolve().parent / '.cache' / 'matplotlib'))

import mne
import numpy as np
import pandas as pd
import pyedflib

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / 'data' / 'sleep-edfx'
CLASSES = ['W', 'N1', 'N2', 'N3', 'REM', 'M', '?']
LABEL_MAP = {'Sleep stage W': 'W', 'Sleep stage 1': 'N1',
             'Sleep stage 2': 'N2', 'Sleep stage 3': 'N3',
             'Sleep stage 4': 'N3', 'Sleep stage R': 'REM',
             'Movement time': 'M', 'Sleep stage ?': '?'}
LABEL_MAP.update({x: x for x in CLASSES})
LABEL_MAP.update({'1': 'N1', '2': 'N2', '3': 'N3', '4': 'N3', 'R': 'REM'})


def identity(path):
    match = re.fullmatch(r'((SC4|ST7)\d{2}[12][A-Za-z0-9])[A-Za-z0-9]-(PSG|Hypnogram)\.edf', path.name)
    if not match:
        raise ValueError('Nombre no reconocido como Sleep-EDFx')
    record = match[1]
    return record, record[:5], record[:2]


def epoch_labels(annotations, duration, offset=0):
    """Cuenta solo ventanas completas en la grilla de 30 s del PSG.

    Huecos, transiciones dentro de una época y solapamientos son excluidos;
    '?' es una etiqueta explícita y no se usa para rellenar datos faltantes.
    """
    starts = np.arange(int(np.floor(duration / 30))) * 30.0
    labels = np.full(len(starts), '', dtype=object)
    touches = np.zeros(len(starts), dtype=int)
    unknown = set()
    for onset, length, description in zip(annotations.onset, annotations.duration, annotations.description):
        begin, end = float(onset) + offset, float(onset) + offset + float(length)
        if length <= 0:
            continue
        intersects = (starts < end - 1e-6) & (starts + 30 > begin + 1e-6)
        touches[intersects] += 1
        full = (starts >= begin - 1e-6) & (starts + 30 <= end + 1e-6)
        mapped = LABEL_MAP.get(str(description).strip())
        if mapped is None:
            unknown.add(str(description))
        else:
            labels[full] = mapped
    labels[touches != 1] = ''
    counts = {label: int(np.sum(labels == label)) for label in CLASSES}
    return counts, int(np.sum(labels == '')), sorted(unknown)


def explore(data_dir, output_dir):
    if not data_dir.is_dir():
        raise ValueError(f'No existe la carpeta de datos: {data_dir}')
    groups = defaultdict(lambda: {'PSG': [], 'Hypnogram': []})
    issues, channels, records, distributions = [], [], [], []
    files = {kind: sorted(data_dir.rglob(f'*-{kind}.edf')) for kind in ('PSG', 'Hypnogram')}
    subjects = set()
    def issue(record, message):
        issues.append({'record_id': record, 'issue': message})
    for kind, paths in files.items():
        for path in paths:
            try:
                record, subject, subset = identity(path)
                groups[record][kind].append(path)
                if kind == 'PSG':
                    subjects.add(subject)
            except ValueError as exc:
                issue(str(path), str(exc))
    pair_count = 0
    for record, pair in sorted(groups.items()):
        if len(pair['PSG']) != 1 or len(pair['Hypnogram']) != 1:
            issue(record, f"Pareja incompleta o ambigua: {len(pair['PSG'])} PSG, {len(pair['Hypnogram'])} hipnogramas")
            continue
        pair_count += 1
        psg, hyp = pair['PSG'][0], pair['Hypnogram'][0]
        try:
            with pyedflib.EdfReader(str(psg)) as reader:
                duration = float(reader.file_duration)
                start = reader.getStartdatetime()
                headers = reader.getSignalHeaders()
            with pyedflib.EdfReader(str(hyp)) as reader:
                hyp_start = reader.getStartdatetime()
            offset = (hyp_start - start).total_seconds()
            annotations = mne.read_annotations(str(hyp))
            counts, excluded, unknown = epoch_labels(annotations, duration, offset)
            if offset:
                issue(record, f'Desfase hipnograma–PSG: {offset} s; corregido por cabeceras')
            if excluded:
                issue(record, f'{excluded} épocas sin etiqueta única que cubra 30 s completos')
            if unknown:
                issue(record, 'Etiquetas no reconocidas: ' + ', '.join(unknown))
            row = {'record_id': record, 'subject_id': record[:5], 'subset': record[:2],
                   'psg': str(psg), 'hypnogram': str(hyp), 'duration_s': duration,
                   'n_epochs_signal': int(duration // 30), 'n_epochs_labeled': sum(counts.values()),
                   'n_epochs_excluded': excluded, 'trailing_seconds': duration % 30,
                   'n_channels': len(headers)}
            records.append(row)
            for header in headers:
                channels.append({'record_id': record, 'channel': header['label'],
                                 'sfreq_hz': header['sample_frequency'], 'unit': header['dimension']})
            for label, count in counts.items():
                distributions.append({'record_id': record, 'subject_id': record[:5],
                                      'subset': record[:2], 'class': label, 'n_epochs': count})
        except Exception as exc:
            issue(record, f'Error de lectura: {type(exc).__name__}: {exc}')
    total_counts = {label: sum(row['n_epochs'] for row in distributions if row['class'] == label) for label in CLASSES}
    total = sum(total_counts.values())
    table = pd.DataFrame([{'class': label, 'n_epochs': count,
                           'percentage': 100 * count / total if total else 0.0}
                          for label, count in total_counts.items()])
    summary = {'data_dir': str(data_dir), 'n_psg_files': len(files['PSG']),
               'n_hypnogram_files': len(files['Hypnogram']), 'n_subjects_found': len(subjects),
               'n_record_ids_found': sum(bool(pair['PSG']) for pair in groups.values()),
               'n_pairs': pair_count, 'n_records_processed': len(records),
               'n_subjects_processed': len({row['subject_id'] for row in records}),
               'n_epochs_signal': sum(row['n_epochs_signal'] for row in records),
               'n_epochs_labeled': total,
               'n_epochs_excluded': sum(row['n_epochs_excluded'] for row in records),
               'n_issues': len(issues)}
    output_dir.mkdir(parents=True, exist_ok=True)
    frames = {'class_distribution': table,
              'records': pd.DataFrame(records, columns=['record_id', 'subject_id', 'subset', 'psg', 'hypnogram', 'duration_s', 'n_epochs_signal', 'n_epochs_labeled', 'n_epochs_excluded', 'trailing_seconds', 'n_channels']),
              'channels': pd.DataFrame(channels, columns=['record_id', 'channel', 'sfreq_hz', 'unit']),
              'classes_by_record': pd.DataFrame(distributions, columns=['record_id', 'subject_id', 'subset', 'class', 'n_epochs']),
              'issues': pd.DataFrame(issues, columns=['record_id', 'issue'])}
    for name, frame in frames.items():
        frame.to_csv(output_dir / f'{name}.csv', index=False)
    (output_dir / 'summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(table.to_string(index=False))
    if not files['PSG']:
        print(f'\nSin datos todavía. Coloca los EDF en {data_dir} y vuelve a ejecutar.')
    print(f'\nResultados: {output_dir}')
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=DATA_DIR)
    parser.add_argument('--output-dir', type=Path, default=PROJECT_DIR / 'outputs')
    args = parser.parse_args()
    try:
        summary = explore(args.data_dir.expanduser().resolve(), args.output_dir.expanduser().resolve())
    except ValueError as exc:
        parser.error(str(exc))
    return 1 if summary['n_issues'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
