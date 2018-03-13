import json

with open('./data/example_data.json') as in_file:
    example_data = json.load(in_file)

# example_data = {
#     'Q27286421': {
#         "ikey": "WXNRAKRZUCLRBP-UHFFFAOYSA-N",
#         "gvk": {
#           "hvac_id": "CBR-HVAC-02492",
#           "gvk_id": 16001459,
#           "drug_name": "AVRIDINE",
#           "phase": [
#             "PRESCRIPTION DRUG"
#           ],
#           "category": [
#             "Antiviral"
#           ],
#           "mechanism": [
#             "Vanilloid receptor 1 Agonist"
#           ],
#           "smiles": "[H]OCCN(CCO[H])CCCN(CCCCCCCCCCCCCCCCCC)CCCCCCCCCCCCCCCCCC",
#           "synonyms": [
#             "Avridinum",
#             " BRN-2227682",
#             " CP-20961"
#           ],
#           "ikey": "WXNRAKRZUCLRBP-UHFFFAOYSA-N",
#           "roa": [
#             "Oral"
#           ]
#         },
#         "integrity": {
#           "phase": "Preclinical",
#           "drug_name": "Auridine",
#           "PubChem CID": "CID37186",
#           "smiles": "CCCCCCCCCCCCCCCCCCN(CCCCCCCCCCCCCCCCCC)CCCN(CCO)CCO",
#           "ikey": "WXNRAKRZUCLRBP-UHFFFAOYSA-N",
#           "id": 90012,
#           "category": [
#             "Immunomodulators",
#             " Antiviral Drugs"
#           ],
#           "mechanism": [
#             "Angiogenesis Inhibitors",
#             " Apoptosis Inducers"
#           ],
#           "wikidata": "Q27286421"
#         },
#         "informa": {
#           "phase": "No Development Reported",
#           "drug_name": "avridine\nCP-20961",
#           "highest_phase": "Phase I Clinical Trial",
#           "PubChem CID": "CID37186",
#           "smiles": "CCCCCCCCCCCCCCCCCCN(CCCCCCCCCCCCCCCCCC)CCCN(CCO)CCO",
#           "ikey": "WXNRAKRZUCLRBP-UHFFFAOYSA-N",
#           "mechanism": "Interferon receptor agonist",
#           "wikidata": "Q27286421"
#         },
#         "assay": {}
#
#     },
#     "Q27088554": {
#         "ikey": "NNBGCSGCRSCFEA-UHFFFAOYSA-N",
#         "gvk": {
#           "hvac_id": "CBR-HVAC-00627",
#           "gvk_id": 5917165,
#           "drug_name": "RILAPLADIB",
#           "phase": [
#             "Phase II"
#           ],
#           "category": [
#             "Antiarteriosclerotic"
#           ],
#           "mechanism": [
#             "Phospholipase A2 Inhibitor"
#           ],
#           "smiles": "COCCN1CCC(CC1)N(CC2=CC=C(C=C2)C3=CC=C(C=C3)C(F)(F)F)C(=O)CN4C(SCC5=C(F)C(F)=CC=C5)=CC(=O)C6=C4C=CC=C6",
#           "synonyms": [
#             "659032",
#             " SB-659032"
#           ],
#           "ikey": "NNBGCSGCRSCFEA-UHFFFAOYSA-N",
#           "roa": [
#             "Oral"
#           ]
#         },
#         "integrity": {
#           "phase": "Phase II",
#           "drug_name": "Rilapladib",
#           "PubChem CID": "CID9918381",
#           "smiles": "COCCN1CCC(CC1)N(Cc2ccc(cc2)c3ccc(cc3)C(F)(F)F)C(=O)Cn4c5ccccc5c(=O)cc4SCc6cccc(c6F)F",
#           "ikey": "NNBGCSGCRSCFEA-UHFFFAOYSA-N",
#           "id": 320250,
#           "category": [
#             "Alzheimer's Dementia, Treatment of ",
#             " Atherosclerosis Therapy"
#           ],
#           "mechanism": [
#             "Lipoprotein Associated Phospholipase A2 (Lp-PLA2) Inhibitors",
#             " Signal Transduction Modulators"
#           ],
#           "wikidata": "Q27088554"
#         },
#         "informa": {
#           "phase": "Phase II",
#           "drug_name": "rilapladib\n659032\nGSK-659032\nGSK659032\nSB-659032\nSB659032",
#           "highest_phase": "Phase I Clinical Trial",
#           "PubChem CID": "CID9918381",
#           "smiles": "COCCN1CCC(CC1)N(Cc1ccc(cc1)-c1ccc(cc1)C(F)(F)F)C(=O)Cn1c(SCc2cccc(F)c2F)cc(=O)c2ccccc12",
#           "ikey": "NNBGCSGCRSCFEA-UHFFFAOYSA-N",
#           "mechanism": "Phospholipase A2 inhibitor",
#           "wikidata": "Q27088554"
#         },
#         "assay": [
#           {
#             "ac50": 0.00000186,
#             "PubChem CID": "CID9918381",
#             "assay_title": "Crypto-C. parvum HCI proliferation assay - Bunch Grass Farm",
#             "smiles": "COCCN1CCC(CC1)N(C(=O)Cn1c(SCc2cccc(c2F)F)cc(=O)c2c1cccc2)Cc1ccc(cc1)c1ccc(cc1)C(F)(F)F",
#             "activity_type": "IC50",
#             "ikey": "NNBGCSGCRSCFEA-UHFFFAOYSA-N",
#             "id": "CBR-001-627-853-8",
#             "wikidata": "Q27088554"
#           },
#           {
#             "ac50": 0.00000222,
#             "PubChem CID": "CID9918381",
#             "assay_title": "Crypto-C. parvum HCI proliferation assay - Sterling Lab",
#             "smiles": "COCCN1CCC(CC1)N(C(=O)Cn1c(SCc2cccc(c2F)F)cc(=O)c2c1cccc2)Cc1ccc(cc1)c1ccc(cc1)C(F)(F)F",
#             "activity_type": "IC50",
#             "ikey": "NNBGCSGCRSCFEA-UHFFFAOYSA-N",
#             "id": "CBR-001-627-853-8",
#             "wikidata": "Q27088554"
#           },
#           {
#             "ac50": 0.00000581,
#             "PubChem CID": "CID9918381",
#             "assay_title": "Crypto-HCT-8 Host Cells - Bunch Grass Farm C. parvum",
#             "smiles": "COCCN1CCC(CC1)N(C(=O)Cn1c(SCc2cccc(c2F)F)cc(=O)c2c1cccc2)Cc1ccc(cc1)c1ccc(cc1)C(F)(F)F",
#             "activity_type": "IC50",
#             "ikey": "NNBGCSGCRSCFEA-UHFFFAOYSA-N",
#             "id": "CBR-001-627-853-8",
#             "wikidata": "Q27088554"
#           },
#           {
#             "ac50": 0.00000511,
#             "PubChem CID": "CID9918381",
#             "assay_title": "Crypto-HCT-8 Host Cells - Sterling Lab C. parvum",
#             "smiles": "COCCN1CCC(CC1)N(C(=O)Cn1c(SCc2cccc(c2F)F)cc(=O)c2c1cccc2)Cc1ccc(cc1)c1ccc(cc1)C(F)(F)F",
#             "activity_type": "IC50",
#             "ikey": "NNBGCSGCRSCFEA-UHFFFAOYSA-N",
#             "id": "CBR-001-627-853-8",
#             "wikidata": "Q27088554"
#           },
#           {
#             "ac50": 0.00000326,
#             "PubChem CID": "CID9918381",
#             "assay_title": "HEK293T 72-h cytotoxicity assay",
#             "smiles": "COCCN1CCC(CC1)N(C(=O)Cn1c(SCc2cccc(c2F)F)cc(=O)c2c1cccc2)Cc1ccc(cc1)c1ccc(cc1)C(F)(F)F",
#             "activity_type": "IC50",
#             "ikey": "NNBGCSGCRSCFEA-UHFFFAOYSA-N",
#             "id": "CBR-001-627-853-8",
#             "wikidata": "Q27088554"
#           }
#         ]
#       },
#     "Q27291538": {
#         "ikey": "MPMZSZMDCRPSRF-UHFFFAOYSA-N",
#         "gvk": {
#           "hvac_id": "CBR-HVAC-03929",
#           "gvk_id": 5916750,
#           "drug_name": "RO 244736",
#           "phase": [
#             "Clinical"
#           ],
#           "category": [
#             "Antiinflammatory"
#           ],
#           "mechanism": [
#             "Platelet activating factor receptor Antagonist"
#           ],
#           "smiles": "CC1=NN=C2CN=C(C3=C(Cl)C=CC=C3)C4=C(SC(=C4)C#CCN5C(=O)C6=CC=CC=C6C7=C5C=CC=C7)N12",
#           "synonyms": [
#             "RO-244736"
#           ],
#           "ikey": "MPMZSZMDCRPSRF-UHFFFAOYSA-N",
#           "roa": [
#             "Oral"
#           ]
#         },
#         "integrity": {
#           "phase": "Phase II",
#           "drug_name": "Ro-24-4736",
#           "PubChem CID": "CID60775",
#           "smiles": "Cc1nnc2n1-c3c(cc(s3)C#CCn4c5ccccc5c6ccccc6c4=O)C(=NC2)c7ccccc7Cl",
#           "ikey": "MPMZSZMDCRPSRF-UHFFFAOYSA-N",
#           "id": 155747,
#           "category": [
#             "Antipsychotic Drugs"
#           ],
#           "mechanism": [
#             "Platelet-Activating Factor Receptor (PAFR) Antagonists",
#             " Signal Transduction Modulators"
#           ],
#           "wikidata": "Q419822"
#         },
#         "informa": {
#           "phase": "No Development Reported",
#           "drug_name": "Ro-24-4736",
#           "highest_phase": "Preclinical",
#           "PubChem CID": "CID60775",
#           "smiles": "Cc1nnc2CN=C(c3cc(sc3-n12)C#CCn1c2ccccc2c2ccccc2c1=O)c1ccccc1Cl |c:6|",
#           "ikey": "MPMZSZMDCRPSRF-UHFFFAOYSA-N",
#           "mechanism": "Platelet activating factor antagonist",
#           "wikidata": "Q27291538"
#         },
#         "assay": [
#           {
#             "ac50": 7.540000000000002e-7,
#             "PubChem CID": "CID60775",
#             "assay_title": "Crypto-C. parvum HCI proliferation assay - Bunch Grass Farm",
#             "smiles": "Cc1nnc2n1c1sc(cc1C(=NC2)c1ccccc1Cl)C#CCn1c(=O)c2ccccc2c2c1cccc2",
#             "activity_type": "IC50",
#             "ikey": "MPMZSZMDCRPSRF-UHFFFAOYSA-N",
#             "id": "CBR-001-633-737-4"
#           },
#           {
#             "ac50": 7.77e-7,
#             "PubChem CID": "CID60775",
#             "assay_title": "Crypto-C. parvum HCI proliferation assay - Sterling Lab",
#             "smiles": "Cc1nnc2n1c1sc(cc1C(=NC2)c1ccccc1Cl)C#CCn1c(=O)c2ccccc2c2c1cccc2",
#             "activity_type": "IC50",
#             "ikey": "MPMZSZMDCRPSRF-UHFFFAOYSA-N",
#             "id": "CBR-001-633-737-4"
#           },
#           {
#             "ac50": 0.0000153,
#             "PubChem CID": "CID60775",
#             "assay_title": "Crypto-HCT-8 Host Cells - Bunch Grass Farm C. parvum",
#             "smiles": "Cc1nnc2n1c1sc(cc1C(=NC2)c1ccccc1Cl)C#CCn1c(=O)c2ccccc2c2c1cccc2",
#             "ikey": "MPMZSZMDCRPSRF-UHFFFAOYSA-N",
#             "id": "CBR-001-633-737-4"
#           },
#           {
#             "ac50": 0.0000464,
#             "PubChem CID": "CID60775",
#             "assay_title": "Crypto-HCT-8 Host Cells - Sterling Lab C. parvum",
#             "smiles": "Cc1nnc2n1c1sc(cc1C(=NC2)c1ccccc1Cl)C#CCn1c(=O)c2ccccc2c2c1cccc2",
#             "ikey": "MPMZSZMDCRPSRF-UHFFFAOYSA-N",
#             "id": "CBR-001-633-737-4"
#           },
#           {
#             "ac50": 0.0000259,
#             "PubChem CID": "CID60775",
#             "assay_title": "HEK293T 72-h cytotoxicity assay",
#             "smiles": "Cc1nnc2n1c1sc(cc1C(=NC2)c1ccccc1Cl)C#CCn1c(=O)c2ccccc2c2c1cccc2",
#             "ikey": "MPMZSZMDCRPSRF-UHFFFAOYSA-N",
#             "id": "CBR-001-633-737-4"
#           }
#         ]
#       },
#
#     "Q27077191": {
#         "ikey": "ONPGOSVDVDPBCY-CQSZACIVSA-N",
#         "gvk": {},
#         "integrity": {
#           "id": 738343,
#           "smiles": "C[C@H](c1c(ccc(c1Cl)F)Cl)Oc2cc(nnc2N)C(=O)Nc3ccc(cc3)C(=O)N4CCN(CC4)C",
#           "drug_name": "X-376",
#           "phase": "Preclinical",
#           "category": [
#             "Oncolytic Drugs"
#           ],
#           "ikey": "ONPGOSVDVDPBCY-CQSZACIVSA-N",
#           "wikidata": "Q27077191",
#           "PubChem CID": "CID56960447",
#           "mechanism": [
#             "ALK Tyrosine Kinase Receptor Inhibitors",
#             " Signal Transduction Modulators"
#           ]
#         },
#         "informa": {},
#         "assay": [
#           {
#             "ac50": 0.00000202,
#             "PubChem CID": "CID56960447",
#             "assay_title": "Crypto-C. parvum HCI proliferation assay - Bunch Grass Farm",
#             "smiles": "CN1CCN(CC1)C(=O)c1ccc(cc1)NC(=O)c1nnc(c(c1)O[C@@H](c1c(Cl)ccc(c1Cl)F)C)N",
#             "activity_type": "IC50",
#             "ikey": "ONPGOSVDVDPBCY-CQSZACIVSA-N",
#             "id": "CBR-001-669-810-5",
#             "wikidata": "Q27077191"
#           },
#           {
#             "ac50": 0.00000168,
#             "PubChem CID": "CID56960447",
#             "assay_title": "Crypto-C. parvum HCI proliferation assay - Sterling Lab",
#             "smiles": "CN1CCN(CC1)C(=O)c1ccc(cc1)NC(=O)c1nnc(c(c1)O[C@@H](c1c(Cl)ccc(c1Cl)F)C)N",
#             "activity_type": "IC50",
#             "ikey": "ONPGOSVDVDPBCY-CQSZACIVSA-N",
#             "id": "CBR-001-669-810-5",
#             "wikidata": "Q27077191"
#           },
#           {
#             "ac50": 0.00000445,
#             "PubChem CID": "CID56960447",
#             "assay_title": "Crypto-HCT-8 Host Cells - Bunch Grass Farm C. parvum",
#             "smiles": "CN1CCN(CC1)C(=O)c1ccc(cc1)NC(=O)c1nnc(c(c1)O[C@@H](c1c(Cl)ccc(c1Cl)F)C)N",
#             "activity_type": "IC50",
#             "ikey": "ONPGOSVDVDPBCY-CQSZACIVSA-N",
#             "id": "CBR-001-669-810-5",
#             "wikidata": "Q27077191"
#           },
#           {
#             "ac50": 0.00000433,
#             "PubChem CID": "CID56960447",
#             "assay_title": "Crypto-HCT-8 Host Cells - Sterling Lab C. parvum",
#             "smiles": "CN1CCN(CC1)C(=O)c1ccc(cc1)NC(=O)c1nnc(c(c1)O[C@@H](c1c(Cl)ccc(c1Cl)F)C)N",
#             "activity_type": "IC50",
#             "ikey": "ONPGOSVDVDPBCY-CQSZACIVSA-N",
#             "id": "CBR-001-669-810-5",
#             "wikidata": "Q27077191"
#           },
#           {
#             "ac50": 0.00000392,
#             "PubChem CID": "CID56960447",
#             "assay_title": "HEK293T 72-h cytotoxicity assay",
#             "smiles": "CN1CCN(CC1)C(=O)c1ccc(cc1)NC(=O)c1nnc(c(c1)O[C@@H](c1c(Cl)ccc(c1Cl)F)C)N",
#             "activity_type": "IC50",
#             "ikey": "ONPGOSVDVDPBCY-CQSZACIVSA-N",
#             "id": "CBR-001-669-810-5",
#             "wikidata": "Q27077191"
#           }
#         ]
#       },
#
#     "Q15411004":  {
#         "ikey": "WXJFKKQWPMNTIM-VWLOTQADSA-N",
#         "gvk": {
#           "hvac_id": "CBR-HVAC-00831",
#           "gvk_id": 17500468,
#           "drug_name": "CMX-001",
#           "phase": [
#             "Phase III"
#           ],
#           "category": [
#             "Antiviral"
#           ],
#           "mechanism": [
#             "Antiviral"
#           ],
#           "smiles": "[H]OC[C@H](CN1C=CC(=NC1=O)N([H])[H])OCP(=O)(O[H])OCCCOCCCCCCCCCCCCCCCC",
#           "synonyms": [
#             "CMX-001"
#           ],
#           "ikey": "WXJFKKQWPMNTIM-VWLOTQADSA-N",
#           "roa": [
#             "Oral"
#           ]
#         },
#         "integrity": {
#           "phase": "Phase III",
#           "drug_name": "Brincidofovir",
#           "PubChem CID": "CID483477",
#           "smiles": "CCCCCCCCCCCCCCCCOCCCOP(=O)(CO[C@@H](Cn1ccc(nc1=O)N)CO)O",
#           "ikey": "WXJFKKQWPMNTIM-VWLOTQADSA-N",
#           "id": 317302,
#           "category": [
#             "Anti-Herpes Virus Drugs",
#             " Anti-Herpes Simplex Virus Drugs",
#             " Antiviral Drugs",
#             " Anti-Cytomegalovirus Drugs"
#           ],
#           "mechanism": [
#             "Histamine Receptor Antagonists",
#             " Signal Transduction Modulators"
#           ],
#           "wikidata": "Q15411004"
#         },
#         "informa": {
#           "phase": "Phase III",
#           "drug_name": "brincidofovir\nbrincidofovir iv\ncidofovir prodrug iv, Chimerix\ncidofovir prodrug, Chimerix\ncidofovir prodrug, Chimerix (oral)\ncidofovir prodrug, Chimerix (topical)\nCMX-001 iv, Chimerix\nCMX-001, Chimerix\nCMX-001, Chimerix (oral)\nCMX-001, Chimerix (topical)\nCMX-021\nCMX-021 iv\nCMX-064\nCMX-064 iv\nCMX001, Chimerix\nCMX001, Chimerix (oral)\nCMX001, Chimerix (topical)\nHDP-CDV\nhexadecyloxypropyl-cidofovir\nhexadecyloxypropyl-cidofovir iv",
#           "highest_phase": "Phase III Clinical Trial",
#           "PubChem CID": "CID483477",
#           "smiles": "CCCCCCCCCCCCCCCCOCCCOP(O)(=O)CO[C@H](CO)Cn1ccc(N)nc1=O |r|",
#           "ikey": "WXJFKKQWPMNTIM-VWLOTQADSA-N",
#           "mechanism": "DNA directed DNA polymerase inhibitor",
#           "wikidata": "Q15411004"
#         },
#         "assay": [
#           {
#             "ac50": 0.00000138,
#             "PubChem CID": "CID483477",
#             "assay_title": "Crypto-C. parvum HCI proliferation assay - Bunch Grass Farm",
#             "smiles": "CCCCCCCCCCCCCCCCOCCCOP(=O)(CO[C@@H](Cn1ccc(nc1=O)N)CO)O",
#             "activity_type": "IC50",
#             "ikey": "WXJFKKQWPMNTIM-VWLOTQADSA-N",
#             "id": "CBR-001-670-010-0",
#             "wikidata": "Q15411004"
#           },
#           {
#             "ac50": 0.00000141,
#             "PubChem CID": "CID483477",
#             "assay_title": "Crypto-C. parvum HCI proliferation assay - Sterling Lab",
#             "smiles": "CCCCCCCCCCCCCCCCOCCCOP(=O)(CO[C@@H](Cn1ccc(nc1=O)N)CO)O",
#             "activity_type": "IC50",
#             "ikey": "WXJFKKQWPMNTIM-VWLOTQADSA-N",
#             "id": "CBR-001-670-010-0",
#             "wikidata": "Q15411004"
#           },
#           {
#             "ac50": 0.0000509,
#             "PubChem CID": "CID483477",
#             "assay_title": "Crypto-HCT-8 Host Cells - Sterling Lab C. parvum",
#             "smiles": "CCCCCCCCCCCCCCCCOCCCOP(=O)(CO[C@@H](Cn1ccc(nc1=O)N)CO)O",
#             "ikey": "WXJFKKQWPMNTIM-VWLOTQADSA-N",
#             "id": "CBR-001-670-010-0",
#             "wikidata": "Q15411004"
#           },
#           {
#             "ac50": 0.0000272,
#             "PubChem CID": "CID483477",
#             "assay_title": "HEK293T 72-h cytotoxicity assay",
#             "smiles": "CCCCCCCCCCCCCCCCOCCCOP(=O)(CO[C@@H](Cn1ccc(nc1=O)N)CO)O",
#             "ikey": "WXJFKKQWPMNTIM-VWLOTQADSA-N",
#             "id": "CBR-001-670-010-0",
#             "wikidata": "Q15411004"
#           }
#         ]
#       }
#
# }
