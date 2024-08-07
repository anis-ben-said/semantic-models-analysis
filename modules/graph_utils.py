from rdflib import Graph, URIRef, Literal, Namespace, RDF
import re, json, os
repo_dir = "sldt-semantic-models"
SMA = Namespace("http://sma.org/")

# Check if the serialized graph exists in ./data/semantic-models.ttl
def serialized_graph_exists():
    return os.path.exists('./data/semantic-models.ttl')


def extract_model_version(ttl_content):
    # Define the regex pattern to match URNs starting with 'samm:io.catenax.'
    pattern = r'@prefix : <(urn:(samm|bamm):io\.catenax\.[^>]+)>'
    
    # Find the first match in the ttl_content
    match = re.search(pattern, ttl_content)
    
    # Return the match
    if match:
        return match.group(1)
    return None


def extract_used_model_versions(ttl_content):
    # Define the regex pattern to match URNs starting with 'samm:io.catenax.'
    pattern = r'@prefix ([^:]+): <(urn:(samm|bamm):io\.catenax\.[^>]+)>'
    
    # Find all matches in the ttl_content
    matches = re.findall(pattern, ttl_content)
    
    # Return the matches
    used_models = [match[1] for match in matches]

    return used_models

# example urn:samm:io.catenax.battery.battery_pass:5.0.0# should return 'urn:battery.battery_pass'
def extract_model_from_model_version(model_version):
    # Define the regex pattern to match the model URN
    pattern = r'urn:(samm|bamm):io\.catenax\.(.+):'
    
    # Find the match in the model_version
    match = re.search(pattern, model_version)
    
    # Return the match
    if match:
        return f"urn:{match.group(2)}"
    return None




def extract_model_version_status(json_content):
    # Charger le contenu JSON
    data = json.loads(json_content)
    
    # Extraire la valeur de la clé 'status'
    status_value = data.get('status')
    
    return status_value

def generate_graph_turtle_from_repo():
    # Initialiser le graphe RDF`
    g = Graph()

    # Définir les namespaces
    sma = Namespace("http://sma.org/")
    g.bind("sma", sma)

    # Définir les classes
    Model = URIRef(sma.Model)
    ModelVersion = URIRef(sma.ModelVersion)

    # Définir les propriétés
    hasVersion = URIRef(sma.hasVersion)
    uses = URIRef(sma.uses)
    status = URIRef(sma.status)

    # Parcourir tous les fichiers .ttl dans le dépôt
    for root, dirs, files in os.walk(repo_dir):
        for file in files:
            if file.endswith('.ttl'):
                file_path = os.path.join(root, file)
                
                # Lire le contenu du fichier
                with open(file_path, 'r', encoding='utf-8') as f:
                    ttl_content = f.read()
                
                # Extraire la version du modèle
                model_version = extract_model_version(ttl_content)
                model = extract_model_from_model_version(model_version)
                
                # Insérer les triplets (modele has version) dans le graphe RDF
                g.add((URIRef(model), hasVersion, URIRef(model_version)))

                # Extraire les modèles utilisés
                used_models = extract_used_model_versions(ttl_content)
                # Insérer les triplets dans le graphe RDF
                for used_model in used_models:
                    g.add((URIRef(model_version), uses, URIRef(used_model)))

                # Vérifier l'existence de metadata.json dans le même répertoire
                metadata_file_path = os.path.join(root, 'metadata.json')
                if os.path.exists(metadata_file_path):
                    with open(metadata_file_path, 'r', encoding='utf-8') as metadata_file:
                        metadata_content = metadata_file.read()
                    status_extrait = extract_model_version_status(metadata_content)
                else:
                    status_extrait = "unknown"
                
                # Ajouter le triplet model_version hasStatus status_extrait
                g.add((URIRef(model_version), status, Literal(status_extrait)))

    # Sauvegarder le graphe RDF dans un fichier
    # Directory where you want to save the file
    output_dir = './data'
    # Check if the directory exists, if not, create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    g.serialize(destination='./data/semantic-models.ttl', format='turtle')

def getModelVersions(g, model):
    model_uri = URIRef(model)
    versions = set()
    for _, _, version in g.triples((model_uri, SMA.hasVersion, None)):
        versions.add(version)
    return versions

def getModelFromVersion(g, modelVersion):
    model_version_uri = URIRef(modelVersion)
    for model, _, _ in g.triples((None, SMA.hasVersion, model_version_uri)):
        return model
    return None

def getModelVersionStatus(g, modelVersion):
    model_version_uri = URIRef(modelVersion)
    for _, _, status in g.triples((model_version_uri, SMA.status, None)):
        return status
    return None

def getAllModels(g):
    models = set()
    for model, _, _ in g.triples((None, SMA.hasVersion, None)):
        models.add(model)
    return models

# Fonction récursive pour parcourir le graphe RDF et obtenir tous les chemins d'utilisation, ainsi qu'une liste unique des noeuds


def get_all_use_paths(graph, start_node, paths=None, nodes=None):
    if paths is None:
        paths = []
    if nodes is None:
        nodes = set()
    
    # Ajouter le nœud de départ à l'ensemble des nœuds d'extrémité
    nodes.add(start_node)

    for _, _, end_node in graph.triples((start_node, SMA.uses, None)):
        if (start_node, SMA.uses, end_node) not in paths:
            paths.append((start_node, SMA.uses, end_node))
            nodes.add(end_node)
            get_all_use_paths(graph, end_node, paths, nodes)

    return paths, nodes

# Fonction récursive pour détecter les boucles
def detect_cycles(graph, current_node, visited=None, stack=None, all_cycles=None):
    if visited is None:
        visited = set()
    if stack is None:
        stack = []
    if all_cycles is None:
        all_cycles = set()

    stack.append(current_node)

    for _, _, next_node in graph.triples((current_node, SMA.uses, None)):
        if next_node in stack:
            cycle = tuple(stack[stack.index(next_node):] + [next_node])
            all_cycles.add(cycle)
        elif next_node not in visited:
            visited.add(next_node)
            detect_cycles(graph, next_node, visited, stack, all_cycles)

    stack.pop()

    return all_cycles


def detect_deprecated_usages(graph, model_version, deprecated_usages=None):
    if deprecated_usages is None:
        deprecated_usages = set()

    paths, nodes =  get_all_use_paths(graph, URIRef(model_version))
    for node in nodes:
        if getModelVersionStatus(graph, node) == Literal("deprecate"):
            deprecated_usages.add(node)
    return deprecated_usages

def get_bamm_active_models(g):
    active_bamm_list = []
    for model in getAllModels(g):
        for version in getModelVersions(g, model):
            # if the version is released or draft or standardize and the name starts with bamm then add it to the list
            #if getModelVersionStatus(g, version) in ["release", "draft", "standardize"] and version.startswith("urn:bamm"):
            # check if the version is release draft or standardize
            if version.startswith("urn:bamm") and getModelVersionStatus(g, version) not in [Literal("release"), Literal("draft"), Literal("standardize")]:
                active_bamm_list.append(version)
    return active_bamm_list




