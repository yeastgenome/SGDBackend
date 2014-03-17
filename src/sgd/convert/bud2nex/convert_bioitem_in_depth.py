from src.sgd.convert.bud2nex.convert_auxiliary import convert_disambigs

__author__ = 'kpaskov'

# ---------------------Convert------------------------------
def convert(new_session_maker):

    from src.sgd.model.nex.bioitem import Domain
    convert_disambigs(new_session_maker, Domain, ['id', 'format_name'], 'BIOITEM', 'DOMAIN', 'convert.domain.disambigs', 2000)
