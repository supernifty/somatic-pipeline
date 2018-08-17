#!/usr/bin/env python

import argparse
import numpy as np
import re
import sys

from cyvcf2 import VCF, Writer

def __main__():
   parser = argparse.ArgumentParser(description='Convert a VCF file with genomic variants to a file with tab-separated values (TSV). One entry (TSV line) per sample genotype', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
   parser.add_argument('query_vcf', help='Bgzipped input VCF file with query variants (SNVs/InDels)')
   parser.add_argument("--skip_info_data",action = "store_true", help="Skip printing of data in INFO column")
   parser.add_argument("--skip_genotype_data", action="store_true", help="Skip printing of genotype_data (FORMAT columns)")
   parser.add_argument("--keep_rejected_calls", action="store_true", help="Print data for rejected calls")
   parser.add_argument("--print_data_type_header", action="store_true", help="Print a header line with data types of VCF annotations")
   args = parser.parse_args()
   
   vcf2tsv(args.query_vcf, args.skip_info_data, args.skip_genotype_data, args.keep_rejected_calls, args.print_data_type_header)
         

def vcf2tsv(query_vcf, skip_info_data, skip_genotype_data, keep_rejected_calls, print_data_type_header):
   
   vcf = VCF(query_vcf, gts012 = True)
   out = sys.stdout
   
   fixed_columns_header = ['CHROM','POS','ID','REF','ALT','QUAL','FILTER']
   fixed_columns_header_type = ['String','Integer','String','String','String','Float','String']
   samples = vcf.samples
   info_columns_header = []
   format_columns_header = []
   sample_columns_header = []
   column_types = {}
   gt_present_header = 0
   
   if len(samples) > 0:
      sample_columns_header.append('VCF_SAMPLE_ID')
   
   for e in vcf.header_iter():
      header_element = e.info()
      if 'ID' in header_element.keys() and 'HeaderType' in header_element.keys():
         if header_element['HeaderType'] == 'INFO' or header_element['HeaderType'] == 'FORMAT':
            column_types[header_element['ID']] = header_element['Type']
         if header_element['HeaderType'] == 'INFO':
            if skip_info_data is False:
               info_columns_header.append(header_element['ID'])
         if header_element['HeaderType'] == 'FORMAT':
            if len(sample_columns_header) > 0 and skip_genotype_data is False:
               if header_element['ID'] != 'GT':
                  format_columns_header.append(header_element['ID'])
               else:
                  gt_present_header = 1

   header_line = '\t'.join(fixed_columns_header)
   if skip_info_data is False:
      header_line = '\t'.join(fixed_columns_header) + '\t' + '\t'.join(sorted(info_columns_header))
      if len(sample_columns_header) > 0:
         if skip_genotype_data is False:
            header_line = '\t'.join(fixed_columns_header) + '\t' + '\t'.join(sorted(info_columns_header)) + '\t' + '\t'.join(sample_columns_header) + '\t' + '\t'.join(sorted(format_columns_header)) + '\tGT'
         else:
            header_line = '\t'.join(fixed_columns_header) + '\t' + '\t'.join(sorted(info_columns_header))
   else:
      if len(sample_columns_header) > 0:
         if skip_genotype_data is False:
            header_line = '\t'.join(fixed_columns_header) + '\t' + '\t'.join(sample_columns_header) + '\t' + '\t'.join(sorted(format_columns_header)) + '\tGT'
         else:
            header_line = '\t'.join(fixed_columns_header)
            
   if print_data_type_header is True:
      header_tags = header_line.rstrip().split('\t')
      header_types = []
      for h in header_tags:
         if h in column_types:
            header_types.append(str(column_types[h]))
      header_line_type = '\t'.join(fixed_columns_header_type) + '\t' + '\t'.join(header_types)
      out.write('#' + str(header_line_type) + '\n')
      out.write(str(header_line) + '\n')
   else:
      out.write(str(header_line) + '\n')
   
   for rec in vcf:
      rec_id = '.'
      rec_qual = '.'
      rec_filter = '.'
      alt = ",".join(str(n) for n in rec.ALT)
      if not rec.ID is None:
         rec_id = str(rec.ID)
      if not rec.QUAL is None:
         rec_qual = str("{0:.2f}".format(rec.QUAL))
      rec_filter = str(rec.FILTER)
      if rec.FILTER is None:
         rec_filter = 'PASS'
     
      pos = int(rec.start) + 1
      fixed_fields_string = str(rec.CHROM) + '\t' + str(pos) + '\t' + str(rec_id) + '\t' + str(rec.REF) + '\t' + str(alt) + '\t' + str(rec_qual) + '\t' + str(rec_filter)
      
      
      if not 'PASS' in rec_filter and not keep_rejected_calls:
         continue
      
      variant_info = rec.INFO
      vcf_info_data = []
      if skip_info_data is False:
         for info_field in sorted(info_columns_header):
            if column_types[info_field] == 'Flag':
               if variant_info.get(info_field) is None:
                  vcf_info_data.append('False')
               else:
                  vcf_info_data.append('True')
            elif column_types[info_field] == 'Float' or column_types[info_field] == 'Integer' or column_types[info_field] == 'String' or column_types[info_field] == 'Character':
               if type(variant_info.get(info_field)) is list or type(variant_info.get(info_field)) is tuple:
                  vcf_info_data.append(",".join(str(n) for n in variant_info.get(info_field)))
               else:
                  if variant_info.get(info_field) is None:
                     vcf_info_data.append('.')
                  else:
                     if column_types[info_field] == 'Float':
                        if not isinstance(variant_info.get(info_field),float):
                           print('vcf2tsv.py WARNING:\tINFO tag ' + str(info_field) + ' is defined in the VCF header as type \'Float\', yet parsed as other type:' + str(type(variant_info.get(info_field))))
                           if not ',' in str(alt):
                              print('Warning: Multiple values in INFO tag for single ALT allele (VCF multiallelic sites not decomposed properly?):' + str(fixed_fields_string) + '\t' + str(info_field) + '=' + str(variant_info.get(info_field)))
                           vcf_info_data.append('.')
                        else:
                           val = str("{0:.7f}".format(variant_info.get(info_field)))
                           vcf_info_data.append(val)
                     else:
                        if column_types[info_field] == 'String' or column_types[info_field] == 'Character':
                           if isinstance(variant_info.get(info_field),str):
                              #print(str(info_field) + '\t' + variant_info.get(info_field).encode('ascii','ignore').rstrip().decode('ascii'))
                              vcf_info_data.append(variant_info.get(info_field).encode('ascii','ignore').decode('ascii'))
                           else:
                              vcf_info_data.append('.')
                              if column_types[info_field] == 'String':
                                    print('vcf2tsv.py WARNING:\tINFO tag ' + str(info_field) + ' is defined in the VCF header as type \'String\', yet parsed as other type:' + str(type(variant_info.get(info_field))))
                              if column_types[info_field] == 'Character':
                                    print('vcf2tsv.py WARNING:\tINFO tag ' + str(info_field) + ' is defined in the VCF header as type \'Character\', yet parsed as other type:' + str(type(variant_info.get(info_field))))
                        else:
                           if isinstance(variant_info.get(info_field),int):
                              vcf_info_data.append(str(variant_info.get(info_field)))
                           else:
                              print('vcf2tsv.py WARNING:\tINFO tag ' + str(info_field) + ' is defined in the VCF header as type \'Integer\', yet parsed as other type:' + str(type(variant_info.get(info_field))))
                              vcf_info_data.append(re.sub('\(|\)', '', variant_info.get(info_field).encode('ascii','ignore').decode('ascii')))

      #print(str(vcf_info_data))
      #dictionary, with sample names as keys, values being genotype data (dictionary with format tags as keys)
      vcf_sample_genotype_data = {}
      if len(samples) > 0 and skip_genotype_data is False:
         gt_cyvcf = rec.gt_types
         i = 0
         while i < len(samples):
            vcf_sample_genotype_data[samples[i]] = {}
            gt = './.'
            if gt_present_header == 1:
               if gt_cyvcf[i] == 0:
                  gt = '0/0'
               if gt_cyvcf[i] == 1:
                  gt = '0/1'
               if gt_cyvcf[i] == 2:
                  gt = '1/1'
            vcf_sample_genotype_data[samples[i]]['GT'] = gt
            i = i + 1
               
      for format_tag in sorted(format_columns_header):
         if len(samples) > 0 and skip_genotype_data is False:
            sample_dat = rec.format(format_tag)
            if sample_dat is None:
               k = 0
               while k < len(samples):
                  if samples[k] in vcf_sample_genotype_data:
                     vcf_sample_genotype_data[samples[k]][format_tag] = '.'
                  k = k + 1               
               continue
            dim = sample_dat.shape
            j = 0
            ## sample-wise
            while j < dim[0]:
               if sample_dat[j].size > 1:
                  d = ','.join(str(e) for e in np.ndarray.tolist(sample_dat[j]))
                  if samples[j] in vcf_sample_genotype_data:
                     vcf_sample_genotype_data[samples[j]][format_tag] = d
               else:
                  d = '.'
                  if column_types[format_tag] == 'String':
                     d = str(sample_dat[j])
                  if column_types[format_tag] == 'Integer':
                     d = str(sample_dat[j][0])
                  if samples[j] in vcf_sample_genotype_data:
                     vcf_sample_genotype_data[samples[j]][format_tag] = d
               j = j + 1
      
      #print(str(vcf_sample_genotype_data))
      tsv_elements = []
      tsv_elements.append(fixed_fields_string)
      if skip_info_data is False:
         if skip_genotype_data is False:
            if len(sample_columns_header) > 0:
               tsv_elements.append("\t".join(str(n) for n in vcf_info_data))
               ## one line per sample variant
               for s in sorted(vcf_sample_genotype_data.keys()):
                  sample = s
                  line_elements = []
                  line_elements.extend(tsv_elements)
                  line_elements.append(sample)
                  gt_tag = '.'
                  for tag in sorted(vcf_sample_genotype_data[sample].keys()):
                     if tag != 'GT':
                        line_elements.append(vcf_sample_genotype_data[sample][tag].encode('ascii','ignore').decode('ascii'))
                     else:
                        gt_tag = vcf_sample_genotype_data[sample][tag].encode('ascii','ignore').decode('ascii')
                  line_elements.append(gt_tag)
                  if gt_tag == './.' or gt_tag == '.':
                     if keep_rejected_calls:
                        out.write('\t'.join(line_elements) + '\n')
                  else:
                     out.write("\t".join(str(n) for n in line_elements) + '\n')
                    
            else:
               tsv_elements.append("\t".join(str(n) for n in vcf_info_data))
               line_elements = []
               line_elements.extend(tsv_elements)
               out.write('\t'.join(line_elements) + '\n')
         else:
            tsv_elements.append("\t".join(str(n) for n in vcf_info_data))
            line_elements = []
            line_elements.extend(tsv_elements)
            out.write('\t'.join(line_elements) + '\n')
      else:
         if skip_genotype_data is False:
            if len(sample_columns_header) > 0:
               ## one line per sample variant
               for s in sorted(vcf_sample_genotype_data.keys()):
                  sample = s
                  line_elements = []
                  line_elements.extend(tsv_elements)
                  line_elements.append(sample)
                  gt_tag = '.'
                  for tag in sorted(vcf_sample_genotype_data[sample].keys()):
                     if tag != 'GT':
                        line_elements.append(vcf_sample_genotype_data[sample][tag])
                     else:
                        gt_tag = vcf_sample_genotype_data[sample][tag]
                  line_elements.append(gt_tag)
                  if gt_tag == './.' or gt_tag == '.':
                     if keep_rejected_calls:
                        out.write('\t'.join(line_elements) + '\n')
                  else:
                     out.write('\t'.join(line_elements) + '\n')
         else:
            line_elements = []
            line_elements.extend(tsv_elements)
            line_elements = tsv_elements
            out.write('\t'.join(line_elements) + '\n')
   
if __name__=="__main__": __main__()


   
