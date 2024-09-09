import pandas as pd
import requests
import streamlit as st
import re
from urllib.parse import quote_plus

@st.cache_data
def get_taxonomy_definition(ssyk_code):
    url = f"https://taxonomy.api.jobtechdev.se/v1/taxonomy/specific/concepts/ssyk?ssyk-code-2012={ssyk_code}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            first_item = data[0]
            definition = first_item.get('taxonomy/definition', 'Ingen beskrivning tillgänglig')
        else:
            definition = 'Ingen beskrivning tillgänglig'
        
    except requests.RequestException as e:
        print(f"API-fel: {e}")
        definition = 'Ingen beskrivning tillgänglig'
    
    return definition

@st.cache_data
def process_data(search_terms):
    df = pd.read_csv('finaldataset.csv')

    if df.empty:
        st.error("Kunde inte läsa in datasetet.")
        return []

    # Dela upp söktermerna baserat på kommatecken och ta bort onödiga mellanslag
    search_terms_list = [term.strip() for term in search_terms.split(",")]
    
    results = []

    for search_term in search_terms_list:
        pattern = rf'\b{re.escape(search_term)}\b'

        matched_rows = df[df['description'].str.contains(pattern, case=False, na=False, regex=True)]

        grouped = matched_rows.groupby('occupation').agg({
            'description': 'count',
            'SSYK_code': 'first'
        }).reset_index()

        grouped = grouped.rename(columns={'description': 'count'})

        for _, row in grouped.iterrows():
            title = row['occupation']
            count = row['count']
            ssyk_code = row['SSYK_code']
            definition = get_taxonomy_definition(ssyk_code)

            # Kontrollera om posten redan finns i resultaten
            existing_result = next((item for item in results if item['title'] == title), None)
            if existing_result:
                existing_result['count'] += count  # Lägg till antalet om posten redan finns
            else:
                results.append({
                    'title': title,
                    'count': count,
                    'definition': definition
                })

    sorted_results = sorted(results, key=lambda x: x['count'], reverse=True)
    
    return sorted_results

# Streamlit app
st.title("Sök potentiella matchningar")

search_terms = st.text_input("Skriv in en eller flera söktermer, separerade med ett kommatecken:", "")

if search_terms:
    
    
    results = process_data(search_terms)
    
    if 'page' not in st.session_state:
        st.session_state.page = 0

    results_per_page = 5

    # Hantera knapptryckningarna innan vi visar resultaten
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Visa tidigare 5 resultat", key="previous"):
            if st.session_state.page > 0:
                st.session_state.page -= 1

    with col2:
        if st.button("Visa nästa 5 resultat", key="next"):
            if (st.session_state.page + 1) * results_per_page < len(results):
                st.session_state.page += 1

    # Beräkna index för aktuell sida
    start_index = st.session_state.page * results_per_page
    end_index = start_index + results_per_page

    paginated_results = results[start_index:end_index]
        # Visa sidinformation
    st.write(f"Visar resultat {start_index + 1} till {min(end_index, len(results))} av {len(results)}.")
    
    st.write("---")

    st.subheader("Sökresultat:")

    for result in paginated_results:
        title = result['title']
        definition = result['definition']
        count = result['count']

        # Generera länk till Arbetsförmedlingens platsbank med den aktuella jobbtiteln
        search_url = f"https://arbetsformedlingen.se/platsbanken/annonser?q={quote_plus(title)}"
        
        st.subheader(title)
        st.write(definition)
        st.write(f"Antal: {count}")
        
        # Lägg till dynamisk länk baserat på jobbtiteln
        st.write(f"[Sök efter {title} på Arbetsförmedlingen]({search_url})")
        st.write("---")
    
