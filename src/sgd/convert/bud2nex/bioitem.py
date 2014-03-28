import logging
import sys

from mpmath import ceil
from sqlalchemy.sql.expression import distinct, or_

from src.sgd.convert import OutputCreator, create_or_update, create_format_name, break_up_file


__author__ = 'kpaskov'

#--------------------- Convert Bioitems ---------------------
def create_phenotype_bioitems(old_phenotype_feature, key_to_source):
    from src.sgd.model.nex.bioitem import Allele as NewAllele, Orphanbioitem as NewOrphanbioitem
    
    allele_reporters = []
    if old_phenotype_feature.experiment is not None:
        allele_info = old_phenotype_feature.experiment.allele
        if allele_info is not None:
            source = key_to_source['SGD']
            new_allele = NewAllele(allele_info[0], source, allele_info[1])
            allele_reporters.append(new_allele)
        reporter_info = old_phenotype_feature.experiment.reporter
        if reporter_info is not None:
            source = key_to_source['SGD']
            new_reporter = NewOrphanbioitem(reporter_info[0], None, source, reporter_info[1], None)
            allele_reporters.append(new_reporter)
    return allele_reporters

def create_go_bioitems(old_dbxref, key_to_source):
    from src.sgd.model.nex.bioitem import Orphanbioitem as NewOrphanbioitem
    dbxref_type = old_dbxref.dbxref_type
    if dbxref_type != 'GOID' and dbxref_type != 'EC number' and dbxref_type != 'DBID Primary' and dbxref_type != 'PANTHER' and dbxref_type != 'Prosite':
        source_key = create_format_name(old_dbxref.source)
        source = None if source_key not in key_to_source else key_to_source[source_key]
        if source is None:
            print source_key
            return []
        link = None
        bioitem_type = None
        if dbxref_type == 'UniProt/Swiss-Prot ID':
            urls = old_dbxref.urls
            if len(urls) == 1:
                link = urls[0].url.replace('_SUBSTITUTE_THIS_', old_dbxref.dbxref_id)
            bioitem_type = 'UniProtKB'
        elif dbxref_type == 'UniProtKB Subcellular Location':
            link = "http://www.uniprot.org/locations/" + old_dbxref.dbxref_id
            bioitem_type = 'UniProtKB-SubCell'
        elif dbxref_type == 'InterPro':
            link = "http://www.ebi.ac.uk/interpro/entry/" + old_dbxref.dbxref_id
            bioitem_type = 'InterPro'
        elif dbxref_type == 'DNA accession ID':
            link = None
            bioitem_type = 'EMBL'
        elif dbxref_type == 'Gene ID':
            link = None
            bioitem_type = old_dbxref.source
        elif dbxref_type == 'HAMAP ID' or dbxref_type == 'HAMAP':
            link = None
            bioitem_type = 'HAMAP'
        elif dbxref_type == 'PDB identifier':
            link = None
            bioitem_type = 'PDB'
        elif dbxref_type == 'Protein version ID':
            link = None
            bioitem_type = 'protein_id'
        elif dbxref_type == 'UniPathway ID':
            link = 'http://www.grenoble.prabi.fr/obiwarehouse/unipathway/upa?upid=' + old_dbxref.dbxref_id
            bioitem_type = 'UniPathway'
        elif dbxref_type == 'UniProtKB Keyword':
            link = 'http://www.uniprot.org/keywords/' + old_dbxref.dbxref_id
            bioitem_type = 'UniProtKB-KW'
        return [NewOrphanbioitem(old_dbxref.dbxref_id, link, source, old_dbxref.dbxref_name, bioitem_type)]

    return []

def convert_orphan(old_session_maker, new_session_maker):
    from src.sgd.model.nex.bioitem import Allele as NewAllele, Orphanbioitem as NewOrphanbioitem
    from src.sgd.model.nex.misc import Source as NewSource
    from src.sgd.model.bud.phenotype import PhenotypeFeature as OldPhenotypeFeature
    from src.sgd.model.bud.go import GorefDbxref as OldGorefDbxref
    from src.sgd.model.bud.general import Dbxref as OldDbxref

    new_session = None
    old_session = None
    log = logging.getLogger('convert.bioitem')
    output_creator = OutputCreator(log)
    
    try:
        new_session = new_session_maker()
        old_session = old_session_maker()     

        #-------------Phenotype---------------
        #Grab all current objects
        current_objs = new_session.query(NewAllele).all()
        current_objs.extend(new_session.query(NewOrphanbioitem).all())
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs]) 
                  
        #Values to check
        values_to_check = ['description', 'display_name', 'source_id', 'link', 'bioitem_type']
                
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        keys_already_seen = set()
        
        #Grab cache
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])
            
        #Grab old objects
        old_objs = old_session.query(OldPhenotypeFeature).all()
        
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_phenotype_bioitems(old_obj, key_to_source)
                
            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                key = newly_created_obj.unique_key()
                if key not in keys_already_seen:
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if key not in key_to_current_obj else key_to_current_obj[key]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                    keys_already_seen.add(key)
                    
                    if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_id.id)
                    if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_key.id)

        #Grab old objects
        dbxref_ids = [x[0] for x in old_session.query(distinct(OldGorefDbxref.dbxref_id)).all()]
        num_chunks = ceil(1.0*len(dbxref_ids)/500)
        old_objs = []
        for i in range(num_chunks):
            dbxref_id_chunk = dbxref_ids[i*500: (i+1)*500]
            old_objs.extend(old_session.query(OldDbxref).filter(OldDbxref.id.in_(dbxref_id_chunk)).all())

        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_go_bioitems(old_obj, key_to_source)

            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                key = newly_created_obj.unique_key()
                if key not in keys_already_seen:
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if key not in key_to_current_obj else key_to_current_obj[key]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                    keys_already_seen.add(key)

                    if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_id.id)
                    if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_key.id)
                        
        #Delete untouched objs
        for untouched_obj_id  in untouched_obj_ids:
            new_session.delete(id_to_current_obj[untouched_obj_id])
            output_creator.removed()

        #Commit
        new_session.commit()
        
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()
        old_session.close()
        
    output_creator.finished()

# --------------------- Convert Domain ---------------------
def create_domain(row, key_to_source):
    from src.sgd.model.nex.bioitem import Domain

    source_key = row[13].strip()

    display_name = row[3].strip()
    description = row[4].strip()
    interpro_id = row[5].strip()
    interpro_description = row[6].strip()

    #Need to check these links
    if source_key == 'JASPAR':
        link = 'http://jaspar.binf.ku.dk/cgi-bin/jaspar_db.pl?rm=present&collection=CORE&ID=' + display_name
    elif source_key == 'HMMSmart':
        source_key = 'SMART'
        link = "http://smart.embl-heidelberg.de/smart/do_annotation.pl?DOMAIN=" + display_name
    elif source_key == 'HMMPfam':
        source_key = 'Pfam'
        link = "http://pfam.sanger.ac.uk/family?type=Family&entry=" + display_name
    elif source_key == 'Gene3D':
        link = "http://www.cathdb.info/version/latest/superfamily/" + display_name[6:]
    elif source_key == 'superfamily':
        source_key = 'SUPERFAMILY'
        link = "http://supfam.org/SUPERFAMILY/cgi-bin/scop.cgi?ipid=" + display_name
    elif source_key == 'Seg':
        source_key = '-'
        link = None
    elif source_key == 'Coil':
        source_key = '-'
        link = None
    elif source_key == 'HMMPanther':
        source_key = 'PANTHER'
        link = "http://www.pantherdb.org/panther/family.do?clsAccession=" + display_name
    elif source_key == 'HMMTigr':
        source_key = 'TIGRFAMs'
        link = "http://cmr.tigr.org/tigr-scripts/CMR/HmmReport.cgi?hmm_acc=" + display_name
    elif source_key == 'FPrintScan':
        source_key = 'PRINTS'
        link = "http:////www.bioinf.man.ac.uk/cgi-bin/dbbrowser/sprint/searchprintss.cgi?display_opts=Prints&amp;category=None&amp;queryform=false&amp;prints_accn=" + display_name
    elif source_key == 'BlastProDom':
        source_key = 'ProDom'
        link = "http://prodom.prabi.fr/prodom/current/cgi-bin/request.pl?question=DBEN&amp;query=" + display_name
    elif source_key == 'HMMPIR':
        source_key = "PIR superfamily"
        link = "http://pir.georgetown.edu/cgi-bin/ipcSF?" + display_name
    elif source_key == 'ProfileScan':
        source_key = 'PROSITE'
        link = "http://prodom.prabi.fr/prodom/cgi-bin/prosite-search-ac?" + display_name
    elif source_key == 'PatternScan':
        source_key = 'PROSITE'
        link = "http://prodom.prabi.fr/prodom/cgi-bin/prosite-search-ac?" + display_name
    else:
        print 'No link for source = ' + source_key + ' ' + str(display_name)
        return None

    source_key = create_format_name(source_key)
    source = None if source_key not in key_to_source else key_to_source[source_key]

    description = None if description == 'no description' else description
    interpro_description = None if interpro_description == 'NULL' else interpro_description
    interpro_id = None if interpro_id == 'NULL' else interpro_id

    domain = Domain(display_name, source, description if description is not None else interpro_description, interpro_id, source_key, interpro_description, link)
    return [domain]

def create_domain_from_tf_file(row, key_to_source):
    from src.sgd.model.nex.bioitem import Domain

    display_name = row[0]
    description = 'Class: ' + row[4] + ', Family: ' + row[3]
    interpro_id = None
    interpro_description = None

    link = 'http://jaspar.binf.ku.dk/cgi-bin/jaspar_db.pl?rm=present&collection=CORE&ID=' + display_name

    source = key_to_source['JASPAR']

    domain = Domain(display_name, source, description if description is not None else interpro_description, 'JASPAR', interpro_id, interpro_description, link)
    return [domain]

def create_domain_from_protein_details(key_to_source):
    from src.sgd.model.nex.bioitem import Domain

    transmembrane = Domain('predicted transmembrane domain', key_to_source['TMHMM'], 'predicted transmembrane domain', 'TMHMM', None, None, None)
    signal_peptide = Domain('predicted signal peptide', key_to_source['SignalP'], 'predicted signal peptide', 'SignalP', None, None, None)
    return [transmembrane, signal_peptide]

def create_domain_from_dbxref(old_dbxref, key_to_source):
    from src.sgd.model.nex.bioitem import Domain
    dbxref_type = old_dbxref.dbxref_type
    source_key = create_format_name(old_dbxref.source)
    source = None if source_key not in key_to_source else key_to_source[source_key]
    if source is None:
        print source_key
        return []
    link = None
    bioitem_type = None
    if dbxref_type == 'Prosite ID':
        bioitem_type = 'Prosite'
        link = "http://prodom.prabi.fr/prodom/cgi-bin/prosite-search-ac?" + old_dbxref.dbxref_id
    elif dbxref_type == 'PANTHER':
        bioitem_type = 'PANTHER'
        link = "http://www.pantherdb.org/panther/family.do?clsAccession=" + old_dbxref.dbxref_id
    return [Domain(old_dbxref.dbxref_id, source, old_dbxref.dbxref_name, bioitem_type, None, None, link)]

def convert_domain(old_session_maker, new_session_maker, chunk_size):
    from src.sgd.model.nex.bioitem import Domain
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.bud.general import Dbxref as OldDbxref

    new_session = None
    log = logging.getLogger('convert.protein_domain.domain')
    output_creator = OutputCreator(log)

    try:
        #Grab all current objects
        new_session = new_session_maker()
        current_objs = new_session.query(Domain).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])

        #Values to check
        values_to_check = ['display_name', 'description', 'interpro_id', 'interpro_description', 'link', 'source_id', 'external_link', 'bioitem_type']

        untouched_obj_ids = set(id_to_current_obj.keys())

        #Grab old objects
        data = break_up_file('src/sgd/convert/data/yeastmine_protein_domains.tsv')

        #Cache
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])

        used_unique_keys = set()

        min_id = 0
        count = len(data)
        num_chunks = ceil(1.0*count/chunk_size)
        for i in range(0, num_chunks):
            old_objs = data[min_id:min_id+chunk_size]
            for old_obj in old_objs:
                #Convert old objects into new ones
                newly_created_objs = create_domain(old_obj, key_to_source)

                if newly_created_objs is not None:
                    #Edit or add new objects
                    for newly_created_obj in newly_created_objs:
                        unique_key = newly_created_obj.unique_key()
                        if unique_key not in used_unique_keys:
                            current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                            current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                            create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                            used_unique_keys.add(unique_key)

                            if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                                untouched_obj_ids.remove(current_obj_by_id.id)
                            if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                                untouched_obj_ids.remove(current_obj_by_key.id)

            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            new_session.commit()
            min_id = min_id+chunk_size

        #Grab JASPAR domains from file
        old_objs = break_up_file('src/sgd/convert/data/TF_family_class_accession04302013.txt')
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_domain_from_tf_file(old_obj, key_to_source)

            if newly_created_objs is not None:
                #Edit or add new objects
                for newly_created_obj in newly_created_objs:
                    unique_key = newly_created_obj.unique_key()
                    if unique_key not in used_unique_keys:
                        current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                        current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                        create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                        used_unique_keys.add(unique_key)

                        if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_id.id)
                        if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_key.id)
                        used_unique_keys.add(unique_key)

        output_creator.finished("1/3")
        new_session.commit()

        #Protein domains from protein_details
        newly_created_objs = create_domain_from_protein_details(key_to_source)

        if newly_created_objs is not None:
            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                unique_key = newly_created_obj.unique_key()
                if unique_key not in used_unique_keys:
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                    used_unique_keys.add(unique_key)

                    if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_id.id)
                    if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_key.id)
                    used_unique_keys.add(unique_key)

        output_creator.finished("2/3")
        new_session.commit()

        #Protein domains from dbxref
        old_session = old_session_maker()
        old_objs = old_session.query(OldDbxref).filter(or_(OldDbxref.dbxref_type == 'PANTHER', OldDbxref.dbxref_type == 'Prosite')).all()

        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_domain_from_dbxref(old_obj, key_to_source)
            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                unique_key = newly_created_obj.unique_key()
                if unique_key not in used_unique_keys:
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                    used_unique_keys.add(unique_key)

                    if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_id.id)
                    if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_key.id)
                    used_unique_keys.add(unique_key)

        output_creator.finished("3/3")
        new_session.commit()

        #Delete untouched objs
        for untouched_obj_id  in untouched_obj_ids:
            new_session.delete(id_to_current_obj[untouched_obj_id])
            output_creator.removed()

        #Commit
        output_creator.finished()
        new_session.commit()

    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()

#1.23.14 Maitenance (sgd-dev): :19

# --------------------- Convert Chemical ---------------------
def create_chemical(expt_property, key_to_source):
    from src.sgd.model.nex.bioitem import Chemical as NewChemical

    display_name = expt_property.value
    source = key_to_source['SGD']
    new_chemical = NewChemical(display_name, source, None, None, expt_property.date_created, expt_property.created_by)
    return [new_chemical]

def create_chemical_from_cv_term(old_cvterm, key_to_source):
    from src.sgd.model.nex.bioitem import Chemical as NewChemical
    source = key_to_source['SGD']
    new_chemical = NewChemical(old_cvterm.name, source, old_cvterm.dbxref_id,
                               old_cvterm.definition, old_cvterm.date_created, old_cvterm.created_by)
    return [new_chemical]

def convert_chemical(old_session_maker, new_session_maker):
    from src.sgd.model.nex.bioitem import Chemical as NewChemical
    from src.sgd.model.nex.misc import Source as NewSource
    from src.sgd.model.bud.phenotype import ExperimentProperty as OldExperimentProperty
    from src.sgd.model.bud.cv import CVTerm as OldCVTerm

    new_session = None
    old_session = None
    log = logging.getLogger('convert.chemical.chemical')
    output_creator = OutputCreator(log)

    try:
        new_session = new_session_maker()
        old_session = old_session_maker()

        #Grab all current objects
        current_objs = new_session.query(NewChemical).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])

        #Values to check
        values_to_check = ['source_id', 'link', 'display_name', 'chebi_id']

        untouched_obj_ids = set(id_to_current_obj.keys())

        keys_already_seen = set()

        #Grab old objects
        old_objs = old_session.query(OldExperimentProperty).filter(or_(OldExperimentProperty.type=='Chemical_pending',
                                                                       OldExperimentProperty.type == 'chebi_ontology')).all()

        #Grab cache
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])

        old_cvterms = old_session.query(OldCVTerm).filter(OldCVTerm.cv_no == 3).all()
        #Convert cv terms
        for old_obj in old_cvterms:
            #Convert old objects into new ones
            newly_created_objs = create_chemical_from_cv_term(old_obj, key_to_source)

            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                key = newly_created_obj.unique_key()
                if key not in keys_already_seen:
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if newly_created_obj.unique_key() not in key_to_current_obj else key_to_current_obj[newly_created_obj.unique_key()]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                    keys_already_seen.add(key)

                    if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_id.id)
                    if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_key.id)

        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_chemical(old_obj, key_to_source)

            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                key = newly_created_obj.unique_key()
                if key not in keys_already_seen:
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if key not in key_to_current_obj else key_to_current_obj[key]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                    keys_already_seen.add(key)

                    if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_id.id)
                    if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_key.id)

        #Delete untouched objs
        for untouched_obj_id  in untouched_obj_ids:
            new_session.delete(id_to_current_obj[untouched_obj_id])
            output_creator.removed()

        #Commit
        output_creator.finished()
        new_session.commit()

    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()
        old_session.close()

# ---------------------Convert------------------------------
def convert(old_session_maker, new_session_maker):

    #convert_orphan(old_session_maker, new_session_maker)

    convert_domain(old_session_maker, new_session_maker, 5000)

    #convert_chemical(old_session_maker, new_session_maker)
