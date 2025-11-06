import folium
from folium.plugins import Draw, MeasureControl
import json

# centre par défaut
m = folium.Map(location=[4.05, 9.7], zoom_start=12)  # adapte coords

# couche où seront stockés les dessins
drawn_items = folium.FeatureGroup(name="Drawn").add_to(m)

# ajout plugin draw
draw = Draw(export=True,
            filename='data.geojson',
            draw_options={
                'polyline': False,
                'polygon': True,
                'circle': False,
                'rectangle': True,
                'marker': False,
                'circlemarker': False
            },
            edit_options={'edit': True}
           )
draw.add_to(m)

# mesures
m.add_child(MeasureControl())

# Ajouter un petit script JS pour poster le dessin au parent
post_message_js = """
<script>
function sendGeoJSONToParent(geojson) {
    try {
        const payload = { action: 'draw-created', payload: { geojson } };
        // envoie au parent (même origine attendu) — adapte origin si besoin
        window.parent.postMessage(payload, window.location.origin);
    } catch(e) {
        console.error('postMessage failed', e);
    }
}

// Lorsque l'utilisateur termine le dessin (Leaflet Draw event)
map.on('draw:created', function(e) {
    var layer = e.layer;
    // on récupère le geojson
    var gj = layer.toGeoJSON();
    // on ajoute visuellement sur la carte
    drawnItems.addLayer(layer);
    sendGeoJSONToParent(gj);
});

// Gestion d'edition / suppression
map.on('draw:edited', function(e) {
    var layers = e.layers;
    layers.eachLayer(function(layer) {
        var gj = layer.toGeoJSON();
        sendGeoJSONToParent(gj);
    });
});

// clear request from parent
window.addEventListener('message', (evt) => {
    const { action } = evt.data || {};
    if (action === 'start-draw') {
        // open draw polygon tool programmatically (trigger click on button)
        const btn = document.querySelector('.leaflet-draw-draw-polygon');
        if (btn) btn.click();
    } else if (action === 'cancel-draw') {
        // cancel drawing by simulating escape
        var e = new KeyboardEvent('keydown', {key:'Escape'});
        document.dispatchEvent(e);
    } else if (action === 'clear-drawing') {
        drawnItems.clearLayers();
        window.parent.postMessage({action:'draw-cleared'}, window.location.origin);
    } else if (action === 'refresh-enclosures') {
        // ici tu peux recharger la couche des enclos via fetch depuis API si besoin
        // location.reload();
    } else if (action === 'init') {
        // initialisation si nécessaire
    }
});
</script>
"""

# Folium ne peut pas directement insérer la variable 'drawnItems' used in JS.
# On ajoute un small template to expose map and drawnItems variables:
extra_script = """
<script>
  // expose drawnItems and map (folium creates 'map' var)
  var drawnItems = window.drawnItems || (function(){
    var layer = L.featureGroup();
    map.addLayer(layer);
    window.drawnItems = layer;
    return layer;
  })();
</script>
"""

m.get_root().html.add_child(folium.Element(extra_script + post_message_js))

# Enregistrer
m.save('app/static/maps/enclosures.html')
print("Carte générée: app/static/maps/enclosures.html")
