// required : -http://openlayers.org/dev/OpenLayers.js
//			  -http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.min.js

(function(){
	var markerWidth = 18,
		markerHeight = 34,
		defaultMarkerStyle = {
			pointRadius:markerHeight,
			externalGraphic:"/static/images/marker.png",
			graphicXOffset:-markerWidth/2,
			graphicYOffset:-markerHeight,
			graphicHeight:markerHeight,
			graphicWidth:markerWidth
		}
		areaStyle = {
			strokeColor: "#004990",
			strokeOpacity: 1,
			strokeWidth: 2,
			fillColor: "#517EB5",
			fillOpacity: 0.6
		};
	
	$.widget("ui.fmsMap", {
		options:{
			apiRootUrl: "/api/",
			localizeUrl: "/api/locate/",
			urbisUrl: "http://geoserver.gis.irisnetlab.be/geoserver/wms",
			apiLang: "fr",
            showControl: true,
			markerStyle: $.extend({},defaultMarkerStyle,{
				externalGraphic: "/static/images/marker.png",
				graphicXOffset: -32/2,
				graphicYOffset: -32,
				graphicHeight: 32,
				graphicWidth: 32
			}),
			fixedMarkerStyle: $.extend({},defaultMarkerStyle,{
				externalGraphic:"/static/images/marker-fixed.png"
			}),
			pendingMarkerStyle: $.extend({},defaultMarkerStyle,{
				externalGraphic:"/static/images/marker-pending.png",
			})
		},
		/**
		 * Open the map in the dom element witch id="map-bxl". If no center coordinate is provide,
		 * the whole map is displayed. Must be called before each other function.
		 * @param x float define the center of the map (in Lambert72 coordinate system)
		 * @param y float define the center of the map (in Lambert72 coordinate system)
		 */
		_init: function()
		{
                        var x = null, y = null, self = this;
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
			this.map.events.on({
				movestart:function(){
					self.element.trigger('movestart');
				},
				zoomend:function(){
					self.element.trigger('zoomend');
				}
			});

			var wms = new OpenLayers.Layer.WMS(
				"Bruxelles",
				this.options.urbisUrl,
				{ layers: 'urbisFR' } // urbisFRshp,urbisFR
				
			);
			this.map.addLayer(wms);
			
			if(x && y)
			{
				this.map.setCenter(new OpenLayers.LonLat(x,y));
		        	this.map.zoomTo(6);
			}
		},

        reset: function(){
            this.map.removeLayer(this.draggableLayer);
            delete this.draggableLayer;
            this.map.removeLayer(this.markersLayer);
            delete this.markersLayer;
        },
	
		setCenter: function(x,y)
		{
			this.map.setCenter(new OpenLayers.LonLat(x,y));
			if(this.draggableMarker)
			{
				this.selectedLocation = {x:x,y:y};
				this.draggableLayer.destroyFeatures();
				
				this.draggableMarker = new OpenLayers.Geometry.Collection([new OpenLayers.Geometry.Point(x,y)]);
				this.draggableLayer.addFeatures([new OpenLayers.Feature.Vector(this.draggableMarker, null, this.options.markerStyle)]);
			}
		},

		center: function()
		{
			this.map.centerLayerContainer(new OpenLayers.LonLat(this.selectedLocation.x, this.selectedLocation.y));
		},

		zoomIn: function()
		{
			this.map.zoomIn();
		},

		zoomOut: function()
		{
			this.map.zoomOut();
		},
	
		/**
		 * Add a draggable marker to the current map. Send a "markermoved" event to
		 * the map element when the marker move.
		 * @param x float define the position of the marker (in Lambert72 coordinate system)
		 * @param y float define the position of the marker (in Lambert72 coordinate system)
		 */
		addDraggableMarker: function(x,y)
		{
			var self = this;
			this.selectedLocation = {x:x,y:y};
			if(!this.draggableLayer)
			{
				this.draggableLayer = new OpenLayers.Layer.Vector( "Dragable Layer" );
				this.map.addLayer(this.draggableLayer);
		
				var dragControl = new OpenLayers.Control.DragFeature(this.draggableLayer,{
					onStart:function(){
						self.element.trigger('markerdrag');
					},
					onComplete:function(feature,pixel){
						var p = feature.geometry.components[0];
						self.selectedLocation = {x:p.x,y:p.y};
						self.element.trigger('markermoved', self.selectedLocation, self.draggableMarker);
						// reverse_geocode(point);
					}
				});
				this.map.addControl(dragControl);
				//this.superControl.dragControl = dragControl;
				dragControl.activate();
			}
			this.draggableMarker = new OpenLayers.Geometry.Collection([new OpenLayers.Geometry.Point(x,y)]);
			
			this.draggableLayer.addFeatures([new OpenLayers.Feature.Vector(this.draggableMarker, null, this.options.markerStyle)]);
		},

		getSelectedLocation: function()
		{
			return this.selectedLocation;
		},
		
		getSelectedAddress: function(callback)
		{
			$.ajax({
				url: this.options.localizeUrl,
				type:'POST',
				dataType:'jsonp',
				data:{json: '{\
					"language": "' + this.options.apiLang + '",\
					"point":{x:' + this.selectedLocation.x + ',y:' + this.selectedLocation.y + '}\
				}'},
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
		addReport: function(report,index)
		{
			var self = this;
			if(!this.markersLayer)
			{
				this.markersLayer = new OpenLayers.Layer.Vector( "Reports Layer" );
				this.map.addLayer(this.markersLayer);


				/*
				!WTF! from http://docs.openlayers.org/library/overlays.html:
				As of OpenLayers 2.7, there is no support for selecting features from more than a single vector
				layer at a time. The layer which is currently being used for selection is the last one on which
				the .activate() method of the attached select feature control was called.
				*/
				
				var selectFeature = new OpenLayers.Control.SelectFeature(this.markersLayer,{
					onSelect:function(feature,pixel){
						var p = feature.geometry.components[0];
						var point = {x:p.x,y:p.y};
						//console.log(point,feature.attributes.report);
						self.element.trigger('reportselected', [point, feature.attributes.report]);
					}
				});
				this.map.addControl(selectFeature);
				
				selectFeature.activate();
				
				/*
				this.superControl.selectControl = selectFeature;
				
				var events = new OpenLayers.Events(this.markersLayer, this.element[0], ['click']);
				events.on({
					'click':function(){
						console.log('click');
					}
				});
				this.element.click(function(evt){
					console.log('wow');
					
				});
				this.element.delegate('image', 'click', function(evt){
					console.log('image',this);
				});
				*/
			}
			
			var newMarker = new OpenLayers.Geometry.Collection([new OpenLayers.Geometry.Point(report.point.x,report.point.y)]);
			
			var markerConf = report.is_fixed ? this.options.fixedMarkerStyle : this.options.pendingMarkerStyle;
			if(index){
				//make a copy
				markerConf = $.extend({},markerConf,{
					externalGraphic:'/static/images/marker/' + (report.is_fixed?'green':'red') + '/marker' + index + '.png'
				});
			}
			this.markersLayer.addFeatures([new OpenLayers.Feature.Vector(newMarker, {'report':report}, markerConf)]);

			/*
			console.log(newMarker);
			var events = new OpenLayers.Events(newMarker, this.element[0], ['click']);
			events.on({
				'click':function()
				{
					console.log('click');
				}
			});
			*/
			
			// http://openlayers.org/dev/examples/dynamic-text-layer.html
            //function onFeatureSelect(evt) {
                //feature = evt.feature;
                //popup = new OpenLayers.Popup.FramedCloud("featurePopup",
					//feature.geometry.getBounds().getCenterLonLat(),
					//new OpenLayers.Size(100,100),
					//"<h2>"+feature.attributes.title + "</h2>" +
					//feature.attributes.description,
					//null, true, onPopupClose);
                //feature.popup = popup;
                //popup.feature = feature;
                //map.addPopup(popup, true);
            //}
            //function onFeatureUnselect(evt) {
                //feature = evt.feature;
                //if (feature.popup) {
                    //popup.feature = null;
                    //map.removePopup(feature.popup);
                    //feature.popup.destroy();
                    //feature.popup = null;
                //}
            //}
		},

		/**
		 * Add a simple indiocator to the current map.
		 * @param pnt object define the x, y position of the marker (in Lambert72 coordinate system)
		 */
		addIndicator: function(pnt)
		{
			var self = this;
			if(!this.indicatorsLayer)
			{
				this.indicatorsLayer = new OpenLayers.Layer.Vector( "Indicators Layer" );
				this.map.addLayer(this.indicatorsLayer);
			}
			
			var newMarker = new OpenLayers.Geometry.Collection([new OpenLayers.Geometry.Point(pnt.x, pnt.y)]);
			
			var markerConf = this.options.markerStyle;
			this.indicatorsLayer.addFeatures([new OpenLayers.Feature.Vector(newMarker, {}, markerConf)]);
		},

		/**
		 * Add a shape to the current map.
		 * @param geometry a standart shape json object.
		 */
		highlightArea: function(featureId)
		{
            //municipalities layer
            var municipalities = new OpenLayers.Layer.WMS(
                "Municipalities",
                this.options.urbisUrl,
                {layers: 'urbis:URB_A_MU', styles: 'fixms_municipalities', transparent: 'true', featureId: featureId},
                {singleTile: true, ratio: 1.25, isBaseLayer: false}
            );
            this.map.addLayer(municipalities);
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

