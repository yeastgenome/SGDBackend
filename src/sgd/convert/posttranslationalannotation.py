from src.sgd.convert.into_curate import basic_convert, remove_nones
from sqlalchemy.sql.expression import or_

__author__ = 'kpaskov'


def posttranslationalannotation_starter(bud_session_maker):

    header = True
    f = open('src/sgd/convert/data/phosphosites.txt', 'r')
    for line in f:
        row = line.strip().split('\t')
        if len(row) == 19:
            if header:
                header = False
            else:
                obj_json = {
                    'dbentity': {'systematic_name': row[0],
                                 'display_name': row[0]},
                    'source': {'display_name': 'PhosphoGRID'},
                    'site_index': int(row[2][1:]),
                    'site_residue': row[2][0],
                    'posttrans_type': 'phosphorylation'
                }

                if row[7] != '-':
                    obj_json['site_functions'] = row[7]

                if row[9] != '-':
                    obj_json['modifier'] = {'systematic_name': row[9].split('|')[0]}

                yield obj_json
    f.close()

    #Other sites
    file_names = ['src/sgd/convert/data/methylationSitesPMID25109467.txt',
                  'src/sgd/convert/data/ubiquitinationSites090314.txt',
                  'src/sgd/convert/data/phosphorylationUbiquitinationPMID23749301.txt',
                  'src/sgd/convert/data/succinylationAcetylation090914.txt']

    for file_name in file_names:
        print file_name
        f = open(file_name, 'rU')
        header = True
        for line in f:
            if header:
                header = False
            else:
                pieces = line.split('\t')
                site = pieces[1].strip()
                obj_json = remove_nones({
                    'dbentity': {'systematic_name': pieces[0],
                                 'display_name': pieces[0]},
                    'source': {'display_name': pieces[5]},
                    'site_index': int(site[1:]),
                    'site_residue': site[0],
                    'posttrans_type': pieces[3],
                    'site_functions': pieces[2],
                    'modification_type': pieces[3]
                })

                if pieces[4] != '':
                    obj_json['modifier'] = {'systematic_name': pieces[4]}
                if pieces[6] != '':
                    obj_json['reference'] = {'pubmed_id': int(pieces[6].replace('PMID:', ''))}
                if pieces[2] != '':
                    obj_json['site_functions'] = pieces[2]

                yield obj_json
        f.close()


def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, posttranslationalannotation_starter, 'posttranslationalannotation', lambda x: (x['dbentity']['systematic_name'], None if 'reference' not in x else x['reference']['pubmed_id'], x['site_residue'], x['site_index']))


if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')

