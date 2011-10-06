// required : -http://openlayers.org/dev/OpenLayers.js
//			  -http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.min.js

(function(){
	var urbisURL = "http://geoserver.gis.irisnet.be/geoserver/",
		markerWidth = 18,
		markerHeight = 34,
		markersLayer = null,
		draggableLayer = null,
		markerStyle = {
			pointRadius:markerHeight,
			externalGraphic:"/media/images/marker.png",
			graphicXOffset:-markerWidth/2,
			graphicYOffset:-markerHeight,
			graphicHeight:markerHeight,
			graphicWidth:markerWidth
			
		},
		fixedMarkerStyle = $.extend({},markerStyle,{
			externalGraphic:"/media/images/marker-fixed.png"
		}),
		pendingMarkerStyle = $.extend({},markerStyle,{
			externalGraphic:"/media/images/marker-pending.png",
		}),
		areaStyle = {
			strokeColor: "#004990",
			strokeOpacity: 1,
			strokeWidth: 2,
			fillColor: "#517EB5",
			fillOpacity: 0.6
		};
	
	$.widget("ui.fmsMap", {
		/**
		 * Open the map in the dom element witch id="map-bxl". If no center coordinate is provide,
		 * the whole map is displayed. Must be called before each other function.
		 * @param x float define the center of the map (in Lambert72 coordinate system)
		 * @param y float define the center of the map (in Lambert72 coordinate system)
		 */
		_init: function()
		{
			var x = null, y = null;
			if(this.options.origin)
			{
				x = this.options.origin.x;
				y = this.options.origin.y;
			}
			this.map = new OpenLayers.Map(this.element[0].id,{
				maxExtent: new OpenLayers.Bounds(133736.38890635, 160293.01359269, 167103.47196451, 182838.33998333),
				maxResolution:46,
				units: 'm',
				projection: "EPSG:31370"
			});
			var wms = new OpenLayers.Layer.WMS(
				"Bruxelles",
				urbisURL + "wms?",
				{ layers: 'urbisFR' } // urbisFRshp,urbisFR
				
			);
			this.map.addLayer(wms);
			
			if(x && y)
			{
				this.map.zoomTo(6);
				this.map.setCenter(new OpenLayers.LonLat(x,y));
			}
			else
			{
				this.map.zoomToMaxExtent();
			}
		},
	
	
		/**
		 * Add a draggable marker to the current map. Send a "markermoved" event to
		 * the map element when the marker move.
		 * @param x float define the position of the marker (in Lambert72 coordinate system)
		 * @param y float define the position of the marker (in Lambert72 coordinate system)
		 */
		addDraggableMarker: function(x,y)
		{
			this.selectedLocation = {x:x,y:y};
			if(!draggableLayer)
			{
				draggableLayer = new OpenLayers.Layer.Vector( "Vector Layer" );
				this.map.addLayer(draggableLayer);
		
				var dragControl = new OpenLayers.Control.DragFeature(draggableLayer,{
					onComplete:function(feature,pixel){
						var p = feature.geometry.components[0];
						this.selectedLocation = {x:p.x,y:p.y};
						$("#map-bxl").trigger('markermoved',this.selectedLocation,marker);
						// reverse_geocode(point);
					}
				});
				this.map.addControl(dragControl);
				dragControl.activate();
			}
			var marker = new OpenLayers.Geometry.Collection([new OpenLayers.Geometry.Point(x,y)]);
			
			draggableLayer.addFeatures([new OpenLayers.Feature.Vector(marker, null, markerStyle)]);
		},

		getSelectedLocation: function()
		{
			return this.selectedLocation;
		},
		getSelectedAddress: function(callback)
		{
			$('#id_address').addClass('loading');
			$.ajax({
				url:'/api/address/',
				type:'POST',
				contentType:'json',
				dataType:'json',
				data:JSON.stringify({
					"language": "fr",
					"point": this.selectedLocation
				}),
				success:function(response)
				{
					callback(response);
				},
				error:function()
				{
					callback({
						error:true,
						status:"Unexpected error"
					});
				}
			});
		},

		/**
		 * Add a marker to the current map, if fixed is true, the marker will be green, if not it will be red.
		 * @param x float define the position of the marker (in Lambert72 coordinate system)
		 * @param y float define the position of the marker (in Lambert72 coordinate system)
		 * @param fixed string define the style of the marker
		 */
		addMarker: function(x,y,fixed)
		{
			if(!markersLayer)
			{
				markersLayer = new OpenLayers.Layer.Vector( "Vector Layer" );
				this.map.addLayer(markersLayer);
			}
			
			var newMarker = new OpenLayers.Geometry.Collection([new OpenLayers.Geometry.Point(x,y)]);
			
			markersLayer.addFeatures([new OpenLayers.Feature.Vector(newMarker, null, fixed ? fixedMarkerStyle : pendingMarkerStyle)]);
		},
	
		/**
		 * Add a shape to the current map.
		 * @param geometry a standart shape json object.
		 */
		highlightArea: function(geometry)
		{
			var vectorLayer = new OpenLayers.Layer.Vector("Vector Layer");
			this.map.addLayer(vectorLayer);
			this.map.setLayerIndex(vectorLayer,0);

			if(geometry.type == 'Polygon'){
				this._addPolygon(geometry.coordinates,vectorLayer);
			}
			else if(geometry.type == 'MultiPolygon')
			{
				for(var i in geometry.coordinates){
					this._addPolygon(geometry.coordinates[i],vectorLayer);
				}
			}
		},
		
		/**
		 * Private function, add a polygon to the current map
		 */
		_addPolygon: function(polygon,layer){
			for(var j in polygon){
				var area = polygon[j];
				var points = [];
				for(var i in area){
					var p = area[i];
					points.push(new OpenLayers.Geometry.Point(p[0],p[1]));
				}
			
				var ring = new OpenLayers.Geometry.LinearRing(points);
				var polygon = new OpenLayers.Feature.Vector(ring,null,areaStyle);
				layer.addFeatures(polygon);
			}
		}
	});
}());

