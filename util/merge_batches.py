#!/usr/bin/env python
'''
  combine batch results into single array
'''

import argparse
import collections
import logging
import os
import sys

import csv

def add_signature(fn, samples, header, source, name):
  for row in csv.DictReader(open(fn, 'r'), delimiter='\t'):
    sample = row['Filename']
    del row['Filename'] # include everything but
    if 'Error' in row:
      row['SignatureError'] = row['Error']
      del row['Error']

    # figure the top sigs
    signature_names = [x for x in row.keys() if x not in ['Mutations', 'SignatureError']]
    signature_values = [float(row[name]) for name in signature_names]
    top = sorted(zip(signature_values, signature_names), reverse=True)
    row['{}_sigs'.format(name)] = ' '.join(['{} ({})'.format(x[1].replace('Signature.', '').replace('SBS', '').replace('ID', ''), x[0]) for x in top[:5]])

    samples['{}/{}'.format(sample, source)].update(row) # add results
    samples['{}/{}'.format(sample, source)]['source'] = source
    header.update(row.keys())

def main(directories, phenotype):
  logging.info('starting...')

  samples = collections.defaultdict(dict)
  header = set()


  for directory in directories:
    logging.info('parsing %s...', directory)
    source = os.path.basename(directory)

    # mutational_signatures_v2.filter.combined.tsv
    # mutational_signatures_v3_dbs.combined.tsv
    # mutational_signatures_v3_sbs.filter.combined.tsv
    # mutational_signatures_v3_id_strelka.filter.combined.tsv

    # targetted gene summary
    #fn = os.path.join(directory, 'out', 'aggregate', 'targetted_gene_summary.tsv')
    #if not os.path.isfile(fn):
    #  logging.info('skipping %s', directory)
    #else: 
    #  for row in csv.DictReader(open(fn, 'r'), delimiter='\t'):


    # signatures - v2
    fn = os.path.join(directory, 'out', 'aggregate', 'mutational_signatures_v2.filter.combined.tsv')
    if not os.path.isfile(fn):
      logging.info('skipping %s', directory)
      continue
    add_signature(fn, samples, header, source, 'v2')

    # v3 sbs signatures
    fn = os.path.join(directory, 'out', 'aggregate', 'mutational_signatures_v3_sbs.filter.combined.tsv')
    if not os.path.isfile(fn):
      logging.info('skipping %s', directory)
      continue
    add_signature(fn, samples, header, source, 'v3_SBS')

    # v3 id signatures
    fn = os.path.join(directory, 'out', 'aggregate', 'mutational_signatures_v3_id_strelka.filter.combined.tsv')
    if not os.path.isfile(fn):
      logging.info('skipping %s', directory)
      continue
    add_signature(fn, samples, header, source, 'v3_ID')

    # tmb
    fn = os.path.join(directory, 'out', 'aggregate', 'mutation_rate.tsv')
    for row in csv.DictReader(open(fn, 'r'), delimiter='\t'):
      sample = row['Filename'].split('/')[-1].split('.')[0]
      del row['Filename'] # include everything but
      samples['{}/{}'.format(sample, source)]['TMB'] = row['PerMB']
      header.add('TMB')

    # tmb with signature artefacts removed
    fn = os.path.join(directory, 'out', 'aggregate', 'mutation_rate.artefact_filter.tsv')
    for row in csv.DictReader(open(fn, 'r'), delimiter='\t'):
      sample = row['Filename'].split('/')[-1].split('.')[0]
      del row['Filename'] # include everything but
      samples['{}/{}'.format(sample, source)]['TMB.cleaned'] = row['PerMB']
      header.add('TMB.cleaned')

    # msisensor
    fn = os.path.join(directory, 'out', 'aggregate', 'msisensor.tsv')
    for row in csv.DictReader(open(fn, 'r'), delimiter='\t'):
      sample = row['Sample']
      del row['Sample'] # include everything but
      samples['{}/{}'.format(sample, source)]['MSISensor'] = row['%']
      header.add('MSISensor')

    # ontarget coverage
    fn = os.path.join(directory, 'out', 'aggregate', 'ontarget.tsv')
    for row in csv.DictReader(open(fn, 'r'), delimiter='\t'):
      sample = row['Filename'].split('/')[-1].split('.')[0]
      del row['Filename'] # include everything but
      samples['{}/{}'.format(sample, source)]['MeanOnTargetCoverage'] = row['Mean']
      header.add('MeanOnTargetCoverage')

  header.add('Phenotype')
  header.add('Category')
  for row in csv.DictReader(open(phenotype, 'r'), delimiter='\t'):
    for key in samples.keys():
      if key.startswith('{}/'.format(row['Sample Name'])):
        samples[key]['Phenotype'] = row['Phenotype']
        samples[key]['Category'] = row['Category']
        logging.debug('adding phenotype for %s', key)
      else:
        pass #logging.info('skipping phenotype for %s', row['Sample Name'])

  # now write everything to stdout
  sys.stdout.write('Sample\tSource\t{}\n'.format('\t'.join(sorted(list(header)))))
  for key in sorted(samples.keys()):
    sample, source = key.split('/')
    sys.stdout.write('{}\t{}\t{}\n'.format(sample, source, '\t'.join([samples[key].get(name, 'NA') for name in sorted(list(header))])))

  logging.info('done')

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='combine batch results')
  parser.add_argument('--directories', required=True, nargs='+', help='location of each batch')
  parser.add_argument('--phenotype', required=True, help='location of phenotype')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  main(args.directories, args.phenotype)