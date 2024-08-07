import streamlit as st
from st_link_analysis.component.layouts import LAYOUTS
from modules.graph_utils import getAllModels, getModelVersions 
from modules.viz_utils import draw_model_graph
from rdflib import Graph

def main():
    st.set_page_config(layout="wide")
    st.markdown("# Models Dependency Graph")


    repo_dir = "sldt-semantic-models"
    ## import graph from turtle file
    g = Graph()
    # parse the turtle file in data folder
    g.parse("data/semantic-models.ttl", format="turtle")

    st.markdown("### Model selection")

    # Define the first list and a dictionary to map the second list values based on the first list selection
    # Initialize the first list with getAllModels() ordered alphabetically
    models_list = sorted(getAllModels(g))

    # Initialisze second list with a dictionnary constructed from the first list where each key is a model and the value is a list of versions from getModelVersions sorted alphabetically
    models_versions_dict = {model: sorted(getModelVersions(g, model)) for model in models_list} 

    selection_cols = st.columns(2)

    # Create a selectbox for the first list
    selected_model = selection_cols[0].selectbox('Select a Model:', models_list)

    # Based on the selected value from the first list, get the corresponding second list
    second_list = models_versions_dict[selected_model]

    # Create a selectbox for the second list
    selected_version = selection_cols[1].selectbox('Select a Version:', second_list)

    st.text(selected_version)
    draw_model_graph(g, selected_version)

          
if __name__ == "__main__":
    main()
