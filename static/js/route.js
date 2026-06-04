async function getSafeRoute() {
  const start = document.getElementById('start').value
  const end = document.getElementById('end').value

  // Get all incidents and find ones "near" the route
  // Simple approach: incidents within ~500m of a bounding box between start/end
  const allIncidents = await fetchIncidentsFromFirebase()
  const nearbyIncidents = filterIncidentsNearRoute(allIncidents, start, end)

  // Call Flask backend for AI narration
  const res = await fetch('/api/narrate-route', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ start, end, incidents: nearbyIncidents })
  })
  const data = await res.json()

  // Show narration card
  document.getElementById('narration-text').textContent = data.narration
  document.getElementById('risk-score').textContent = data.risk_score + '/10'
  document.getElementById('risk-badge').style.background =
    data.risk_score >= 7 ? '#ef4444' :
    data.risk_score >= 4 ? '#f97316' : '#22c55e'
}