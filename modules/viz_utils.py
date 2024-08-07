
from modules.graph_utils import getAllModels, getModelVersions, get_all_use_paths, getModelVersionStatus
import streamlit as st
from st_link_analysis.component.layouts import LAYOUTS
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle


def draw_model_graph(g, modelVersion):
    # initialize the dictionary elements with 2 keys: nodes and edges and empty lists as values
        elements = {"nodes": [], "edges": []}
        # Obtenir tous les chemins
        use_paths, nodes = get_all_use_paths(g, modelVersion)


        for start, predicate, end in use_paths:
            elements["edges"].append({"data": {"id": f"{start}-{end}","label": "uses", "source": start, "target": end}})

        for node in nodes:
            # extraire nom du modèle en supprimant le début jusqu'à "catenax."
            model_name = node.split("catenax.")[-1]
            # "is selected" boolean variable true where model_name is equal to selected_version            
            
            status = getModelVersionStatus(g, node)
            
            elements["nodes"].append({"data": {"id": node, "label": status, "name": model_name, "status": status}})
        st.divider()
        st.markdown("#### Styles customization")
        left, middle, right = st.columns([2, 2, 1])
        with left:
            left1, left2, left3, left4 = st.columns(4)
            with left1:
                color_draft = st.color_picker("draft", value="#FFEEAD")
            with left2:
                color_release = st.color_picker("release", value="#96CEB4")
            with left3:
                color_standardize = st.color_picker("standardize", value="#FFAD60")
            with left4:
                color_deprecate = st.color_picker("deprecate", value="#A02334")
        #st.markdown("### Edge Styles")
        CURVE_STYLES = [
            "bezier",
            "haystack",
            "straight",
            "unbundled-bezier",
            "round-segments",
            "segments",
            "round-taxi",
            "taxi",
        ]
        with middle:
            middle1, middle2 = st.columns(2)
            with middle1:
                curve_style = st.selectbox("Curve Style", CURVE_STYLES)
            with middle2:
                line_color = st.color_picker("Line Color", value="#808080")

        #st.markdown("### Layout Algorithms")

        with right:
            LAYOUT_NAMES = list(LAYOUTS.keys())
            layout = right.selectbox("Layout Name", LAYOUT_NAMES, index=0)



        #2A629A
        #FF7F3E
        # Style node & edge groups
        node_styles = [
            #NodeStyle("Model", "#FF7F3E", "name", "folder"),
            NodeStyle("release", color_release, "name", "description"),
            NodeStyle("draft", color_draft, "name", "description"),
            NodeStyle("deprecate", color_deprecate, "name", "description"),
            NodeStyle("standardize", color_standardize, "name", "description"),

        ]

        edge_styles = [
            EdgeStyle("uses",line_color, True, True, curve_style),
        ]
    

        # Render the component
        st.markdown(f"#### {modelVersion} graph")
        st_link_analysis(elements, layout, node_styles, edge_styles,height=600)
