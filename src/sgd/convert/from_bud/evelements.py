from sqlalchemy.orm import joinedload

from src.sgd.convert.transformers import make_file_starter, \
    make_obo_file_starter
from src.sgd.convert import create_format_name


__author__ = 'kpaskov'

#Recorded times: 
#Maitenance (cherry-vm08): 0:01, 
#First Load (sgd-ng1): :09, :10
#1.23.14 Maitenance (sgd-dev): :06

# --------------------- Convert Experiment ---------------------
def make_experiment_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.bud.cv import CVTerm

    def experiment_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        for bud_obj in make_obo_file_starter('src/sgd/convert/data/eco.obo')():
            yield {'display_name': bud_obj['name'],
                   'source': key_to_source['ECO'],
                   'description': None if 'def' not in bud_obj else bud_obj['def'],
                   'eco_id': bud_obj['id']}

        for bud_obj in bud_session.query(CVTerm).filter(CVTerm.cv_no==7).all():
            format_name = create_format_name(bud_obj.name)
            yield {'display_name': bud_obj.name,
                   'source': key_to_source['SGD'],
                   'description': bud_obj.definition,
                   'category': 'large-scale survey' if format_name in large_scale_survey else 'classical genetics' if format_name in classical_genetics else None,
                   'date_created': bud_obj.date_created,
                   'created_by': bud_obj.created_by}

        for row in make_file_starter('src/sgd/convert/data/2014-05-15_reg_data/Venters_Macisaac_Hu05-12-2014_regulator_lines')():
            source_key = row[11].strip()
            if source_key in key_to_source:
                yield {'display_name': row[4] if row[4] != '' else row[5],
                       'source': None if source_key not in key_to_source else key_to_source[source_key],
                       'eco_id': row[5]}
            else:
                print 'Source not found: ' + str(source_key)

        for row in make_file_starter('src/sgd/convert/data/2014-05-15_reg_data/SGD_data_05_14_2014')():
            source_key = row[11].strip()
            if source_key in key_to_source:
                yield {'display_name': row[4] if row[4] != '' else row[5],
                       'source': None if source_key not in key_to_source else key_to_source[source_key],
                       'eco_id': row[5]}
            else:
                print 'Source not found: ' + str(source_key)

        for row in make_file_starter('src/sgd/convert/data/2014-05-15_reg_data/Madhani_fixed')():
            if len(row) >= 10:
                if source_key in key_to_source:
                    source_key = row[11].strip()
                    yield {'display_name': row[4] if row[4] != '' else row[5],
                           'source': None if source_key not in key_to_source else key_to_source[source_key],
                           'eco_id': row[5]}
                else:
                    print 'Source not found: ' + str(source_key)

        for row in make_file_starter('src/sgd/convert/data/2014-05-15_reg_data/Pimentel_PMID22616008.txt')():
            if len(row) >= 10:
                if source_key in key_to_source:
                    source_key = row[11].strip()
                    yield {'display_name': row[4] if row[4] != '' else row[5],
                           'source': None if source_key not in key_to_source else key_to_source[source_key],
                           'eco_id': row[5]}
                else:
                    print 'Source not found: ' + str(source_key)

        for row in make_file_starter('src/sgd/convert/data/yetfasco_data.txt', delimeter=';')():
            yield {'display_name': row[9][1:-1],
                   'source': key_to_source['YeTFaSCo']}

        for row in make_file_starter('src/sgd/convert/data/phosphosites.txt', delimeter=';')():
            if len(row) > 3:
                for display_name in row[3].split('|'):
                    yield {'display_name': display_name,
                           'source': key_to_source['PhosphoGRID']}

        yield {'display_name': 'protein abundance',
               'source': key_to_source['SGD']}

        yield {'display_name': 'EXP', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/exp-inferred-experiment', 'description': 'Inferred from Experiment'}
        yield {'display_name': 'IDA', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/ida-inferred-direct-assay', 'description': 'Inferred from Direct Assay'}
        yield {'display_name': 'IPI', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/ipi-inferred-physical-interaction', 'description': 'Inferred from Physical Interaction'}
        yield {'display_name': 'IMP', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/imp-inferred-mutant-phenotype', 'description': 'Inferred from Mutant Phenotype'}
        yield {'display_name': 'IGI', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/igi-inferred-genetic-interaction', 'description': 'Inferred from Genetic Interaction'}
        yield {'display_name': 'IEP', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/iep-inferred-expression-pattern', 'description': 'Inferred from Expression Pattern'}
        yield {'display_name': 'ISS', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/iss-inferred-sequence-or-structural-similarity', 'description': 'Inferred from Sequence or Structural Similarity'}
        yield {'display_name': 'ISA', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/isa-inferred-sequence-alignment', 'description': 'Inferred from Sequence Alignment'}
        yield {'display_name': 'ISO', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/iso-inferred-sequence-orthology', 'description': 'Inferred from Sequence Orthology'}
        yield {'display_name': 'ISM', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/ism-inferred-sequence-model', 'description': 'Inferred from Sequence Model'}
        yield {'display_name': 'IGC', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/igc-inferred-genomic-context', 'description': 'Inferred from Genomic Context'}
        yield {'display_name': 'IBA', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/iba-inferred-biological-aspect-ancestor', 'description': 'Inferred from Biological aspect of Ancestor'}
        yield {'display_name': 'IBD', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/ibd-inferred-biological-aspect-descendent', 'description': 'Inferred from Biological aspect of Descendent'}
        yield {'display_name': 'IKR', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/ikr-inferred-key-residues', 'description': 'Inferred from Key Residues'}
        yield {'display_name': 'IRD', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/ird-inferred-rapid-divergence', 'description': 'Inferred from Rapid Divergence'}
        yield {'display_name': 'RCA', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/rca-inferred-reviewed-computational-analysis', 'description': 'inferred from Reviewed Computational Analysis'}
        yield {'display_name': 'TAS', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/tas-traceable-author-statement', 'description': 'Traceable Author Statement'}
        yield {'display_name': 'NAS', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/nas-non-traceable-author-statement', 'description': 'Non-traceable Author Statement'}
        yield {'display_name': 'IC', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/ic-inferred-curator', 'description': 'Inferred by Curator'}
        yield {'display_name': 'ND', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/nd-no-biological-data-available', 'description': 'No Biological Data Available'}
        yield {'display_name': 'IEA', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/automatically-assigned-evidence-codes', 'description': 'Inferred from Electronic Annotation'}

        bud_session.close()
        nex_session.close()
    return experiment_starter

large_scale_survey = {'large-scale_survey', 'competitive_growth', 'heterozygous_diploid,_large-scale_survey', 'homozygous_diploid,_large-scale_survey', 'systematic_mutation_set', 'heterozygous_diploid,_competitive_growth',
                      'homozygous_diploid,_competitive_growth', 'heterozygous_diploid,_systematic_mutation_set', 'homozygous_diploid,_systematic_mutation_set'}
classical_genetics = {'classical_genetics', 'heterozygous_diploid', 'homozygous_diploid'}

# --------------------- Convert Experiment Alias ---------------------
def make_experiment_alias_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source, Experiment
    from src.sgd.model.nex import create_format_name
    from src.sgd.model.bud.cv import CVTerm
    def experiment_alias_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_experiment = dict([(x.unique_key(), x) for x in nex_session.query(Experiment).all()])
        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        for old_cv_term in bud_session.query(CVTerm).filter(CVTerm.cv_no==7).options(joinedload('cv_dbxrefs'), joinedload('cv_dbxrefs.dbxref')).all():
            experiment_key = create_format_name(old_cv_term.name)
            if experiment_key in key_to_experiment:
                for dbxref in old_cv_term.dbxrefs:
                    yield {'display_name': dbxref.dbxref_id,
                           'source': key_to_source['SGD'],
                           'category': 'APOID',
                           'experiment_id': key_to_experiment[experiment_key].id,
                           'date_created': dbxref.date_created,
                           'created_by': dbxref.created_by}
            else:
                print 'Experiment does not exist: ' + str(experiment_key)
                yield None

        bud_session.close()
        nex_session.close()
    return experiment_alias_starter

# --------------------- Convert Experiment Relation ---------------------
def make_experiment_relation_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source, Experiment
    from src.sgd.model.nex import create_format_name
    from src.sgd.model.bud.cv import CVTerm
    def experiment_relation_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_experiment = dict([(x.unique_key(), x) for x in nex_session.query(Experiment).all()])
        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        for old_cv_term in bud_session.query(CVTerm).filter(CVTerm.cv_no==7).options(joinedload('parent_rels'), joinedload('parent_rels.parent')).all():
            child_key = create_format_name(old_cv_term.name)
            for parent_rel in old_cv_term.parent_rels:
                parent_key = create_format_name(parent_rel.parent.name)
                if parent_key in key_to_experiment and child_key in key_to_experiment:
                    yield {'source': key_to_source['SGD'],
                           'parent_id': key_to_experiment[parent_key].id,
                           'child_id': key_to_experiment[child_key].id,
                           'date_created': parent_rel.date_created,
                           'created_by': parent_rel.created_by}
                else:
                    print 'Experiment does not exist: ' + str(parent_key) + ' ' + str(child_key)

        bud_session.close()
        nex_session.close()
    return experiment_relation_starter

# --------------------- Convert Strain ---------------------
alternative_reference_strains = {'CEN.PK', 'D273-10B', 'FL100', 'JK9-3d', 'RM11-1a', 'SEY6210', 'SK1', 'Sigma1278b', 'W303', 'X2180-1A', 'Y55'}

strain_to_genotype = {'S288C': '<i>MAT&alpha; SUC2 gal2 mal2 mel flo1 flo8-1 hap1 ho bio1 bio6</i>',
                      'BY4743': '<i>MAT</i>a<i>/&alpha; his3&Delta;1/his3&Delta;1 leu2&Delta;0/leu2&Delta;0 LYS2/lys2&Delta;0 met15&Delta;0/MET15 ura3&Delta;0/ura3&Delta;0</i>',
                      'FY4': '<i>MAT</i>a',
                      'DBY12020': '<i>MAT<b>a</b>(P<sub>GAL10</sub>+gal1)&Delta;::loxP, leu2&Delta;0::P<sub>ACT1</sub>-GEV-NatMX, gal4&Delta;::LEU2, HAP1<sup>+</sup></i>',
                      'DBY12021': '<i>MAT<b>&alpha;</b>(P<sub>GAL10</sub>+gal1)&Delta;::loxP, leu2&Delta;0::P<sub>ACT1</sub>-GEV-NatMX, gal4&Delta;::LEU2, HAP1<sup>+</sup></i>',
                      'FY1679': '<i>MAT</i>a<i>/&alpha; ura3-52/ura3-52 trp1&Delta;63/TRP1 leu2&Delta;1/LEU2 his3&Delta;200/HIS3 GAL2/GAL</i>',
                      'AB972': '<i>MAT&alpha; X2180-1B trp1<sub>0</sub> [rho<sup>0</sup>]</i>',
                      'A364A': '<i>MAT</i>a<i> ade1 ade2 ura1 his7 lys2 tyr1 gal1 SUC mal cup BIO</i>',
                      'XJ24-24a': '<i>MAT</i>a<i> ho HMa HM&alpha; ade6 arg4-17 trp1-1 tyr7-1 MAL2</i>',
                      'DC5': '<i>MAT</i>a<i> leu2-3,112 his3-11,15 can1-11</i>',
                      'X2180-1A': '<i>MAT</i>a<i> SUC2 mal mel gal2 CUP1</i>',
                      'YNN216': '<i>MAT</i>a<i>/&alpha; ura3-52/ura3-52 lys2-801<sup>amber</sup>/lys2-801<sup>amber</sup> ade2-101<sup>ochre</sup>/ade2-101<sup>ochre</sup></i>',
                      'YPH499': '<i>MAT</i>a<i> ura3-52 lys2-801_amber ade2-101_ochre trp1-&Delta;63 his3-&Delta;200 leu2-&Delta;1</i>',
                      'YPH500': '<i>MAT&alpha; ura3-52 lys2-801_amber ade2-101_ochre trp1-&Delta;63 his3-&Delta;200 leu2-&Delta;1</i>',
                      'YPH501': '<i>MAT</i>a<i>/MAT&alpha; ura3-52/ura3-52 lys2-801_amber/lys2-801_amber ade2-101_ochre/ade2-101_ochre trp1-&Delta;63/trp1-&Delta;63 his3-&Delta;200/his3-&Delta;200 leu2-&Delta;1/leu2-&Delta;1</i>',
                      'SK1': '<i>MAT</i>a<i>/&alpha; HO gal2 cup<sup>S</sup> can1<sup>R</sup> BIO</i>',
                      'CENPK': '<i>MAT</i>a<i>/&alpha; ura3-52/ura3-52 trp1-289/trp1-289 leu2-3_112/leu2-3_112 his3 &Delta;1/his3 &Delta;1 MAL2-8C/MAL2-8C SUC2/SUC2</i>',
                      'W303': '<i>MAT</i>a<i>/MAT&alpha; {leu2-3,112 trp1-1 can1-100 ura3-1 ade2-1 his3-11,15} [phi<sup>+</sup>]</i>',
                      'W303-1A': '<i>MAT</i>a<i> {leu2-3,112 trp1-1 can1-100 ura3-1 ade2-1 his3-11,15}</i>',
                      'W303-1B': '<i>MAT&alpha; {leu2-3,112 trp1-1 can1-100 ura3-1 ade2-1 his3-11,15}</i>',
                      'W303-K6001': '<i>MAT</i>a<i>; {ade2-1, trp1-1, can1-100, leu2-3,112, his3-11,15, GAL, psi+, ho::HO::CDC6 (at HO), cdc6::hisG, ura3::URA3 GAL-ubiR-CDC6 (at URA3)}</i>',
                      'DY1457': '<i>MAT</i>a<i>; {ade6 can1-100(oc) his3-11,15 leu2-3,112 trp1-1 ura3-52}</i>',
                      'D273-10B': '<i>MAT&alpha; mal</i>',
                      'FL100': '<i>MAT</i>a',
                      'SEY6210/SEY6211': '<i>MAT</i>a<i>/MAT&alpha; leu2-3,112/leu2-3,112 ura3-52/ura3-52 his3-&Delta;200/his3-&Delta;200 trp1-&Delta;901/trp1-&Delta;901 ade2/ADE2 suc2-&Delta;9/suc2-&Delta;9 GAL/GAL LYS2/lys2-801</i>',
                      'SEY6210': '<i>MAT&alpha; leu2-3,112 ura3-52 his3-&Delta;200 trp1-&Delta;901 suc2-&Delta;9 lys2-801; GAL</i>',
                      'SEY6211': '<i>MAT</i>a<i> leu2-3,112 ura3-52 his3-&Delta;200 trp1-&Delta;901 ade2-101 suc2-&Delta;9; GAL</i>',
                      'JK9-3d': 'JK9-3da <i>MAT</i>a<i> leu2-3,112 ura3-52 rme1 trp1 his4</i><br>JK9-3d&alpha; has the same genotype as JK9-3da with the exception of the MAT locus<br>JK9-3da/&alpha; is homozygous for all markers except mating type',
                      'RM11-1a': '<i>MAT</i>a<i> leu2&Delta;0 ura3-&Delta;0 HO::kanMX</i>',
                      'Y55': '<i>MAT</i>a<i>/MATalpha HO/HO</i>',
                      'BY4741': 'MATa his3&Delta;1 leu2&Delta;0 met15&Delta;0 ura3&Delta;0',
                      'BY4742': 'MAT&alpha; his3&Delta;1 leu2&Delta;0 lys2&Delta;0 ura3&Delta;0',
                      'FY1679': 'MATa/&alpha; ura3-52/ura3-52 trp1&Delta;63/TRP1 leu2&Delta;1/LEU2 his3&Delta;200/HIS3 GAL2/GAL2'
}

strain_to_description = {'S288C': 'Reference Genome',
                        'Other': 'Strain background is designated "Other" when the genetic background of the strain used in an experiment supporting a particular annotation is either not traceable or is not one of the twelve most commonly used backgrounds that are recorded in SGD curation.'}

def make_strain_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.bud.cv import CVTerm
    def strain_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        for bud_obj in bud_session.query(CVTerm).filter(CVTerm.cv_no==10).all():
            yield {'display_name': bud_obj.name,
                   'source': key_to_source['SGD'],
                   'description': bud_obj.definition if bud_obj.name not in strain_to_description else strain_to_description[bud_obj.name],
                   'status': 'Reference' if bud_obj.name == 'S288C' else ('Alternative Reference' if bud_obj.name in alternative_reference_strains else (None if bud_obj.name == 'Other' else 'Other')),
                   'genotype': None if bud_obj.name not in strain_to_genotype else strain_to_genotype[bud_obj.name],
                   'date_created': bud_obj.date_created,
                   'created_by': bud_obj.created_by}

        other_strains = [('10560-6B', 'Sigma1278b-derivative laboratory strain'),
                                   ('AB972', 'Isogenic to S288C; used in the systematic sequencing project, the sequence stored in SGD. AB972 is an ethidium bromide-induced rho- derivative of the strain X2180-1B-trp1.'),
                                   ('A364A', 'Used in the systematic sequencing project, the sequence stored in SGD'),
                                   ('AWRI1631', 'Haploid derivative of South African commercial wine strain N96'),
                                   ('AWRI796', 'South African red wine strain'),
                                   ('BC187', 'Derivative of California wine barrel isolate'),
                                   ('BY4741', 'S288C-derivative laboratory strain'),
                                   ('BY4742', 'S288C-derivative laboratory strain'),
                                   ('BY4743', 'Strain used in the systematic deletion project, generated from a cross between BY4741 and BY4742, which are derived from S288C. As in S288c, this strain as well as haploid derivatives BY4741, and BY4742 have allelic variants of MIP1, SAL1 and CAT5 and these polymorphisms, described in the respective locus history notes for these genes (MIP1, SAL1 and CAT5) all contribute to the high observed petite frequency.'),
                                   ('CBS7960', 'Brazilian bioethanol factory isolate'),
                                   ('CLIB215', 'New Zealand bakery isolate'),
                                   ('CLIB324', 'Vietnamese bakery isolate'),
                                   ('CLIB382', 'Irish beer isolate'),
                                   ('D273', 'Laboratory strain'),
                                   ('D273-10B', 'Normal cytochrome content and respiration; low frequency of rho-. This strain and its auxotrophic derivatives were used in numerious laboratories for mitochondrial and related studies and for mutant screens. Good respirer that\'s relatively resistant to glucose repression.'),
                                   ('DBVPG6044', 'West African isolate'),
                                   ('DBY12020', 'Derived from FY4'),
                                   ('DBY12021', 'Derived from FY4'),
                                   ('DC5', 'Isogenic to S288C; used in the systematic sequencing project, the sequence stored in SGD'),
                                   ('DY1457', ''),
                                   ('EC1118', 'Commercial wine strain'),
                                   ('EC9-8', 'Haploid derivative of Israeli canyon isolate'),
                                   ('FL100', 'Laboratory strain'),
                                   ('FostersB', 'Commercial ale strain'),
                                   ('FostersO', 'Commercial ale strain'),
                                   ('FY4', 'Derived from S288C'),
                                   ('FY1679', 'S288C-derivative laboratory strain'),
                                   ('JAY291', 'Haploid derivative of Brazilian industrial bioethanol strain PE-2'),
                                   ('JK9', 'Laboratory strain'),
                                   ('JK9-3d', 'JK9-3d was constructed by Jeanette Kunz while in Mike Hall\'s lab. She made the original strain while Joe Heitman isolated isogenic strains of opposite mating type and derived the a/alpha isogenic diploid by mating type switching. It has in its background S288c, a strain from the Oshima lab, and a strain from the Herskowitz lab. It was chosen because of its robust growth and sporulation, as well as good growth on galactose (GAL+) (so that genes under control of the galactose promoter could be induced). It may also have a SUP mutation that allows translation through premature STOP codons and therefore produces functional alleles with many point mutations.'),
                                   ('K11', 'Sake strain'),
                                   ('Kyokai7', 'Japanese sake yeast'),
                                   ('L1528', 'Chilean wine strain'),
                                   ('LalvinQA23', 'Portuguese Vinho Verde white wine strain'),
                                   ('M22', 'Italian vineyard isolate'),
                                   ('PW5', 'Nigerian Raphia palm wine isolate'),
                                   ('RedStar', 'Commercial baking strain'),
                                   ('SEY', 'Laboratory strain'),
                                   ('SEY6210', 'SEY6210 is a MATalpha haploid constructed by Scott Emr and has been used in studies of autophagy, protein sorting etc. It is the product of crossing with strains from 5 different labs (Gerry Fink, Ron Davis, David Botstein, Fred Sherman, Randy Schekman). It has several selectable markers and good growth properties.'),
                                   ('SEY6211', 'SEY6211 is a MATa haploid constructed by Scott Emr and has been used in studies of autophagy, protein sorting etc. It is the product of crossing with strains from 5 different labs (Gerry Fink, Ron Davis, David Botstein, Fred Sherman, Randy Schekman). It has several selectable markers and good growth properties.'),
                                   ('SEY6210/SEY6211', 'SEY6210/SEY6211, also known as SEY6210.5, was constructed by Scott Emr and has been used in studies of autophagy, protein sorting etc. It is the product of crossing with strains from 5 different labs (Gerry Fink, Ron Davis, David Botstein, Fred Sherman, Randy Schekman). It has several selectable markers, good growth properties and good sporulation.'),
                                   ('SK1', 'Laboratory strain'),
                                   ('T7', 'Missouri oak tree exudate isolate'),
                                   ('T73', 'Spanish red wine strain'),
                                   ('UC5', 'Japanese sake yeast'),
                                   ('UWOPSS', 'Environmental isolate'),
                                   ('VIN13', 'South African white wine strain'),
                                   ('VL3', 'French white wine strain'),
                                   ('W303', 'Laboratory strain'),
                                   ('W303-1A', 'W303-1A possesses a ybp1-1 mutation (I7L, F328V, K343E, N571D) which abolishes Ybp1p function, increasing sensitivity to oxidative stress.'),
                                   ('W303-1B', ''),
                                   ('W303-K6001', ''),
                                   ('X2180', 'S288C-derivative laboratory strain'),
                                   ('X2180-1A', 'S288c spontaneously diploidized to give rise to X2180. The haploid segregants X2180-1a and X2180-1b were obtained from sporulated X2180.'),
                                   ('XJ24-24a', 'Derived from, but not isogenic to, S288C'),
                                   ('Y10', 'Philippine coconut isolate'),
                                   ('Y55', 'Laboratory strain'),
                                   ('YJM269', 'Austrian Blauer Portugieser wine grape isolate'),
                                   ('YJM339', 'Clinical isolate'),
                                   ('YJM789', 'Haploid derivative of opportunistic human pathogen'),
                                   ('YNN216', 'Congenic to S288C (see Sikorski and Hieter). Used to derive YSS and CY strains (see Sobel and Wolin).'),
                                   ('YPH499', 'S288C-congenic laboratory strain'),
                                   ('YPH500', 'MAT&alpha; strain isogenic to YPH499 except at mating type locus. Derived from the diploid strain YNN216 (Johnston and Davis 1984; original source: M. Carlson, Columbia University), which is congenic with S288C.'),
                                   ('YPH501', 'a/&alpha; diploid isogenic to YPH499 and YPH500. Derived from the diploid strain YNN216 (Johnston and Davis 1984; original source: M. Carlson, Columbia University), which is congenic with S288C.'),
                                   ('YPS128', 'Pennsylvania woodland isolate'),
                                   ('YPS163', 'Pennsylvania woodland isolate'),
                                   ('YS9', 'Singapore baking strain'),
                                   ('ZTW1', 'Chinese corn mash bioethanol isolate')]

        for strain, description in other_strains:
            yield {'display_name': strain,
                   'source': key_to_source['SGD'],
                   'description': description,
                   'genotype': None if strain not in strain_to_genotype else strain_to_genotype[strain],
                   'status': 'Reference' if bud_obj.name == 'S288C' else ('Alternative Reference' if strain in alternative_reference_strains else 'Other')}

        bud_session.close()
        nex_session.close()
    return strain_starter

# --------------------- Convert Strain Url ---------------------
wiki_strains = set(['S288C', 'BY4743', 'FY4', 'DBY12020', 'DBY12021', 'FY1679', 'AB972', 'A364A', 'XJ24-24a', 'DC5', 'X2180-1A',
                'YNN216', 'YPH499', 'YPH500', 'YPH501', 'Sigma1278b', 'SK1', 'CEN.PK', 'W303', 'W303-1A',
                'W303-1B', 'W303-K6001', 'DY1457', 'D273-10B', 'FL100', 'SEY6210/SEY6211', 'SEY6210', 'SEY6211',
                'JK9-3d', 'RM11-1a', 'Y55'])
sequence_download_strains = set(['AWRI1631', 'AWRI796', 'BY4741', 'BY4742', 'CBS7960', 'CEN.PK', 'CLIB215', 'CLIB324',
                                'CLIB382', 'EC1118', 'EC9-8', 'FL100', 'FostersB', 'FostersO', 'JAY291', 'Kyokai7',
                                'LalvinQA23', 'M22', 'PW5', 'RM11-1a', 'Sigma1278b', 'T7', 'T73', 'UC5', 'VIN13', 'VL3',
                                'W303', 'Y10', 'YJM269', 'YJM789', 'YPS163', 'ZTW1'])


strain_to_source = {'S288C': ('ATCC:204508', 'http://www.atcc.org/ATCCAdvancedCatalogSearch/ProductDetails/tabid/452/Default.aspx?ATCCNum=204508&Template=yeastGeneticStock'),
                    'BY4743': ('Thermo Scientific:YSC1050', 'http://www.thermoscientificbio.com/search/?term=YSC1050'),
                    'FY1679': ('EUROSCARF:10000D', 'http://web.uni-frankfurt.de/fb15/mikro/euroscarf/data/fy1679.html'),
                    'AB972': ('ATCC:204511', 'http://www.atcc.org/ATCCAdvancedCatalogSearch/ProductDetails/tabid/452/Default.aspx?ATCCNum=204511&Template=yeastGeneticStock'),
                    'A364A': ('ATCC:208526', 'http://www.atcc.org/ATCCAdvancedCatalogSearch/ProductDetails/tabid/452/Default.aspx?ATCCNum=208526&Template=yeastGeneticStock'),
                    'X2180-1A': ('ATCC:204504', 'http://www.atcc.org/ATCCAdvancedCatalogSearch/ProductDetails/tabid/452/Default.aspx?ATCCNum=204504&Template=yeastGeneticStock'),
                    'YPH499': ('ATCC:204679', 'http://www.atcc.org/ATCCAdvancedCatalogSearch/ProductDetails/tabid/452/Default.aspx?ATCCNum=204679&Template=yeastGeneticStock'),
                    'YPH500': ('ATCC:204680', 'http://www.atcc.org/ATCCAdvancedCatalogSearch/ProductDetails/tabid/452/Default.aspx?ATCCNum=204680&Template=yeastGeneticStock'),
                    'YPH501': ('ATCC:204681', 'http://www.atcc.org/ATCCAdvancedCatalogSearch/ProductDetails/tabid/452/Default.aspx?ATCCNum=204681&Template=yeastGeneticStock'),
                    'SK1': ('ATCC:204722', 'http://www.atcc.org/ATCCAdvancedCatalogSearch/ProductDetails/tabid/452/Default.aspx?ATCCNum=204722&Template=yeastGeneticStock'),
                    'CENPK': ('EUROSCARF:30000D', 'http://web.uni-frankfurt.de/fb15/mikro/euroscarf/data/cen.html'),
                    'W303': ('Thermo Scientific:YSC1058', 'http://www.thermoscientificbio.com/search/?term=YSC1058'),
                    'W303-1A': ('Thermo Scientific:YSC1058', 'http://www.thermoscientificbio.com/search/?term=YSC1058'),
                    'W303-1B': ('Thermo Scientific:YSC1058', 'http://www.thermoscientificbio.com/search/?term=YSC1058'),
                    'D273-10B': ('ATCC:24657', 'http://www.atcc.org/ATCCAdvancedCatalogSearch/ProductDetails/tabid/452/Default.aspx?ATCCNum=24657&Template=fungiYeast'),
                    'FL100': ('ATCC:28383', 'http://www.atcc.org/ATCCAdvancedCatalogSearch/ProductDetails/tabid/452/Default.aspx?ATCCNum=28383&Template=fungiYeast'),
                    'SEY6210/SEY6211': ('ATCC:201392', 'http://www.atcc.org/ATCCAdvancedCatalogSearch/ProductDetails/tabid/452/Default.aspx?ATCCNum=201392&Template=fungiYeast'),
                    'SEY6210': ('ATCC:96099', 'http://www.atcc.org/ATCCAdvancedCatalogSearch/ProductDetails/tabid/452/Default.aspx?ATCCNum=96099&Template=fungiYeast'),
                    'SEY6211': ('ATCC:96100', 'http://www.atcc.org/ATCCAdvancedCatalogSearch/ProductDetails/tabid/452/Default.aspx?ATCCNum=96100&Template=fungiYeast'),
                    'FY1679': ('ATCC:96604', 'http://www.atcc.org/ATCCAdvancedCatalogSearch/ProductDetails/tabid/452/Default.aspx?ATCCNum=96604&Template=fungiYeast')
}

strain_to_euroscarf = {
    'BY4741': 'Y00000',
    'BY4742': 'Y10000',
    'FY1679': '10000D'
}

def make_strain_url_starter(nex_session_maker):
    from src.sgd.model.nex.misc import Source, Strain
    def strain_url_starter():
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        key_to_strain = dict([(x.unique_key(), x) for x in nex_session.query(Strain).all()])

        for strain in key_to_strain.values():
            if strain.display_name in wiki_strains:
                yield {'display_name': 'Wiki',
                               'link': 'http://wiki.yeastgenome.org/index.php/Commonly_used_strains#' + strain.display_name,
                               'source': key_to_source['SGD'],
                               'category': 'wiki',
                               'strain': strain}

            if strain.display_name in sequence_download_strains:
                yield {'display_name': 'Download Sequence',
                               'link': 'http://downloads.yeastgenome.org/sequence/strains/' + strain.display_name,
                               'source': key_to_source['SGD'],
                               'category': 'download',
                               'strain': strain}

            if strain.format_name in strain_to_source:
                yield {'display_name': strain_to_source[strain.format_name][0],
                               'link': strain_to_source[strain.format_name][1],
                               'source': key_to_source['SGD'],
                               'category': 'source',
                               'strain': strain}

            if strain.format_name in strain_to_euroscarf:
                yield {'display_name': 'EUROSCARF:' + strain_to_euroscarf[strain.format_name],
                               'link': 'http://web.uni-frankfurt.de/fb15/mikro/euroscarf/data/' + strain.format_name + '.html',
                               'source': key_to_source['SGD'],
                               'category': 'source',
                               'strain': strain}

            yield {'display_name': 'PubMed',
                    'link': 'http://www.ncbi.nlm.nih.gov/pubmed/?term=saccharomyces+cerevisiae+' + strain.display_name,
                    'source': key_to_source['SGD'],
                    'category': 'pubmed',
                    'strain': strain}

        yield {'display_name': 'Download Sequence',
                               'link': 'http://www.yeastgenome.org/download-data/sequence',
                               'source': key_to_source['SGD'],
                               'category': 'download',
                               'strain': key_to_strain['S288C']}

        nex_session.close()
    return strain_url_starter

# --------------------- Convert Source ---------------------
def make_source_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.bud.cv import Code
    def source_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        for bud_obj in bud_session.query(Code).all():
            if (bud_obj.tab_name, bud_obj.col_name) in ok_codes:
                yield {'display_name': bud_obj.code_value,
                       'description': bud_obj.description,
                       'date_created': bud_obj.date_created,
                       'created_by': bud_obj.created_by}

        other_sources = ['SGD', 'GO', 'PROSITE', 'Gene3D', 'SUPERFAMILY', 'TIGRFAM', 'Pfam', 'PRINTS',
                                        'PIRSF', 'JASPAR', 'SMART', 'PANTHER', 'ProDom', 'DOI',
                                        'PubMedCentral', 'PubMed', '-', 'ECO', 'TMHMM', 'SignalP', 'PhosphoGRID',
                                        'GenBank/EMBL/DDBJ', 'Phobius']

        for source in other_sources:
            yield {'display_name': source}

        bud_session.close()
        nex_session.close()
    return source_starter

ok_codes = {('ALIAS', 'ALIAS_TYPE'), ('DBXREF', 'SOURCE'), ('EXPERIMENT', 'SOURCE'), ('FEATURE', 'SOURCE'),
                ('GO_ANNOTATION', 'SOURCE'), ('HOMOLOG', 'SOURCE'), ('INTERACTION', 'SOURCE'), ('PHENOTYPE', 'SOURCE'),
                ('REFTYPE', 'SOURCE'), ('REFERENCE', 'SOURCE'), ('URL', 'SOURCE')}
