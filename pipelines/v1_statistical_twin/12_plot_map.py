import folium
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687")
m = folium.Map(location=[32.60, 51.71], zoom_start=13,
    tiles="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png", attr="CartoDB")

with driver.session() as session:
    result = session.run("MATCH (c:Capsule) RETURN c.center_lat AS lat, c.center_lon AS lon, c.iss_weight AS w, c.gss_context AS gss")
    for r in result:
        folium.CircleMarker(location=[r['lat'], r['lon']],
            radius=max(3, min(12, int(r['w'] ** 0.5))),
            color='blue' if r['gss'] > 20 else 'red',
            fill=True, fill_opacity=0.6).add_to(m)

m.save('/home/hmid/ssan-data/isfahan_capsules.html')
print("Map saved.")
driver.close()
