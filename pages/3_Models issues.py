import streamlit as st
from rdflib import Graph, URIRef, Literal, Namespace, RDF
import importlib
import modules
from modules.graph_utils import getAllModels, getModelVersions, get_all_use_paths, detect_cycles, getModelVersionStatus, detect_deprecated_usages, get_bamm_active_models
from modules.viz_utils import draw_model_graph
from modules.repo_utils import parse_repo_for_missing_files
import pandas as pd
importlib.reload(modules.graph_utils)


def main():
    st.set_page_config(layout="wide")
    st.markdown("# Models Issues")


    repo_dir = "sldt-semantic-models"
    ## import graph from turtle file
    g = Graph()
    # parse the turtle file in data folder
    g.parse("data/semantic-models.ttl", format="turtle")

    issues_list = ('draft/release/standardize model using deprecated one', 'Circular dependency', 'Missing files', 'Active bamm models')
    selected_issue = st.selectbox('Select an issue:', issues_list)
    if selected_issue == 'Circular dependency':
        circular_issues = []
        for model in getAllModels(g):
            for modelVersion in getModelVersions(g, model):
                cycles = detect_cycles(g, modelVersion)
                # if cycles is not empty
                if cycles:
                    circular_issues.append(modelVersion)
                    #st.write(f"{modelVersion} has a circular dependency")
                    #for cycle in cycles:
                    #    st.text(" -> ".join(str(node) for node in cycle))
                    #draw_model_graph(g, modelVersion)    
        selected_circular_issue = st.selectbox(f"Select one model version ({len(circular_issues)}) :", circular_issues)
        st.write(f"{selected_circular_issue} has a circular dependency")
        for cycle in detect_cycles(g, selected_circular_issue):
            st.text(" -> ".join(str(node) for node in cycle))
        draw_model_graph(g, selected_circular_issue)
    elif selected_issue == 'draft/release/standardize model using deprecated one':
        deprecated_issues = []
        for model in getAllModels(g):
            for modelVersion in getModelVersions(g, model):
                if getModelVersionStatus(g, modelVersion) != Literal('deprecate'):
                    depreacted_usages = detect_deprecated_usages(g, modelVersion)
                    if depreacted_usages:
                        deprecated_issues.append(modelVersion)
        selected_deprecated_issue = st.selectbox(f"Select one model version ({len(deprecated_issues)}) :", deprecated_issues)
        st.write(f"{selected_deprecated_issue} is using a deprecated model")
        draw_model_graph(g, selected_deprecated_issue)

    elif selected_issue == 'Missing files':
        st.write("Checking for missing files in the repository")   
        without_metadata, without_ttl, no_versions = parse_repo_for_missing_files(repo_dir)
        cols = st.columns(3)
        with cols[0]:
            col0_title =f"Directories without metadata.json file ({len(without_metadata)})"
            df_without_metadata = pd.DataFrame({col0_title: pd.Series(without_metadata).astype(str)})
            st.data_editor(
                df_without_metadata,
                column_config={
                    col0_title: st.column_config.TextColumn(
                        col0_title,
                        help="Streamlit **widget** commands 🎈",
                        default="st.",
                        max_chars=100,
                    )
                }
            )
        with cols[1]:
            col1_title = f"Directories without ttl file ({len(without_ttl)})"
            df_without_ttl = pd.DataFrame({col1_title: pd.Series(without_ttl).astype(str)})
            st.data_editor(
                df_without_ttl,
                column_config={
                    col1_title: st.column_config.TextColumn(
                        col1_title,
                        help="Streamlit **widget** commands 🎈",
                        default="st.",
                        max_chars=100,
                    )
                }
            )
        with cols[2]:
            col2_title = f"Models without version ({len(no_versions)})"
            df_no_versions = pd.DataFrame({col2_title: pd.Series(no_versions).astype(str)})
            st.data_editor(
                df_no_versions,
                column_config={
                    col2_title: st.column_config.TextColumn(
                        col2_title,
                        help="Streamlit **widget** commands 🎈",
                        default="st.",
                        max_chars=100,
                    )
                }
            )
    elif selected_issue == 'Active bamm models':
        active_bamm_list = get_bamm_active_models(g)
        active_bamm_title = f"Models without version ({len(active_bamm_list)})"
        df_active_bamm = pd.DataFrame({active_bamm_title: pd.Series(active_bamm_list).astype(str)})
        st.data_editor(
            df_active_bamm,
            column_config={
                active_bamm_title: st.column_config.TextColumn(
                    active_bamm_title,
                    help="Streamlit **widget** commands 🎈",
                    default="st.",
                    max_chars=100,
                )
            }
        )



if __name__ == "__main__":
    main()
