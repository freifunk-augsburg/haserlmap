var ffmap = document.getElementById('ffmap');
var zoomLevel = ffmap.getAttribute('data-zoom');
var initLon = parseFloat(ffmap.getAttribute('data-lon'));
var initLat = parseFloat(ffmap.getAttribute('data-lat'));
var initCoords = ol.proj.fromLonLat([initLon, initLat])
var aliases = new Array;
var points = new Array;
var unkpos = new Array;
var markers = new Array;
var lines = new Array;
var container = document.getElementById('popup');
var content = document.getElementById('popup-content');
var closer = document.getElementById('popup-closer');
var lineid = 0;

/**
 * Create an overlay to anchor the popup to the map.
 */
var overlay = new ol.Overlay(/** @type {olx.OverlayOptions} */ ({
    element: container,
    autoPan: true,
    autoPanAnimation: {
        duration: 250
    }
}));

/**
 * Add a click handler to hide the popup.
 * @return {boolean} Don't follow the href.
 */
closer.onclick = function() {
    overlay.setPosition(undefined);
    closer.blur();
    return false;
};

if (!String.prototype.format) {
    String.prototype.format = function() {
        var args = arguments;
        return this.replace(/{(\d+)}/g, function(match, number) {
            return typeof args[number] != 'undefined'
                ? args[number]
                : match
                ;
        });
    };
}

// default icon style
var iconStyle = new ol.style.Style({
    image: new ol.style.Icon(/** @type {olx.style.IconOptions} */ ({
        color: '#8959A8',
        crossOrigin: 'anonymous',
        src: 'https://openlayers.org/en/v4.3.2/examples/data/dot.png'
    })),
    anchor: [0.5, 46],
    anchorXUnits: 'fraction',
    anchorYUnits: 'pixels',
});

// default lines style
var linesStyle = new ol.style.Style({
    stroke: new ol.style.Stroke(({
        width: 1
    }))
});

onload = new Function("if(null!=window.ffmapinit)ffmapinit();");

function getAliases(mainip) {
    var nodeAliases = new Array();
    Object.keys(aliases).forEach(function(key) {
        value = aliases[key];
        if (value === mainip) {
            nodeAliases.push(key);
        }
    });
    return nodeAliases;
}

function Mid(mainip, aliasip) {
    aliases[aliasip] = mainip;
}

function Node(mainip, lat, lon, ishna, hnaip, name) {
    points[mainip] = [lon, lat];
    var feature = new ol.Feature({
        geometry: new ol.geom.Point(ol.proj.fromLonLat([lon, lat])),
        type: 'node',
        mainip: mainip,
        name: name
    });

    var featureIconStyle = iconStyle.clone();
    featureIconStyle.setImage(
        new ol.style.Icon(/** @type {olx.style.IconOptions} */ ({
            color: ishna ? '#ff0000' : '#8959A8',
            crossOrigin: 'anonymous',
            src: 'https://openlayers.org/en/v4.3.2/examples/data/dot.png'
        }))
    );
    feature.setStyle(featureIconStyle);
    markers.push(feature);
}

function Self(mainip, lat, lon, ishna, hnaip, name) {
    points[mainip] = [lon, lat];
    var feature = new ol.Feature({
        geometry: new ol.geom.Point(ol.proj.fromLonLat([lon, lat])),
        mainip: mainip,
        type: 'node',
        name: name
    });

    var featureIconStyle = iconStyle.clone();
    featureIconStyle.setImage(
        new ol.style.Icon(/** @type {olx.style.IconOptions} */ ({
            color: '#0000ff',
            crossOrigin: 'anonymous',
            src: 'https://openlayers.org/en/v4.3.2/examples/data/dot.png'
        }))
    );
    feature.setStyle(featureIconStyle);
    markers.push(feature);
    map.getView().setCenter(ol.proj.fromLonLat([lon, lat]));
    map.getView().setZoom(zoomLevel);
}

function Link(fromip, toip, lq, nlq, etx) {
    if (0 == lineid && null != window.ffmapstatic) ffmapstatic();
    if (null != aliases[toip]) toip = aliases[toip];
    if (null != aliases[fromip]) fromip = aliases[fromip];
    if (null != points[fromip] && null != points[toip]) {
        var w = 1;
        if (etx < 4) w++;
        if (etx < 2) w++;

        var coords = [ol.proj.fromLonLat(points[fromip]), ol.proj.fromLonLat(points[toip])];
        var linesColor = "rgba(102," + Math.floor(lq * 255.0) + "," + Math.floor(nlq * 255.0) + ",1.0)";

        var linesStyle = new ol.style.Style({
            stroke: new ol.style.Stroke(({
                width: 1.5,
                color: linesColor
            }))
        });

        var feature = new ol.Feature({
            geometry: new ol.geom.LineString(coords),
            name: 'Line',
            type: 'link',
            fromip: fromip,
            toip: toip,
            lq: lq,
            nlq: nlq,
            etx: etx
        });

        feature.setStyle(linesStyle);
        lines.push(feature);
    } else {
        if (null == points[toip]) unkpos[toip] = '';
        if (null == points[fromip]) unkpos[fromip] = '';
    }
    lineid++;
}

function PLink(fromip, toip, lq, nlq, etx, lata, lona, ishnaa, latb, lonb, ishnab) {
    Link(fromip, toip, lq, nlq, etx);
}

function ffmapinit() {
    map = new ol.Map({
        layers: [
            new ol.layer.Tile({
                source: new ol.source.OSM()
            }),
        ],
        target: 'ffmap',
        controls: ol.control.defaults({
            attributionOptions: /** @type {olx.control.AttributionOptions} */ ({
                collapsible: false
            })
        }),
        overlays: [overlay],
        view: new ol.View({
            center: initCoords,
            zoom: zoomLevel
        })
    });

    // get the data (aka functions to add nodes/links) from hidden container in the html file and evaluate them
    var data = document.getElementById('node-data');
    eval(data.innerHTML);

    var vectorSource = new ol.source.Vector({
        features: markers
    });

    vectorLayer = new ol.layer.Vector({
        source: vectorSource,
        style: iconStyle,
    });

    var linesSource = new ol.source.Vector({
        features: lines
    });

    var linesLayer = new ol.layer.Vector({
        style: linesStyle,
        source: linesSource
    });

    map.addLayer(linesLayer);

    map.addLayer(vectorLayer);

    map.on('singleclick', function(evt) {
        var coordinate = evt.coordinate;
        var feature = map.forEachFeatureAtPixel(evt.pixel, function(feature, layer) {
            //you can add a condition on layer to restrict the listener
            return feature;
        });
        if (feature) {
            var properties = feature.getProperties();

            if (properties['type'] === 'node') {
                var nodeAliases = getAliases(properties['mainip']);
                function nodeAliasesFormatted() {
                    var ret = '';
                    for (var i = 0; i < nodeAliases.length; i++) {
                        ret += nodeAliases[i];
                        if (i < nodeAliases.length - 1) {
                            ret += ', ';
                        }
                    };
                    return ret;
                }

                content.innerHTML = '<h2>' + properties['name'] + '</h2>';
                content.innerHTML += '<p>Main IP: <a href="http://{0}" rel="nofollow">{0}</a></p>'.format(properties['mainip']);
                if (nodeAliases.length > 0) {
                    content.innerHTML += "<p>Alias IPs: {0}".format(nodeAliasesFormatted());
                }
            } else if (properties['type'] === 'link') {
                content.innerHTML = '<h2>' + properties['fromip'] + ' - ' + properties['toip'] + '</h2>';
                content.innerHTML += '<p>ETX: ' + properties['etx'] + '</p>'
                content.innerHTML += '<p>LQ: ' + properties['lq'] + '</p>'
                content.innerHTML += '<p>NLQ: ' + properties['nlq'] + '</p>'
            }
            overlay.setPosition(coordinate);
        }
    });
}