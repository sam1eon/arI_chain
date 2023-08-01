import pandas as pd
import requests
from CustomLibrary.Graph_Utils import select_paths

def get_umls_id(search_string: str) -> str:
    api_key = "7cc294c9-98ed-486b-add8-a60bd53de1c6"
    base_url = "https://uts-ws.nlm.nih.gov/rest/search/current"
    query = f"?string={search_string}&inputType=atom&returnIdType=concept&apiKey={api_key}"
    url = f"{base_url}{query}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        results = data["result"]["results"]
        if results:
            filtered_results = [result for result in results if search_string.lower() in result['name'].lower()]
            if filtered_results:
                top_result = filtered_results[0]
                return top_result['ui']
        return None
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")

def disease_query(string, question):
    umls_id = get_umls_id(string)
    df = pd.read_csv('top_15_av_sim.csv')
    matched_rows = df[df['dis'] == umls_id]
    disease = string
    if matched_rows.empty:
        print(f"No matches found for UMLS_ID: {umls_id}")
        return None
    else:
        output = []
        for index, row in matched_rows.iterrows():
            score = row['av.sim']
            nodes = [disease, row['gene']]
            relationships = ['ASSOCIATED_WITH']
            output.append({'nodes': nodes, 'relationships': relationships})

        print(output)
        progress_callback = None
        selected_paths, selected_nodes, unique_rels, selected_paths_stage2 = select_paths(output, question, 15, 15, progress_callback)
        return selected_paths, selected_nodes, unique_rels

def disease_query_new(string, question):
    umls_id = get_umls_id(string)
    df = pd.read_csv('top_15_av_sim.csv')
    matched_rows = df[df['dis'] == umls_id]
    disease = string
    if matched_rows.empty:
        print(f"No matches found for UMLS_ID: {umls_id}")
        return None
    else:
        output = []

        for index, row in matched_rows.iterrows():
            score = row['av.sim']
            gene = row['gene']
            nodes = [ disease, gene]
            relationships = ['ASSOCIATED_WITH']
            output.append({'nodes': nodes, 'relationships': relationships})

        print(output)
        del df, matched_rows
        return output