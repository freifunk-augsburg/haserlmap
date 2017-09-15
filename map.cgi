#!/usr/bin/haserl
Content-type: text/html

<!DOCTYPE html>

<%
    . ./.config
%>

<html>
<head>
    <title>Map</title>
    <link rel="stylesheet" href="https://openlayers.org/en/v4.3.2/css/ol.css" type="text/css">
    <style>
        body {margin:0}
        #ffmap {
            position:relative;
            width:100%;
            height:640px;
        }

        .hidden {
            display: none;
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

<div id="ffmap" tabindex="0" data-zoom="<% echo -n $ZOOM_LEVEL %>" data-lat="<% echo -n $LAT %>" data-lon="<% echo -n $LON %>"></div>
<div id="popup" class="ol-popup">
    <a href="#" id="popup-closer" class="ol-popup-closer">X</a>
    <div id="popup-content"></div>
</div>

<div id="node-data" class="hidden">
<%
if [ "$MODE" = "luci" ]; then
for h in $HOSTS; do
if [ -z "$result" ]; then
# result = "`wget -q http://$h/cgi-bin/luci/freifunk/map/content -O - |grep -e '^Mid' -e '^Self' -e '^Node' -e '^PLink' -e '^Link'`"
result="`wget -q http://$h/cgi-bin/luci/freifunk/map/content -O - |grep  -e '^Mid' -e '^Self' -e '^Node' -e '^PLink' -e '^Link'`"
fi
done
fi

if [ "$MODE" = "latlon" ]; then
cat $LATLON_FILE
fi

echo "$result" | sed 's/INFINITE/99.999/g'
%>
</div>

<script src="https://cdn.polyfill.io/v2/polyfill.min.js?features=requestAnimationFrame,Element.prototype.classList,URL"></script>
<script src="https://openlayers.org/en/v4.3.2/build/ol.js"></script>
<script src="<% echo $STATIC_PATH %>/map.js"></script>

</body>
</html>
