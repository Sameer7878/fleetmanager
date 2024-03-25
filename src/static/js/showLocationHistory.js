/*jshint esversion: 9 */
/* global console*/
/* global L*/
/* global map */

/* global alert*/
const map = L.map('map').setView([14.028572109658956, 80.0218235993725], 15); // Set initial map view
var selectedLocation = L.marker([0, 0], {draggable: true});
selectedLocation.addTo(map);
//L.geoJSON(collegesGeoJSON, {
//pointToLayer: function (feature, latlng) {
// return L.circleMarker(latlng, collegeMarkerStyle);
//}
//}).addTo(map);
// Add the OpenStreetMap tile layer
const openStreetMap = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
    maxZoom: 20,
}).addTo(map);
const googleSatellite = L.tileLayer('http://{s}.google.com/vt?lyrs=y&x={x}&y={y}&z={z}', {
    maxZoom: 20,
    subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
});

const googleStreets = L.tileLayer('http://{s}.google.com/vt?lyrs=m&x={x}&y={y}&z={z}', {
    maxZoom: 20,
    subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
});

const baseMaps = {
    "OpenStreetMap": openStreetMap,
    "Google Streets": googleStreets,
    "Google Satellite": googleSatellite
};
L.control.layers(baseMaps).addTo(map);

function getData(url = '') {
    // Default options are marked with *
    return fetch(url)
        .then(response => response.json()); // parses JSON response into native JavaScript objects
}

const busIcon = L.divIcon({
    className: 'bus-icon',
    iconSize: [32, 32], // Set the size of the icon
});

// Add the bus marker with the custom divIcon
const busMarker = L.marker([0, 0], {icon: busIcon}).addTo(map);
busMarker.id = 'bus';
let trail = L.polyline([], {color: 'red', weight: 5}).addTo(map);


// Function to update the bus marker's position and rotation and log distance
let prevLocation;

function updateBusMarker(location) {
    "use strict";
    if (!(prevLocation)) {
        rotateMapToLocation(L.latLng(location));
        busMarker.setLatLng(L.latLng(location));
        prevLocation = location;
        return 0;
    }
    const latLng = L.latLng(location);

    rotateMapToLocation(latLng);
    busMarker.setLatLng(latLng);
    trail.addLatLng(latLng);

    // Add the current position to the bus's trail

    // Calculate the angle between two points to set the rotation
    const angle = Math.atan2(location[1] - prevLocation[1], location[0] - prevLocation[0]);
    const degrees = (angle * 180) / Math.PI;
    // Set the rotation angle of the bus marker
    busMarker.options.rotationAngle = degrees;
    // console.log(busMarker.getLatLng());
    // const distance = map.distance(busMarker.getLatLng(), L.latLng(stages[stages.length - 1].stageCoord));
    // document.getElementById('remDis').innerText = (distance / 1000).toFixed(2) + " Kms";

}

function rotateMapToLocation(targetLatLng) {
    "use strict";

    if (targetLatLng) {
        // Calculate bearing between current marker position and target location
        var bearing = getBearing(busMarker.getLatLng(), targetLatLng);

        // Smoothly rotate the map
        map.setView(targetLatLng, 17, {
            animate: true,
            duration: 0.5,
            pan: {
                animate: true,
                duration: 0.5,
                easeLinearity: 0.5,
            },
            zoom: {
                animate: true,
                duration: 0.5,
            },
            bearing: bearing,
        });
    }
}

// Helper function to calculate bearing between two points
function getBearing(prevPoint, nextPoint) {
    "use strict";
    var x = Math.cos(nextPoint.lat) * Math.sin(nextPoint.lng - prevPoint.lng);
    var y = Math.cos(prevPoint.lat) * Math.sin(nextPoint.lat) -
        Math.sin(prevPoint.lat) * Math.cos(nextPoint.lat) * Math.cos(nextPoint.lng - prevPoint.lng);
    var bearing = Math.atan2(x, y);
    return (bearing * (180 / Math.PI) + 360) % 360;
}

function getTodayDate() {
    "use strict";
    // Get today's date
    var today = new Date();

// Extract day, month, and year
    var day = today.getDate();
    var month = today.getMonth() + 1; // Month is zero-based, so we add 1
    var year = today.getFullYear();

// Format day and month to have leading zeros if needed
    day = (day < 10 ? '0' : '') + day;
    month = (month < 10 ? '0' : '') + month;

// Format the date as dd-mm-yyyy
    var formattedDate = day + '-' + month + '-' + year;

    return formattedDate; // Output the formatted date

}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
let callFlag=false;
function getRouteDetails(busPlateNumber) {
    "use strict";
    if(callFlag){
        return 0;
    }
    map.removeLayer(trail);
    trail = L.polyline([], {color: 'red', weight: 5}).addTo(map);
    getData('/apis/getLocationHistory?busPlateNumber=' + busPlateNumber + "&dateString=" + getTodayDate())
        .then(async data => {
            console.log(data);
            callFlag=true;
            for (var i = 0; i < data.locationHistory.length; i++) {
                updateBusMarker(data.locationHistory[i]);
                await sleep(200);
            }
            callFlag=false;
        })
        .catch(error => {
            console.error('Error:', error);
        });
}