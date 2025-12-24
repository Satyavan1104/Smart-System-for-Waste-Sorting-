document.getElementById('viewMapBtn').addEventListener('click', function () {
    const mapContainer = document.getElementById('map-container');
    mapContainer.style.display = 'block'; // Show the map container

    // Check if the Google Maps API is already loaded, if not load it
    if (!document.querySelector('script[src*="maps.googleapis.com"]')) {
        const script = document.createElement('script');
        script.src = "https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap";
        script.defer = true;
        script.onload = () => initMap(); // Ensure initMap is called after script is loaded
        document.body.appendChild(script);
    } else {
        initMap(); // If already loaded, directly call initMap
    }
});

function initMap() {
    const locations = [
        { lat: 40.7128, lng: -74.0060, label: 'Location 1' }, // Example static data
        { lat: 34.0522, lng: -118.2437, label: 'Location 2' }
    ];

    // Initialize the map centered on the first location
    const map = new google.maps.Map(document.getElementById('map'), {
        zoom: 5,
        center: locations[0],  // Center the map on the first location
    });

    // Add markers for each location
    locations.forEach((location) => {
        new google.maps.Marker({
            position: { lat: location.lat, lng: location.lng },
            map: map,
            title: location.label,
        });
    });
}
