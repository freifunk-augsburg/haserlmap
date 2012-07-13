#!/usr/bin/haserl
Content-type: text/html

<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">

<%
# config #

# To get input data there are two ways:
# 1. luci - download luci maps, 2. get from local latlon_file
mode="latlon"
# If mode is luci then download the decentral map from these hosts
# first one is tried first and so on until download succeeded
hosts="10.11.0.15 10.11.0.1"

# if mode is latlon then read data from a local latlon file
latlon_file="/tmp/latlon.js"
%>



<html>
	<head>
		<title>Map</title>
	</head>

	<body style="margin:0">
		<script src="http://dev.virtualearth.net/mapcontrol/mapcontrol.ashx?v=6.1" type="text/javascript"></script>
		<script type="text/javascript">
			var alias = new Array;
			var points = new Array;
			var unkpos = new Array;
			var lineid = 0;
			onload=new Function("if(null!=window.ffmapinit)ffmapinit();");

			function Mid(mainip,aliasip)
			{
				alias[aliasip]=mainip;
			}

			function Node(mainip,lat,lon,ishna,hnaip,name)
			{
				points[mainip] = new VELatLong(lat, lon);
				map.AddPushpin(new VEPushpin(mainip, points[mainip],
				'/images/'+(ishna?'hna':'node')+'.gif', 'Node:'+name,
				'<br><img src="/images/'+(ishna?'hna':'node')+'.gif">'+
				'<br>IP:'+mainip+'<br>DefGW:'+hnaip));
			}

			function Self(mainip,lat,lon,ishna,hnaip,name)
			{
				//map.SetDashboardSize(VEDashboardSize.Small);
				map.LoadMap(new VELatLong(lat, lon), 13, VEMapStyle.Hybrid);
				map.SetScaleBarDistanceUnit(VEDistanceUnit.Kilometers);
				map.ShowMiniMap(14, 474);
				Node(mainip,lat,lon,ishna,hnaip,name);
			}

			function Link(fromip,toip,lq,nlq,etx)
			{
				if (0==lineid && null!=window.ffmapstatic) ffmapstatic();
				if (null != alias[toip]) toip = alias[toip];
				if (null != alias[fromip]) fromip = alias[fromip];
				if (null != points[fromip] && null != points[toip])
				{
					var w = 1;
					if (etx < 4) w++;
					if (etx < 2) w++;
					map.AddPolyline(new VEPolyline('id'+lineid, [points[fromip], points[toip]],
					new VEColor(102,Math.floor(lq*255.0),Math.floor(nlq*255.0),1.0), w));
				}
				else
				{
					if (null == points[toip]) unkpos[toip] = '';
					if (null == points[fromip]) unkpos[fromip] = '';
				}
				lineid++;
			}

			function PLink(fromip,toip,lq,nlq,etx,lata,lona,ishnaa,latb,lonb,ishnab)
			{
				Link(fromip,toip,lq,nlq,etx);
			}

			function ffmapinit()
			{
				if(null!=window.map)map.Dispose();

				var INFINITE = 99.99;

				map = new VEMap('ffmap');

				<%
				if [ "$mode" = "luci" ]; then
						for h in $hosts; do
						if [ -z "$result" ]; then
							result="`wget -q http://$h/cgi-bin/luci/freifunk/map/content -O - |grep -e '^Mid' -e '^Self' -e '^Node' -e '^PLink' -e '^Link'`"
						fi
					done
				fi

				if [ "$mode" = "latlon" ]; then
					cat $latlon_file
                                fi

				echo "$result"
				%>
			}

			function ffgoto(ip)
			{
				map.SetCenter(points[ip]);
			}
		</script>
		<div id="ffmap" style="position:relative; width:100%; height:640px;"></div>
	</body>
</html>
