from folium.plugins import Draw
import folium

def generate_map():
    output_path = "app/static/maps/generated_map.html"
    lat, lon = 7.417017, 13.541282

    m = folium.Map(location=[lat, lon], zoom_start=19, tiles=None, max_zoom=22, control_scale=True)

    # Calque Satellite
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        attr="Google Satellite",
        name="Satellite",
        overlay=False,
        control=True,
        max_zoom=22
    ).add_to(m)

    # Calque Routes
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=h&x={x}&y={y}&z={z}",
        attr="Google Roads",
        name="Routes",
        overlay=True,
        control=True,
        max_zoom=22
    ).add_to(m)

    # Marker du point
    folium.Marker([lat, lon], popup="Point d'intérêt").add_to(m)

    # FeatureGroup supplémentaire
    feature_group = folium.FeatureGroup(name="Calque supplémentaire")
    folium.CircleMarker([lat, lon], radius=10, color='red', fill=True, fill_opacity=0.5).add_to(feature_group)
    feature_group.add_to(m)

    # Draw plugin avec outils personnalisés
    Draw(
        export=True,
        position='topleft',
        draw_options={
            'polyline': False,
            'polygon': False,
            'circle': False,
            'rectangle': False,
            'marker': True,
            'circlemarker': False
        },
        edit_options={'edit': True, 'remove': True}
    ).add_to(m)

    # Contrôle des calques
    folium.LayerControl().add_to(m)

    m.save(output_path)
    return output_path
