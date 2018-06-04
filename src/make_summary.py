#!/usr/bin/env python
'''
  summarize the analysis
'''

import argparse
import collections
import logging
import os.path
import sys

DEAMINATION_THRESHOLD = 30
OXOG_THRESHOLD = 30

def main(samples):
  logging.info('starting...')

  results = collections.defaultdict(dict)
  issues = 0
  for sample_filename in samples:
    # the actual sample name
    sample = os.path.basename(sample_filename).split('.')[0]
    logging.debug('Sample is %s', sample)
    sample_prefix = os.path.join(os.path.dirname(sample_filename), sample)
    with open('{}.artifact_metrics.txt.pre_adapter_summary_metrics'.format(sample_prefix), 'r') as fh:
      # SAMPLE_ALIAS    LIBRARY REF_BASE        ALT_BASE        TOTAL_QSCORE    WORST_CXT       WORST_CXT_QSCORE        WORST_PRE_CXT   WORST_PRE_CXT_QSCORE    WORST_POST_CXT  WORST_POST_CXT_QSCORE   ARTIFACT_NAME
      # OHI005001_T     UnknownLibrary  A       C       100     CAC     56      AAN     100     NAC     62      NA
      to_find = 2
      results[sample]['Issues'] = []
      for line in fh:
        fields = line.strip('\n').split('\t')
        if len(fields) < 12:
          continue
        if fields[11] == 'Deamination':
          results[sample]['Deamination'] = float(fields[4]) # TOTAL_QSCORE
          if results[sample]['Deamination'] <= DEAMINATION_THRESHOLD:
            results[sample]['Issues'].append('deamination')
            issues += 1
          to_find -= 1
        elif fields[11] == 'OxoG':
          results[sample]['OxoG'] = float(fields[4]) 
          if results[sample]['OxoG'] <= OXOG_THRESHOLD:
            results[sample]['Issues'].append('oxog')
            issues += 1
          to_find -= 1
      if to_find != 0:
        logging.warn('%i results not found for %s', found, sample)

  # write results
  sys.stdout.write('{}\t{}\t{}\t{}\n'.format('Sample', 'Deamination', 'OxoG', 'Issues'))
  for sample in sorted(results):
    sys.stdout.write('{}\t{}\t{}\t{}\n'.format(sample, results[sample]['Deamination'], results[sample]['OxoG'], ','.join(results[sample]['Issues'])))

  logging.info('done. %i issues for %i samples', issues, len(results))

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Assess MSI')
  parser.add_argument('--samples', required=True, nargs='+', help='sample names')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  main(args.samples)


