
// Initialize map centered on Indore
const map = L.map('map').setView([22.7196, 75.8577], 15);

// OpenStreetMap tiles
L.tileLayer(
  'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
  {
    attribution: '© OpenStreetMap contributors'
  }
).addTo(map);

// Heatmap layer
let heatLayer = L.heatLayer([], {
  radius: 35,
  blur: 20
}).addTo(map);

// Sample incidents (replace later with Firebase)
const incidents = [
{
  lat:22.7196,
  lng:75.8577,
  severity:9,
  time_risk:'night_only',
  short_label:'Poor Lighting',
  advice:'Avoid isolated roads at night.'
},

{
  lat:22.7218,
  lng:75.8602,
  severity:6,
  time_risk:'always',
  short_label:'Unsafe Road',
  advice:'Stay alert while crossing.'
},

{
  lat:22.7175,
  lng:75.8540,
  severity:4,
  time_risk:'daytime_only',
  short_label:'Suspicious Area',
  advice:'Use the main road.'
}
];

function loadIncidents(currentHour = 22) {

  // Remove old markers
  map.eachLayer(layer => {
    if (layer instanceof L.CircleMarker) {
      map.removeLayer(layer);
    }
  });

  // Filter incidents
  const active = incidents.filter(i =>
    isActiveAtHour(i.time_risk, currentHour)
  );

  // Heatmap points
  const points = active.map(i => [
    i.lat,
    i.lng,
    i.severity / 10
  ]);

  heatLayer.setLatLngs(points);

  // Add markers
  active.forEach(i => {

    L.circleMarker(
      [i.lat, i.lng],
      {
        radius:10,
        color:severityColor(i.severity),
        fillOpacity:0.8
      }
    )
    .bindPopup(`
      <b>${i.short_label}</b><br>
      Severity: ${i.severity}/10<br>
      Risk Time: ${i.time_risk}<br>
      <i>${i.advice}</i>
    `)
    .addTo(map);

  });

}

function isActiveAtHour(time_risk, hour){

  if(time_risk==='always') return true;

  if(time_risk==='night_only')
    return hour>=20 || hour<=5;

  if(time_risk==='evening_night')
    return hour>=17;

  if(time_risk==='daytime_only')
    return hour>=6 && hour<=18;

  return true;
}

function severityColor(severity){

  if(severity>=8)
    return '#ef4444';

  if(severity>=5)
    return '#f97316';

  return '#eab308';

}

// Initial load
loadIncidents(22);

