// Function to generate cards for drivers
/*jshint esversion: 9 */
/* global console*/
/* global L*/

/* global alert*/


// Event listener for filtering cards on input change
document.getElementById("searchInput").addEventListener("input", filterCards);

// Function to filter and display cards based on search input
function filterCards() {
    "use strict";
    var input, filter, cards, card, driverName, i;
    input = document.getElementById("searchInput");
    filter = input.value.toUpperCase();
    cards = document.getElementById("cards").getElementsByClassName("card");

    for (i = 0; i < cards.length; i++) {
        card = cards[i];
        driverName = card.getElementsByClassName("driverName")[0];
        if (driverName) {
            if (driverName.innerHTML.toUpperCase().indexOf(filter) > -1) {
                card.style.display = "";
            } else {
                card.style.display = "none";
            }
        }
    }
}

let getLocationPromise = () => {
    "use strict";
    return new Promise(function (resolve, reject) {
        // Promisifying the geolocation API
        console.log(navigator);
        navigator.geolocation.getCurrentPosition((position) => resolve(new Array(position.coords.latitude, position.coords.longitude)), (error) => reject(error));
    });
};

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function postData(url = '', data = {}) {
    // Default options are marked with *
    return fetch(url, {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data) // body data type must match "Content-Type" header
    })
        .then(response => response.json()); // parses JSON response into native JavaScript objects
}

// Function to make a GET request
function getData(url = '') {
    // Default options are marked with *
    return fetch(url)
        .then(response => response.json()); // parses JSON response into native JavaScript objects
}

const map = L.map('map').setView([14.028572109658956, 80.0218235993725], 15); // Set initial map view
var selectedLocation = L.marker([0, 0], {draggable: true});
selectedLocation.addTo(map);
document.getElementById('locateMe').addEventListener('click', async () => {
    "use strict";
    const curLoc = await getLocationPromise();
    console.log(curLoc);
    map.setView(curLoc);
    selectedLocation.setLatLng(curLoc);
    document.getElementById('stage-coordinates').value = new Array(curLoc[0].toFixed(8), curLoc[1].toFixed(8));


});
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
let allStages = [];
let stageMarkers = [];
let assignedStage = [];
let routingControl = L.Routing.control({});
let routeDetails = {};
// Add the marker to the map
map.on('click', function (e) {
    "use strict";
    var latlng = e.latlng;
    selectedLocation.setLatLng(latlng);
    document.getElementById('stage-coordinates').value = new Array(latlng.lat.toFixed(8), latlng.lng.toFixed(8));

});
selectedLocation.on('drag', function (e) {
    var latlng = e.latlng;
    selectedLocation.setLatLng(latlng);
    document.getElementById('stage-coordinates').value = new Array(latlng.lat.toFixed(8), latlng.lng.toFixed(8));
});


function showShortestPath(wayPoints, edit = false, routeId = "", areaName = "", routeName = "", busNumber = "", busPlateNumber = "", driverName = "", driverMobile = "") {
    stageMarkers.forEach(function (marker) {
        map.removeLayer(marker); // Remove each marker from the map
    });
    assignedStage = stageMarkers;
    stageMarkers = [];
    map.removeControl(routingControl);
    routingControl = L.Routing.control({
        waypoints: wayPoints,
        lineOptions: {
            styles: [{color: 'blue', opacity: 0.6, weight: 15}]
        }
    }).addTo(map);
    routingControl.on('routesfound', function (e) {
        // Get the routes from the event object
        var routes = e.routes;
        // Iterate over each route
        routeDetails.routes = routes;
        for (var i = 0; i < routes[0].waypoints.length; i++) {
            allStages[i][0] = [routes[0].waypoints[i].latLng.lat, routes[0].waypoints[i].latLng.lng];
        }
    });
    document.getElementsByClassName('leaflet-routing-container')[0].remove();
    if (document.getElementById('addBusForm')) {
        return 0;
    }
    const submitButton = `<form class="addBusForm" id="addBusForm">
        <h4>Enter Route Details </h4>
        <input type="text" name="areaName" placeholder="Enter Route/Area Name..." value="${areaName}"><br>
        <input type="text" name="routeName" placeholder="Enter subName like Via Bustand... " value="${routeName}"<br>
        <input type="text" name="busNumber" placeholder="Enter Bus No..." value="${busNumber}"><br>
        <input type="text" name="busPlateNumber" placeholder="Enter Bus Plate Number.. " value="${busPlateNumber}"<br>
        <input type="text" name="driverName" placeholder="Enter Driver Name" value="${driverName}"><br>
        <input type="text" name="driverMobile" placeholder="Enter Driver Mobile No.. " value="${driverMobile}"<br>
        </form><button type="button" class="custom-button" id="submitbtn" onclick="submitRoute(${edit},'${routeId}')">Create Route</button>`;
    document.getElementsByClassName('container2')[0].insertAdjacentHTML('beforeend', submitButton);
}

function updateStages(stageName, stageCoord) {
    "use strict";
    var stageInputs = document.getElementById("stage-inputs");
    var stageInput = `
            <div class="stage-input extra"  id="stageInput-${allStages.length}">
            <label for="stage-${allStages.length}">Stage ${allStages.length}:</label>
            <input type="text" id="stage-${allStages.length}-name" value="${stageName}" onblur="changeStageName(this.id)">
            <input type="text" id="stage-${allStages.length}-coordinates" value="${stageCoord}" readonly onfocus="changeStageCoord(this.id)"> <button id="stage-${allStages.length}-remove" class="custom-button" onclick="removeStage(this.id)"> Remove</button></div>
        `;
    stageInputs.insertAdjacentHTML('beforebegin', stageInput);
}


function addStage() {
    var stageName = document.getElementById('stage-name').value;
    var stageCoord = document.getElementById('stage-coordinates').value;
    stageCoord = stageCoord.split(",").map(parseFloat);
    allStages.push([stageCoord, capitalizeFirstLetter(stageName)]);
    updateStages(capitalizeFirstLetter(stageName), stageCoord);

    let marker = L.marker(stageCoord, {draggable: false}).addTo(map).bindPopup(capitalizeFirstLetter(stageName), {
        autoClose: false, closeOnClick: false
    }).openPopup();
    stageMarkers.push(marker);
    selectedLocation.setLatLng([0, 0]);
    document.getElementById('stage-name').value = '';
    document.getElementById('stage-coordinates').value = '';
    console.log(allStages);
}


function calculateRoute(edit = false, routeId = "", areaName = "", routeName = "", busNumber = "", busPlateNumber = "", driverName = "", driverMobile = "") {
    showShortestPath(allStages.map(function (stage) {
        return stage[0];
    }), edit, routeId, areaName, routeName, busNumber, busPlateNumber, driverName, driverMobile);
}

function generateCard(busPlateNumber, driverName, areaName, routeName, busNumber) {
    "use strict";
    var card = `<div class="card" onClick="editRouteDetails('${busPlateNumber}')" id="${busPlateNumber}">
        <h2 class="driverName">${driverName}</h2>
        <p>${busNumber}</p>
        <p>${areaName} (${routeName})</p>
    </div>`;
    document.getElementById('cards').insertAdjacentHTML('beforeend', card);
}

function submitRoute(edit = false, routeId = "") {
    var routeForm = document.getElementById('addBusForm');
    let formData = new FormData(routeForm);
    routeDetails.allStages = allStages;
    routeDetails = {...routeDetails, ...Object.fromEntries(formData)};
    console.log(routeDetails);
    if (edit) {
        routeDetails.routeId = routeId;
        postData('/apis/updateData/?type=route', routeDetails).then(data => {
            console.log(data);
            alert("Route Updated Successfully.");
            document.getElementById(data.busPlateNumber).remove();
            generateCard(data.busPlateNumber, data.driverName, data.areaName, data.routeName, data.busNumber);
            map.removeControl(routingControl);
            document.getElementById('addBusForm').remove();
            document.querySelectorAll('.extra').forEach(f => f.remove());
            document.getElementById('submitbtn').remove();
            return 0;
        });
        return 0;
    }
    postData('/apis/addroute', routeDetails)
        .then(data => {
            console.log(data);
            generateCard(data.busPlateNumber, data.driverName, data.areaName, data.routeName, data.busNumber);
            alert("Route Created Successfully.");// JSON data parsed by `response.json()` call
            map.removeControl(routingControl);
            document.getElementById('addBusForm').remove();
            document.querySelectorAll('.extra').forEach(f => f.remove());
            document.getElementById('submitbtn').remove();
        })
        .catch(error => {
            alert(error);
            console.error('Error:', error);
        });
}

function editRouteDetails(busPlateNumber) {
    "use strict";
    getData('/apis/getRouteData/?busPlateNumber=' + busPlateNumber)
        .then(data => {
            const routeData = data;
            routeData.routeStageWithNames.forEach(stage => {
                document.getElementById('stage-name').value = stage.stageName;
                document.getElementById('stage-coordinates').value = stage.stageCoord;
                addStage();
            });
            document.getElementById('calculateRoute').setAttribute('onclick', `calculateRoute(edit = ${true}, routeId = '${routeData.routeId}',areaName='${routeData.areaName}',routeName='${routeData.routeName}',busNumber='${routeData.busNumber}',busPlateNumber='${routeData.busPlateNumber}',driverName='${routeData.driverName}',driverMobile='${routeData.driverMobile}')`);
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function changeStageName(sid) {
    "use strict";
    map.removeControl(routingControl);
    assignedStage.forEach(mark => mark.addTo(map).openPopup());
    stageMarkers = assignedStage;
    var newValue = document.getElementById(sid).value;
    console.log(newValue, sid.split('-'))
    allStages[parseInt(sid.split('-')[1]) - 1][1] = capitalizeFirstLetter(newValue);
    stageMarkers[parseInt(sid.split('-')[1]) - 1].bindPopup(newValue);
}

function changeStageCoord(sid) {
    "use strict";
    stageMarkers[parseInt(sid.split('-')[1]) - 1].dragging.enable();
    stageMarkers[parseInt(sid.split('-')[1]) - 1].on('dragend', function (event) {
        document.getElementById(sid).value = [event.target.getLatLng().lat, event.target.getLatLng().lng];
        stageMarkers[parseInt(sid.split('-')[1]) - 1] = event.target;
        allStages[parseInt(sid.split('-')[1]) - 1][0] = [event.target.getLatLng().lat, event.target.getLatLng().lng];
    });
}

function removeStage(sid) {
    "use strict";
    if (stageMarkers.length === 0 && assignedStage.length !== 0) {
        console.log('hello');
        map.removeControl(routingControl);
        assignedStage.forEach(mark => mark.addTo(map).openPopup());
        stageMarkers = assignedStage;
    }
    console.log(parseInt(sid.split('-')[1]) - 1);
    console.log(stageMarkers);
    map.removeLayer(stageMarkers[parseInt(sid.split('-')[1]) - 1]);
    stageMarkers.pop(parseInt(sid.split('-')[1]) - 1);
    document.getElementById("stageInput-" + sid.split('-')[1]).remove();
    allStages.pop(parseInt(sid.split('-')[1]) - 1);
}
