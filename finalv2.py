import requests
from bs4 import BeautifulSoup
from CustomLibrary.Graph_Utils import select_paths

base_url = "https://www.google.com/search?q="

def get_similar_compounds(drug_name, top_n):
    # Get CID of the drug from PubChem
    pubchem_cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{drug_name}/cids/JSON"
    response = requests.get(pubchem_cid_url)
    cid = response.json()['IdentifierList']['CID'][0]

    # Get canonical SMILES of the drug from PubChem
    pubchem_smiles_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/CanonicalSMILES/JSON"
    response = requests.get(pubchem_smiles_url)
    smiles = response.json()['PropertyTable']['Properties'][0]['CanonicalSMILES']

    # Use the ChEMBL API to find similar compounds
    chembl_url = f"https://www.ebi.ac.uk/chembl/api/data/similarity/{smiles}/40?format=json"
    response = requests.get(chembl_url)
    print(response.json())
    similar_compounds = [molecule['pref_name'] for molecule in response.json()['molecules'] if 'pref_name' in molecule and molecule['pref_name'] is not None]

    # If there are less compounds than top_n + 1 (including the top most similar one which we are going to ignore), return all compounds except the first one
    if len(similar_compounds) < top_n + 1:
        return similar_compounds[1:]

    # Otherwise, return the top_n similar compounds after the first one
    return similar_compounds[1:top_n + 1]

def get_url(drug_name):
    # similar_compounds = get_similar_compounds(drug_name, top_n)
    # query = f"{similar_compounds} drugbank"
    query = f"{drug_name} drugbank"
    response = requests.get(base_url + query)
    soup = BeautifulSoup(response.content, 'html.parser')
    result = soup.find('div', class_='kCrYT').find('a', href=True)['href']
    url = result.split('/url?q=')[1].split('&')[0]
    return url

def parse_elements(url, drug_name):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        h1_tag = soup.find('h1', class_="align-self-center mr-4").text

        if h1_tag.lower() != drug_name.lower():
            return

        # your new script starts here
        targets_header = soup.find('h3', string='Targets')
        targets_div = targets_header.find_next_sibling('div')
        dt_tags = targets_div.find_all('dt', {'id': 'gene-name'})

        gene_data = [] # to store gene_name and gene_value pairs

        for dt_tag in dt_tags:
            dd_tag = dt_tag.find_next_sibling('dd')
            gene_name = dt_tag.text.strip()
            gene_value = dd_tag.text.strip()
            gene_data.append((gene_name, gene_value)) # add gene_name and gene_value as a tuple to the list

        return gene_data
        # your new script ends here

    except Exception:
        pass

def process_similar_compounds(drug_name, top_n):
    print(f"Checking for similar compounds for drug: {drug_name}")
    similar_compounds = get_similar_compounds(drug_name, top_n)
    print(f"Similar compounds: {similar_compounds}")

    results = []

    for compound in similar_compounds:
        print(f"Processing for compound: {compound}")

        # Create a result dictionary with only the similarity between drug_name and compound
        result = {
            "nodes": [drug_name, compound], 
            "relationships": ["is similar to"]
        }

        try:
            url = get_url(compound)
            gene_data = parse_elements(get_url(compound), compound)
            if gene_data:
                # On successful retrieval of gene data, 
                # add each gene to nodes and create a new relationship
                for gene in gene_data:
                    result["nodes"].append(gene[1]) # Append the gene to Nodes
                    result["relationships"].append("which has the target") # Append the relationship
        except Exception:
            print(f"Skipping due to errors for compound {compound}")

        # Append the result to results after processing each compound
        results.append(result)
    
    # This will output the list of result dictionaries
    print(results)
    return results



drug_name = "STYRAMATE"

question = "yes?"

def drug_query(string, question, progress_callback=None):
    paths = process_similar_compounds(string, 100)
    selected_paths, selected_nodes, unique_rels = select_paths(paths, question, len(paths), len(paths), progress_callback)
    return selected_paths, selected_nodes, unique_rels

def drug_query_new(string,question):
    paths = process_similar_compounds(string, 100)
    selected_paths, selected_nodes, unique_rels = select_paths(paths, question, len(paths), len(paths), progress_callback)
    return selected_paths, selected_nodes, unique_rels