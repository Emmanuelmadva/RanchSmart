import folium
import os

def generate_map():
    """Génère une carte Folium et retourne le chemin du fichier HTML."""
    # Crée la carte centrée sur une position (latitude, longitude)
    m = folium.Map(location=[3.848, 11.502], zoom_start=13)

    # Exemple : ajout d’un marqueur
    folium.Marker(
        [3.848, 11.502],
        popup="Zone d'enclos 1",
        tooltip="Cliquer pour plus d'infos"
    ).add_to(m)

    # Dossier de sortie
    output_dir = os.path.join("app", "static", "maps")
    os.makedirs(output_dir, exist_ok=True)

    map_path = os.path.join(output_dir, "map.html")
    m.save(map_path)
    return map_path
