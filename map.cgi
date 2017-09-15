#!/usr/bin/haserl
Content-type: text/html

<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">

<%
# config #

# To get input data there are two ways:
# 1. luci - download luci maps, 2. get from local latlon_file
mode="luci"
# If mode is luci then download the decentral map from these hosts
# first one is tried first and so on until download succeeded
hosts="10.11.10.8 10.11.10.1"

# if mode is latlon then read data from a local latlon file
latlon_file="/tmp/latlon.js"
%>


<html>
<head>
    <title>Map</title>
    <link rel="stylesheet" href="https://openlayers.org/en/v4.3.2/css/ol.css" type="text/css">
    <script src="https://cdn.polyfill.io/v2/polyfill.min.js?features=requestAnimationFrame,Element.prototype.classList,URL"></script>
    <script src="https://openlayers.org/en/v4.3.2/build/ol.js"></script>
    <style>
        body {margin:0}
        #ffmap {
            position:relative;
            width:100%;
            height:640px;
        }
        .ol-popup {
            background-color: #fff;
            padding: 10px;
            border-radius: 5px;
        }
    </style>
</head>

<body>

<noscript>No JavaScript, no map. sorry.</noscript>

<div id="ffmap" tabindex="0"></div>
<div id="popup" class="ol-popup">
    <a href="#" id="popup-closer" class="ol-popup-closer"></a>
    <div id="popup-content"></div>
</div>

<script type="text/javascript">
    var zoomLevel = 16;
    var alias = new Array;
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

    function Mid(mainip, aliasip) {
        alias[aliasip] = mainip;
    }

    function Node(mainip, lat, lon, ishna, hnaip, name) {

        //points[mainip] = ol.proj.fromLonLat([lon, lat]);
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
            })),
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
            })),
        );
        feature.setStyle(featureIconStyle);
        markers.push(feature);
        map.getView().setCenter(ol.proj.fromLonLat([lon, lat]));
        map.getView().setZoom(zoomLevel);
    }

    function Link(fromip, toip, lq, nlq, etx) {
        if (0 == lineid && null != window.ffmapstatic) ffmapstatic();
        if (null != alias[toip]) toip = alias[toip];
        if (null != alias[fromip]) fromip = alias[fromip];
        if (null != points[fromip] && null != points[toip]) {
            var w = 1;
            if (etx < 4) w++;
            if (etx < 2) w++;

            //console.log(points);

            var coords = [ol.proj.fromLonLat(points[fromip]), ol.proj.fromLonLat(points[toip])];
            // var coords = ol.proj.fromLonLat(fromip);

            //console.log(coords);

            var linesColor = "rgba(102," + Math.floor(lq * 255.0) + "," + Math.floor(nlq * 255.0) + ",1.0)";
            //console.log(linesColor);

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


//            map.AddPolyline(new VEPolyline('id' + lineid, [points[fromip], points[toip]],
//                new VEColor(102, Math.floor(lq * 255.0), Math.floor(nlq * 255.0), 1.0), w));
        }
        else {
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
                center: [0, 0],
                zoom: zoomLevel
            })
        });

    <%
        if [ "$mode" = "luci" ]; then
            for h in $hosts; do
                if [ -z "$result" ]; then
                    # result = "`wget -q http://$h/cgi-bin/luci/freifunk/map/content -O - |grep -e '^Mid' -e '^Self' -e '^Node' -e '^PLink' -e '^Link'`"
                    result="`wget -q http://$h/cgi-bin/luci/freifunk/map/content -O - |grep  -e '^Mid' -e '^Self' -e '^Node' -e '^PLink' -e '^Link'`"
                fi
            done
        fi

        if [ "$mode" = "latlon" ]; then
            cat $latlon_file
        fi

        echo "$result" | sed 's/INFINITE/99.999/g'
    %>

        var vectorSource = new ol.source.Vector({
            features: markers
        });

        vectorLayer = new ol.layer.Vector({
            source: vectorSource,
            style: iconStyle,
        });




        //console.log(lines);
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
//            var hdms = ol.coordinate.toStringHDMS(ol.proj.transform(
//                coordinate, 'EPSG:3857', 'EPSG:4326'));

            var feature = map.forEachFeatureAtPixel(evt.pixel, function(feature, layer) {
                //you can add a condition on layer to restrict the listener
                return feature;
            });
            if (feature) {
                //console.log(feature);
                var properties = feature.getProperties();
                //console.log(properties);

                if (properties['type'] === 'node') {
                    content.innerHTML = '<h2>' + properties['mainip'] + '</h2>';
                    content.innerHTML += '<p>'+ properties['name'] + '</p>'

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

</script>

</body>
</html>
