from src.sgd.convert import basic_convert, remove_nones

__author__ = 'kpaskov'
## updated by sweng66

def journal_starter(bud_session_maker):
    from src.sgd.model.bud.reference import Journal
    bud_session = bud_session_maker()

    for old_journal in bud_session.query(Journal).all():
        abbreviation = old_journal.abbreviation
        if old_journal.issn == '0948-5023':
            abbreviation = 'J Mol Model (Online)'

        title = old_journal.full_name
        if title is not None or abbreviation is not None:
            display_name = title
            if title == None:
                display_name = abbreviation
            yield remove_nones({
                'source': {'display_name': 'PubMed'},
                'display_name': display_name,
                'title': title,
                'med_abbr': abbreviation,
                'issn_print': old_journal.issn,
                'issn_online': old_journal.essn,
                'bud_id': old_journal.id,
                'date_created': str(old_journal.date_created),
                'created_by': old_journal.created_by})

    bud_session.close()


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, journal_starter, 'journal', lambda x: (None if 'title' not in x else x['title'], None if 'med_abbr' not in x else x['med_abbr']))



