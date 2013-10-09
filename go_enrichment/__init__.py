from go_enrichment import query_batter, query_yeastmine

def query_go_processes(bioent_format_names):
    enrichment_results = query_batter.query_go_processes(bioent_format_names)
    if enrichment_results is None:
        enrichment_results = query_yeastmine.query_go_processes(bioent_format_names)
    return enrichment_results