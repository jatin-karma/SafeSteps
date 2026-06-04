const sosButtons = [
  document.getElementById('sos-btn'),
  document.getElementById('sos-sidebar')
].filter(Boolean)

sosButtons.forEach((btn) => {
  btn.addEventListener('click', (event) => {
    event.preventDefault()
    navigator.geolocation.getCurrentPosition((pos) => {
      const lat = pos.coords.latitude
      const lng = pos.coords.longitude
      const mapsLink = `https://maps.google.com/?q=${lat},${lng}`

      // Pre-filled WhatsApp message with live location
      const message = encodeURIComponent(
        `🚨 SOS — I need help! My current location: ${mapsLink}`
      )

      // Opens WhatsApp — works on mobile instantly
      window.open(`https://wa.me/?text=${message}`, '_blank')
    })
  })
})