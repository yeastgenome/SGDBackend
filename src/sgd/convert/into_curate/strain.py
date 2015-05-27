from src.sgd.convert.into_curate import basic_convert, remove_nones

__author__ = 'kpaskov'


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
                      'CEN.PK': '<i>MAT</i>a<i>/&alpha; ura3-52/ura3-52 trp1-289/trp1-289 leu2-3_112/leu2-3_112 his3 &Delta;1/his3 &Delta;1 MAL2-8C/MAL2-8C SUC2/SUC2</i>',
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

strain_to_genbank = {
    'YS9': 'JRIB00000000',
    'YPS163': 'JRIC00000000',
    'YPS128': 'JRIC00000000',
    'YJM339': 'JRIF00000000',
    'Y55': 'JRIF00000000',
    'DBVPG6044': 'JRIG00000000',
    'SK1': 'JRIH00000000',
    'BC187': 'JRII00000000',
    'K11': 'JRIJ00000000',
    'L1528': 'JRIK00000000',
    'RedStar': 'JRIL00000000',
    'UWOPSS': 'JRIM00000000',
    'FY1679': 'JRIN00000000',
    'YPH499': 'JRIO00000000',
    'RM11-1a': 'JRIP00000000',
    'Sigma1278b': 'JRIQ00000000',
    'BY4742': 'JRIR00000000',
    'BY4741': 'JRIS00000000',
    'FL100': 'JRIT00000000',
    'W303': 'JRIU00000000',
    'CEN.PK': 'JRIV00000000',
    'SEY6210': 'JRIW00000000',
    'X2180-1A': 'JRIX00000000',
    'D273-10B': 'JRIY00000000',
    'JK9-3d': 'JRIZ00000000',
    'S288C': 'GCF_000146045.2'}

#Name Fold coverage, Number of scaffolds, Assembly size, Longest scaffold, Scaffold N50
strain_to_assembly_stats = {
    'YS9': [100, 1972, 11750421, 142656, 30314, 5271],
    'YPS163': [96, 959, 11692983, 170627, 39876, 5263],
    'YPS128': [95, 1067, 11608384, 143401, 39695, 5241],
    'YJM339': [102, 994, 11683869, 216801, 47674, 5317],
    'Y55': [112, 829, 11700636, 406493, 107844, 5359],
    'DBVPG6044': [176, 819, 11642411, 134064, 36171, 5297],
    'SK1': [261, 978, 11687249, 326823, 103064, 5350],
    'BC187': [177, 853, 11539626, 135217, 36331, 5254],
    'K11': [189, 692, 11532471, 244353, 47234, 5267],
    'L1528': [186, 692, 11640535, 150051, 42013, 5361],
    'RedStar': [180, 1812, 12003693, 319971, 98298, 5440],
    'UWOPSS': [57, 1508, 11398116, 57541, 13931, 4788],
    'FY1679': [329, 886, 11701731, 454382, 122764, 5370],
    'YPH499': [69, 749, 11721435, 462932, 125709, 5421],
    'RM11-1a': [197, 615, 11571262, 540496, 114595, 5323],
    'Sigma1278b': [191, 875, 11642710, 458709, 109268, 5358],
    'BY4742': [103, 868, 11674767, 341843, 108974, 5391],
    'BY4741': [209, 864, 11678362, 454112, 112644, 5404],
    'FL100': [184, 942, 11667748, 580633, 118714, 5366],
    'W303': [301, 967, 11704989, 336272, 102309, 5397],
    'CEN.PK': [89, 850, 11651483, 334215, 115163, 5379],
    'SEY6210': [106, 805, 11664136, 389964, 122714, 5400],
    'X2180-1A': [112, 904, 11693006, 298290, 105189, 5387],
    'D273-10B': [112, 866, 11708626, 343062, 108887, 5383],
    'S288C': [None, 17, 12157105, 1531933, None, None],
    'JK9-3d': [154, 933, 11669230, 320854, 103867, 5385]
}

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
                    'CEN.PK': ('EUROSCARF:30000D', 'http://web.uni-frankfurt.de/fb15/mikro/euroscarf/data/cen.html'),
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

strain_paragraphs = {'S288C': ('S288C is a widely used laboratory strain, designed by Robert Mortimer for biochemical studies, and specifically selected to be non-flocculent with a minimal set of nutritional requirements.  S288C is the strain used in the systematic sequencing project, the reference sequence stored in SGD. S288C does not form pseudohyphae. In addition, since it has a mutated copy of HAP1, it is not a good strain for mitochondrial studies. It has an allelic variant of MIP1 which increases petite frequency. S288C is gal2- and does not use galactose anaerobically.', [3519363]),
                     'RM11-1a': ('RM11-1a is a haploid derivative of RM11, which is a diploid derivative of Bb32(3), which is an ascus derived from Bb32, which is a natural isolate collected by Robert Mortimer from a California vineyard (Ravenswood Zinfandel) in 1993. It has high spore viability (80-90%) and has been extensively characterized phenotypically under a wide range of conditions. It has a significantly longer life span than typical lab yeast strains and accumulates age-associated abnormalities at a lower rate.', [11923494]),
                     'YJM789': ('YJM789 is the haploid form of an opportunistic pathogen derived from a yeast isolated from the lung of an immunocompromised patient in 1989. YJM789 has a reciprocal translocation relative to S288C and AWRI1631, between chromosomes VI and X, as well as a large inversion in chromosome XIV. YJM789 is useful for infection studies and quantitative genetics owing to its divergent phenotype, which includes flocculence, heat tolerance, and deadly virulence.', [2671026, 17652520, 18778279]),
                     'M22': ('M22 was collected in an Italian vineyard.  It has a reciprocal translocation between chromosomes VIII and XVI relative to S288C. This translocation is common in vineyard and wine yeast strains, leads to increased sulfite resistance.', [18769710, 12368245]),
                     'YPS163': ('YPS163 was isolated in 1999 from the soil beneath an oak tree (Quercus rubra) in a Pennsylvania woodland.  YPS163 is freeze tolerant, a phenotype associated with its increased expression of aquaporin AQY2.', [12702333, 15059259]),
                     'AWRI1631': ('AWRI1631 is Australian wine yeast, a robust fermenter and haploid derivative of South African commercial wine strain N96.', [18778279]),
                     'JAY291': ('JAY291 is a non-flocculent haploid derivative of Brazilian industrial bioethanol strain PE-2; it produces high levels of ethanol and cell mass, and is tolerant to heat and oxidative stress. JAY291 is highly divergent to S288C, RM11-1a and YJM789, and contains well-characterized alleles at several genes of known relation to thermotolerance and fermentation performance.', [19812109]),
                     'EC1118': ('EC1118, a diploid commercial yeast, is probably the most widely used wine-making strain worldwide based on volume produced. In the Northern hemisphere, it is also known as Premier Cuvee or Prise de Mousse; it is a reliably aggressive fermenter, and makes clean but somewhat uninteresting wines. EC1118 is more diverged from S288C and YJM789 than from RM11-1a and AWRI1631.  EC1118 has three unique regions from 17 to 65 kb in size on chromosomes VI, XIV and XV, encompassing 34 genes related to key fermentation characteristics, such as metabolism and transport of sugar or nitrogen. There are >100 genes present in S288C that are missing from EC1118.', [19805302]),
                     'Sigma1278b': ('Sigma1278b is widely used laboratory strain, and a systematic deletion collection has been constructed in this strain background.  There are 75 genes in Sigma1278b that are absent from S288C. Some non-S288C regions in W303 are also present in Sigma1278b, which exhibits six times the rate of sequence divergence to S288C as seen in W303.  Sigma1278b is identical to S288C at less than half its genome.', [20413493]),
                     'FostersO': ("Foster's O is a commercial ale strain which has a whole-chromosome amplification of chromosome III.  Foster's O has 48 ORFs not present in S288C.", [21304888]),
                     'FostersB': ("Foster's B is a commercial ale strain which has whole-chromosome amplifications of chromosomes II, V and XV. Foster's B has 36 ORFs not present in S288C.", [21304888]),
                     'VIN13': ('VIN13 is a cold-tolerant South African wine strain, a strong fermenter that is good for making aromatic white wines.  VIN13 has 45 ORFs not present in S288C.', [21304888]),
                     'AWRI796': ("AWRI796 is a South African wine strain that ferments more successfully at warmer temperatures and is more suited to the production of reds. AWRI796 has a whole-chromosome amplification of chromosome I.  AWRI has 74 ORFs that are not present in S288C.", [21304888]),
                     'CLIB215': ("CLIB215 was isolated in 1994 from a bakery in Taranaki in the North Island of New Zealand.", []),
                     'CBS7960': ("CBS7960 was isolated from a cane sugar bioethanol factory in Sao Paulo, Brazil.", []),
                     'CLIB324': ("CLIB324 is a Vietnamese baker's strain collected in 1996 from Ho Chi Minh City.", []),
                     'CLIB382': ("CLIB382 was isolated from beer brewed in Ireland sometime before 1952.", []),
                     'EC9-8': ("EC9-8 is a haploid cadmium-resistant derivative of a yeast isolated from the valley bottom of Evolution Canyon at Lower Nahal Oren, Israel.", [21483812]),
                     'FL100': ("FL100 is a commonly used laboratory strain.  FL100 has a duplication of 80 kb of chromosome III on the left arm chromosome I, and has lost ~45 kb from right end of chromosome I.", [9605505]),
                     'Kyokai7': ("Kyokai No. 7 (K7) is the most extensively used sake yeast, and was first isolated from a sake brewery in Nagano Prefecture, Japan, in 1946.  K7 has two large inversions on chromosomes V and XIV, both flanked by transposable elements and inverted repeats, two CNV reductions on chromosomes I and VII and a mosaic-like pattern and non-random distribution of variation compared with S288C. There are 48 ORFs in K7 that are absent in S288C, and 49 ORFs in S288C that are missing from K7.", [21900213]),
                     'LalvinQA23': ("QA23 is a cold-tolerant Portuguese wine strain from the Vinho Verde region. QA23 has low nutrient and oxygen requirements, and exhibits high beta-glucosidase activity, a combination that makes beautiful Sauvignon blancs. QA23 has 110 ORFs that are not present in S288C.", [21304888]),
                     'PW5': ("PW5 was isolated from fermented sap of a Raphia palm tree in Aba, Abia state, Nigeria in 2002. PW5 shares with YJM269 and CEN.PK113-7D some genes that are absent from S288C.", [22448915]),
                     'T7': ("T7 was isolated from oak tree exudate in Missouri's Babler State Park. ", []),
                     'T73': ("T73 is from a Mourvedre (aka Monastrell) red wine made in Alicante, Spain, in 1987. T73 has low nitrogen requirements, high alcohol tolerance and low volatile acidity production, making it ideal for fermenting robust structured reds grown in hot climates.", []),
                     'UC5': ("UC5 came from Sene sake in Kurashi, Japan, sometime before 1974.", []),
                     'VL3': ("VL3 was isolated in Bordeaux, France, and is most suited to the production of premium aromatic white wines with high thiol content (citrus and tropical fruit characters). VL3 has a whole-chromosome amplification of chromosome VIII, as well as 54 ORFs that are missing from S288C.", [21304888]),
                     'W303': ("W303-derivative K6001 is a key model organism for research into aging, and shares >85% of its genome with S288C, differing at >8000 nucleotide positions, causing changes to the sequences of 799 proteins. These differences are distributed non-randomly throughout the genome, with chromosome XVI being almost identical between the two strains, and chromosome XI the most divergent. Some of the non-S288C regions in W303 are also present in Sigma1278b.", [22977733]),
                     'Y10': ("Y10 was isolated from a coconut in the Philippines, sometime before 1973.", []),
                     'YJM269': ("YJM269 came from red Blauer Portugieser grapes in Austria in 1954. YJM269 shares with CEN.PK113-7D some genes that are absent from S288C, including the ENA6 sodium pump, and others that are also found in PW5.", [22448915]),
                     'BY4741': ("BY4741 is part of a set of deletion strains derived from S288C in which commonly used selectable marker genes were deleted by design in order to minimize or eliminate homology to the corresponding marker genes in commonly used vectors without significantly affecting adjacent gene expression. The yeast strains were all directly descended from FY2, which is itself a direct descendant of S288C. Variation between BY4741 and S288C is miniscule. BY4741 was used as a parent strain for the international systematic <i>Saccharomyces cerevisiae</i> gene disruption project.", [9483801, 7762301]),
                     'BY4742': ("BY4742 is part of a set of deletion strains derived from S288C in which commonly used selectable marker genes were deleted by design in order to minimize or eliminate homology to the corresponding marker genes in commonly used vectors without significantly affecting adjacent gene expression. The yeast strains were all directly descended from FY2, which is itself a direct descendant of S288C. Variation between BY4742 and S288C is miniscule. BY4742 was used as a parent strain for the international systematic <i>Saccharomyces cerevisiae</i> gene disruption project.", [9483801, 7762301]),
                     'CEN.PK': ("CEN.PK113-7D is a laboratory strain derived from parental strains ENY.WA-1A and MC996A, and is popular for use in systems biology studies. There are six duplicated regions in CEN.PK113-7D relative to S288C, two on chromosome II, and one each on chromosomes III, VII, VIII and XV, including an enrichment of maltose metabolism genes. CEN.PK113-7D is a biotin prototroph, and has genes required for biotin biosynthesis. There are >20,000 SNPs between CEN.PK113-7D and S288C, two-thirds of which are within ORFs. Almost 5000 of these result in altered sequences of >1400 proteins. There are also >2800 small indels averaging 3 bp each in CEN.PK113-7D relative to S288C, and more than 400 of these are in coding regions. CEN.PK113-7D also has an additional 83 genes that are absent from S288C, including the ENA6 sodium pump that is also found in YJM269, and others that are present in both YJM269 and PW5.", [22448915]),
                     'ZTW1': ("ZTW1 was isolated from corn mash used for industrial bioethanol production in China in 2007.", []),
                     'AB972': ('AB972 is an ethidium bromide-induced [rho<sup>0</sup>] derivative of Robert Mortimer\'s X2180-1B (obtained via Elizabeth Jones), itself a haploid derivative of strain X2180, which was made by self-diploidization of S288C. AB972 was used in the original sequencing project for chromosomes I, III, IV, V, VI, VIII, IX, XII, XIII, and XVI.  A single colony of AB972 was also later used as the source of DNA for the latest <i>S. cerevisiae</i> version R64 genomic reference sequence (also known as S288C 2010). This single colony was grown from a stored isolate from the original AB972 strain used by Linda Riles to create the DNA libraries used in the original genome project.', [2029969, 3463999, 3519363, 8514151, 7731988, 1574125, 9169867, 9169868, 7670463, 8091229, 9169870, 9169871, 9169872, 9169875, 24374639]),
                     'FY1679': ('FY1679 is a diploid made from haploid parents FY23 (mating type a) and FY73 (mating type &alpha;) by Fred Winston and colleagues who used gene replacement to develop a set of yeast strains isogenic to S288C but repaired for GAL2, and which also contained nonreverting mutations in several genes commonly used for selection in the laboratory environment (URA3, TRP1, LYS2, LEU2, HIS3). A cosmid library made from FY1679 was used in the original genome sequencing project as the source of DNA for chromosomes VII, X, XI, XIV, and XV. FY1679 was also used for sequencing the mitochondrial DNA, which was not part of the nuclear genome project and was determined separately.', [7762301, 9169869, 8641269, 8196765, 9169873, 9169874, 9872396, 1964349]),
                     'FY4': ('FY4 was made by Fred Winston and colleagues who used gene replacement to develop a set of yeast strains isogenic to S288C but repaired for GAL2, and which also contained nonreverting mutations in several genes commonly used for selection in the laboratory environment (URA3, TRP1, LYS2, LEU2, HIS3).', [7762301])

}


def strain_starter(bud_session_maker):
    from src.sgd.model.bud.cv import CVTerm

    bud_session = bud_session_maker()

    for bud_obj in bud_session.query(CVTerm).filter(CVTerm.cv_no==10).all():
        obj_json = remove_nones({'display_name': bud_obj.name,
                                 'source': {'display_name': 'SGD'},
                                 'description': bud_obj.definition if bud_obj.name not in strain_to_description else strain_to_description[bud_obj.name],
                                 'status': 'Reference' if bud_obj.name == 'S288C' else ('Alternative Reference' if bud_obj.name in alternative_reference_strains else (None if bud_obj.name == 'Other' else 'Other')),
                                 'genotype': None if bud_obj.name not in strain_to_genotype else strain_to_genotype[bud_obj.name],
                                 'genbank_id': None if bud_obj.name not in strain_to_genbank else strain_to_genbank[bud_obj.name],
                                 'sgdid': 'S000' + bud_obj.name,
                                 'taxonomy': {'display_name': 'Saccharomyces cerevisiae'},
                                 'date_created': str(bud_obj.date_created),
                                 'created_by': bud_obj.created_by})
        if bud_obj.name in strain_to_assembly_stats:
            assembly_stats = strain_to_assembly_stats[bud_obj.name]
            obj_json['fold_coverage'] = assembly_stats[0]
            obj_json['scaffold_number'] = assembly_stats[1]
            obj_json['assembly_size'] = assembly_stats[2]
            obj_json['longest_scaffold'] = assembly_stats[3]
            obj_json['scaffold_n50'] = assembly_stats[4]
            obj_json['feature_count'] = assembly_stats[5]

        obj_json['urls'] = load_urls(bud_obj.name, obj_json.get('genbank_id'))
        obj_json['documents'] = load_documents(bud_obj.name)
        yield obj_json

    for strain, description in other_strains:
        obj_json = {'display_name': strain,
                    'source': {'display_name': 'SGD'},
                    'description': description,
                    'sgdid': 'S000' + strain,
                    'taxonomy': {'display_name': 'Saccharomyces cerevisiae'},
                    'genotype': None if strain not in strain_to_genotype else strain_to_genotype[strain],
                    'genbank_id': None if strain not in strain_to_genbank else strain_to_genbank[strain],
                    'status': 'Reference' if bud_obj.name == 'S288C' else ('Alternative Reference' if strain in alternative_reference_strains else 'Other')}

        if strain in strain_to_assembly_stats:
            assembly_stats = strain_to_assembly_stats[strain]
            obj_json['fold_coverage'] = assembly_stats[0]
            obj_json['scaffold_number'] = assembly_stats[1]
            obj_json['assembly_size'] = assembly_stats[2]
            obj_json['longest_scaffold'] = assembly_stats[3]
            obj_json['scaffold_n50'] = assembly_stats[4]
            obj_json['feature_count'] = assembly_stats[5]

        obj_json['urls'] = load_urls(strain, obj_json.get('genbank_id'))
        obj_json['documents'] = load_documents(strain)
        yield obj_json

    bud_session.close()


def load_urls(strain, genbank_id):
    urls = []

    if strain in wiki_strains:
        urls.append({'display_name': 'Wiki',
                     'link': 'http://wiki.yeastgenome.org/index.php/Commonly_used_strains#' + strain,
                     'source': {'display_name': 'SGD'},
                     'url_type': 'wiki'})

    if strain in sequence_download_strains:
        urls.append({'display_name': 'Download Sequence',
                     'link': 'http://downloads.yeastgenome.org/sequence/strains/' + strain,
                     'source': {'display_name': 'SGD'},
                     'url_type': 'download'})

    if strain in strain_to_source:
        urls.append({'display_name': strain_to_source[strain][0],
                     'link': strain_to_source[strain][1],
                     'source': {'display_name': 'SGD'},
                     'url_type': 'source'})

    if strain in strain_to_euroscarf:
        urls.append({'display_name': 'EUROSCARF:' + strain_to_euroscarf[strain],
                     'link': 'http://web.uni-frankfurt.de/fb15/mikro/euroscarf/data/' + strain + '.html',
                     'source': {'display_name': 'SGD'},
                     'url_type': 'source'})

    if genbank_id is not None:
        urls.append({'display_name': genbank_id,
                     'link': 'http://www.ncbi.nlm.nih.gov/nuccore/' + genbank_id if strain != 'S288C' else 'http://www.ncbi.nlm.nih.gov/assembly/GCF_000146045.2/',
                     'source': {'display_name': 'SGD'},
                     'url_type': 'genbank'})

    if strain == 'S288C':
        urls.append({'display_name': 'Download Sequence',
                     'link': 'http://www.yeastgenome.org/download-data/sequence',
                     'source': {'display_name': 'SGD'},
                     'url_type': 'download'})

    urls.append({'display_name': 'PubMed',
                 'link': 'http://www.ncbi.nlm.nih.gov/pubmed/?term=saccharomyces+cerevisiae+' + strain,
                 'source': {'display_name': 'SGD'},
                 'url_type': 'pubmed'})

    return urls


def load_documents(strain):
    documents = []
    if strain in strain_paragraphs:
        paragraph = strain_paragraphs[strain]
        documents.append({
            'source': {'display_name': 'SGD'},
            'document_type': 'Paragraph',
            'text': paragraph[0],
            'html': paragraph[0],
            'references': [{'pubmed_id': pubmed_id, 'reference_order': i+1} for (i, pubmed_id) in enumerate(paragraph[1])]
            })

    return documents


def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, strain_starter, 'strain', lambda x: x['display_name'])


if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')

