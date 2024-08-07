import streamlit as st
import pandas as pd
from modules.repo_utils import parse_repo_metadata

def main():
    st.title("Models Metadata")
    repo_dir = "sldt-semantic-models"
    directories_without_metadata, metadata_dict = parse_repo_metadata(repo_dir)
    st.write("Directories without metadata.json file:")
    for directory in directories_without_metadata:
        st.markdown("- " + directory)
    
        # Loop through the keys of metadata_dict
        for key, sub_dict in metadata_dict.items():
            st.header(key)  # Print the key as a header
            
            # Get the number of subkeys
            num_subkeys = len(sub_dict.keys())
            # Calculate the number of rows needed
            num_rows = (num_subkeys + 1) // 2  # +1 to handle odd number of subkeys

            # Loop through the sub-dictionary and print subkey and subvalue in columns
            sub_dict_items = list(sub_dict.items())
            for row in range(num_rows):
                cols = st.columns(2)  # Create 2 columns per row
                for col_index in range(2):
                    item_index = row * 2 + col_index
                    if item_index < num_subkeys:
                        subkey, subvalue = sub_dict_items[item_index]
                        # Supprimer le préfixe "io.catenax." de chaque élément dans la liste
                        cleaned_subvalue = [item.replace("io.catenax.", "") for item in subvalue]

                        # Ajouter le nombre de valeurs dans le titre de la colonne
                        column_title = f"{subkey} ({len(cleaned_subvalue)})"

                        with cols[col_index]:
                            df_modeles_list = pd.DataFrame({column_title: cleaned_subvalue})
                            # Use the DataFrame in the st.data_editor function
                            st.data_editor(
                                df_modeles_list,
                                column_config={
                                    column_title: st.column_config.TextColumn(
                                        column_title,
                                        help="Streamlit **widget** commands 🎈",
                                        default="st.",
                                        max_chars=100,
                                        validate="^st\.[a-z_]+$",
                                    )
                                }
                            )

if __name__ == "__main__":
    main()
