function initMap() {
    const locations = [
        { lat: 40.7128, lng: -74.0060, label: 'Location 1' }, // Replace with actual locations
        { lat: 34.0522, lng: -118.2437, label: 'Location 2' }
    ];

    const map = new google.maps.Map(document.getElementById('map'), {
        zoom: 5,
        center: locations[0],
    });

    locations.forEach((location) => {
        new google.maps.Marker({
            position: { lat: location.lat, lng: location.lng },
            map: map,
            title: location.label,
        });
    });
}

window.onload = initMap;
