const slider = document.getElementById('time-slider')
const timeLabel = document.getElementById('time-label')

slider.addEventListener('input', () => {
  const hour = parseInt(slider.value)

  // Format display: "09:00 AM" or "10:00 PM"
  const period = hour >= 12 ? 'PM' : 'AM'
  const display = `${hour % 12 || 12}:00 ${period}`
  timeLabel.textContent = display

  // Change map background tint based on time
  if (hour >= 20 || hour <= 5) {
    document.getElementById('map').style.filter = 'brightness(0.7)'  // dark
  } else if (hour >= 17) {
    document.getElementById('map').style.filter = 'brightness(0.85)' // dusk
  } else {
    document.getElementById('map').style.filter = 'brightness(1)'    // day
  }

  // Reload heatmap with new time filter
  loadIncidents(hour)
})