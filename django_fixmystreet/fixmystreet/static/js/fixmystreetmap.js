// required : -http://openlayers.org/dev/OpenLayers.js
//              -http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.min.js

if (!('fms' in window)) {
    window.fms = {};
}

function cloneObj (obj) {
    if('create' in Object) {
        return Object.create(obj);
    } else {
        var target = {};
        for (var i in obj) {
            if (obj.hasOwnProperty(i)) {
                target[i] = obj[i];
            }
        }
        return target;
    }
}

fms.statusFilterCreated = OpenLayers.Class(OpenLayers.Control, {
    type:OpenLayers.Control.TYPE_TOGGLE,
    draw: function() {
        var self = this;
        OpenLayers.Control.prototype.draw.apply(this, arguments);

        this.div.id = "statusFilter1";
        this.div.innerHTML = "Created";
        this.div.className = "btn";
        this.div.addEventListener('click', this.trigger);

        return this.div;
    },
    trigger: function(){
        if(this.className.indexOf("active")=== -1){
            this.className += ' active';
            fms.statusFilter.push("created");
        }
        else {
            this.className = this.className.replace(/active/, '');
            var i = fms.statusFilter.indexOf("created");
            if(i != -1) {
                fms.statusFilter.splice(i, 1);
            }
        }
        fms.filterMapWithStatus();
    }
});

fms.statusFilterInProgress = OpenLayers.Class(OpenLayers.Control, {
    type:OpenLayers.Control.TYPE_TOGGLE,
    draw: function() {
        var self = this;
        OpenLayers.Control.prototype.draw.apply(this, arguments);

        this.div.id = "statusFilter2";
        this.div.innerHTML = "In progress";
        this.div.className = "btn";
        this.div.addEventListener('click', this.trigger);

        return this.div;
    },
    trigger: function(){
        if(this.className.indexOf("active")=== -1){
            this.className += ' active';
            fms.statusFilter.push("in_progress");
        }
        else {
            this.className = this.className.replace(/active/, '');
            var i = fms.statusFilter.indexOf("in_progress");
            if(i != -1) {
                fms.statusFilter.splice(i, 1);
            }
        }
        fms.filterMapWithStatus();
    }
});

fms.statusFilterClosed = OpenLayers.Class(OpenLayers.Control, {
    type:OpenLayers.Control.TYPE_TOGGLE,
    draw: function() {
        var self = this;
        OpenLayers.Control.prototype.draw.apply(this, arguments);

        this.div.id = "statusFilter3";
        this.div.innerHTML = "Closed";
        this.div.className = "btn";
        this.div.addEventListener('click', this.trigger);

        return this.div;
    },
    trigger: function(){
        if(this.className.indexOf("active")=== -1){
            this.className += ' active';
            fms.statusFilter.push("closed");
        }
        else {
            this.className = this.className.replace(/active/, '');
            var i = fms.statusFilter.indexOf("closed");
            if(i != -1) {
                fms.statusFilter.splice(i, 1);
            }
        }
        fms.filterMapWithStatus();
    }
});

fms.filterMapWithStatus = function(){
    $.ajax({
            url:"/nl/pro/ajax/map/filter/?filter="+fms.statusFilter,
            type:'GET',
            datatype:"json",
            success: function(data){
                if(fms.currentMap.markersLayer){
                    fms.currentMap.markersLayer.destroyFeatures();
                }
                var markers = [];
                for(var i=0; i< data.length; ++i){
                    markers.push(fms.currentMap.addReport(data[i], i, true));
                }
                fms.currentMap.markersLayer.addFeatures(markers);
            }
        }
        );
}

// Controller of regional layer
fms.regionalLayerShowControl = OpenLayers.Class(OpenLayers.Control, {
    type: OpenLayers.Control.TYPE_BUTTON,
    draw: function() {
        var self = this;
        OpenLayers.Control.prototype.draw.apply(this, arguments);

        this.div.id = "regionalLayerSwitcher";
        this.div.innerHTML = "reg";
        this.div.className = "btn";
        this.div.addEventListener('click', this.trigger);

        return this.div;
    },
    trigger: function(evt) {
        if (fms.regionalLayer.getVisibility()) {
            fms.regionalLayer.setVisibility(false);
            this.className = this.className.replace(/active/, '');
        } else {
            fms.regionalLayer.setVisibility(true);
            this.className += ' active';
        }
    },
    CLASS_NAME: "fms.regionalLayerShowControl"
});

// Controller of municipality limits layer
fms.MunicipalityLimitsLayerShowControl = OpenLayers.Class(OpenLayers.Control, {
    type: OpenLayers.Control.TYPE_BUTTON,
    draw: function() {
        var self = this;
        OpenLayers.Control.prototype.draw.apply(this, arguments);

        this.div.id = "municipalityLayerSwitcher";
        this.div.innerHTML = "com";
        this.div.className = "btn";
        this.div.addEventListener('click', this.trigger);

        return this.div;
    },
    trigger: function(evt) {
        if (fms.municipalityLayer.getVisibility()) {
            fms.municipalityLayer.setVisibility(false);
            this.className = this.className.replace(/active/, '');
        } else {
            fms.municipalityLayer.setVisibility(true);
            this.className += ' active';
        }
    },
    CLASS_NAME: "fms.MunicipalityLimitsLayerShowControl"
});

(function(){
        var markerWidth = 30,
            markerHeight = 40,
            defaultMarkerStyle = {
                pointRadius: markerHeight,
                externalGraphic: STATIC_URL + "images/pin-red-L.png",
                graphicXOffset: -markerWidth/2,
                graphicYOffset: -markerHeight,
                graphicHeight: markerHeight,
                graphicWidth: markerWidth
            },
            areaStyle = {
                strokeColor: "#004990",
                strokeOpacity: 1,
                strokeWidth: 2,
                fillColor: "#517EB5",
                fillOpacity: 0.6
            },
            apiRootUrl = "/api/",
            localizeUrl = "/api/locate/",
            urbisUrl = "http://geoserver.gis.irisnet.be/geoserver/wms",
            apiLang = "fr",
            showControl = true,
            markerStyle = cloneObj(defaultMarkerStyle),
            fixedMarkerStyle = cloneObj(defaultMarkerStyle),
            pendingMarkerStyle = cloneObj(defaultMarkerStyle),
            pendingExecutedMarkerStyle = cloneObj(defaultMarkerStyle),
            draggableMarkerStyle = cloneObj(defaultMarkerStyle),
            fixedMarkerStyleReg = cloneObj(defaultMarkerStyle),
            pendingMarkerStyleReg = cloneObj(defaultMarkerStyle),
            pendingExecutedMarkerStyleReg = cloneObj(defaultMarkerStyle),
            defaultMarkerStyleReg = cloneObj(defaultMarkerStyle),
            fixedMarkerStylePro = cloneObj(defaultMarkerStyle),
            pendingMarkerStylePro = cloneObj(defaultMarkerStyle),
            pendingExecutedMarkerStylePro = cloneObj(defaultMarkerStyle),
            defaultMarkerStylePro = cloneObj(defaultMarkerStyle);

        markerStyle.externalGraphic = "/static/images/pin-red-L.png";
        fixedMarkerStyle.externalGraphic = "/static/images/pin-green-L.png";
        pendingMarkerStyle.externalGraphic = "/static/images/pin-orange-L.png";
        pendingExecutedMarkerStyle.externalGraphic = "/static/images/pin-orange-executed-L.png";

        defaultMarkerStyleReg.externalGraphic = "/static/images/reg-pin-red-L.png";
        fixedMarkerStyleReg.externalGraphic = "/static/images/reg-pin-green-L.png";
        pendingMarkerStyleReg.externalGraphic = "/static/images/reg-pin-orange-L.png";
        pendingExecutedMarkerStyleReg.externalGraphic = "/static/images/reg-pin-orange-executed-L.png";

        defaultMarkerStylePro.externalGraphic = "/static/images/pro-pin-red-L.png";
        fixedMarkerStylePro.externalGraphic = "/static/images/pro-pin-green-L.png";
        pendingMarkerStylePro.externalGraphic = "/static/images/pro-pin-orange-L.png";
        pendingExecutedMarkerStylePro.externalGraphic = "/static/images/pro-pin-orange-executed-L.png";

        draggableMarkerStyle.externalGraphic = "/static/images/pin-fixmystreet-L.png";
        fms.statusFilter = [];
    /**
     * Open the map in the dom element witch id="map-bxl". If no center coordinate is provide,
     * the whole map is displayed. Must be called before each other function.
     * @param x float define the center of the map (in Lambert72 coordinate system)
     * @param y float define the center of the map (in Lambert72 coordinate system)
     */
    fms.Map = function (elementOrId, options) {
        this.options = options;

        this.element = typeof elementOrId == 'string' ? document.getElementById(elementOrId) : elementOrId;
        this.id = this.element.id;

        var x = null, y = null, self = this;
        if(this.options.origin) {
            x = this.options.origin.x;
            y = this.options.origin.y;
        }
        this.map = new OpenLayers.Map(this.id, {
            maxExtent: new OpenLayers.Bounds(16478.795,19244.928,301307.738,304073.87100000004),
//            maxResolution: 46,
            resolutions: [
                69.53831616210938, 34.76915808105469, 17.384579040527345, 8.692289520263673,
                4.346144760131836, 2.173072380065918, 1.086536190032959, 0.5432680950164795,
                0.2716340475082398, 0.1358170237541199
            ],
            units: 'm',
            projection: "EPSG:31370",
            controls: [
                new OpenLayers.Control.Navigation(
                            {dragPanOptions: {enableKinetic: true}}
                    ),
                new OpenLayers.Control.Zoom()
            ],
            numZoomLevels:9
        });

        // Regional layer
        var filter= new OpenLayers.Filter.Comparison({
            type: OpenLayers.Filter.Comparison.EQUAL_TO,
            property: 'ADMINISTRATOR',
            value: 'REG'
        });
        var xml = new OpenLayers.Format.XML();
        var filter_1_1 = new OpenLayers.Format.Filter({version: "1.1.0"});

        // Add regional limits layer
        fms.regionalLayer = new OpenLayers.Layer.WMS("regional",
            URBIS_URL + "geoserver/wms",
            {
                layers: "urbis:URB_A_SS",
                styles: "URB_A_SS_FIXMYSTREET",
                format: "image/png",
                transparent: true,
                filter: xml.write(filter_1_1.write(filter))
            },
            {
                opacity: 0.5,
                buffer: 0,
                isBaseLayer: false,
                displayInLayerSwitcher: true,
                visibility: false
            }
        );
        this.map.addLayer(fms.regionalLayer);

        var regionalLayerShow = new fms.regionalLayerShowControl();
        this.map.addControl(regionalLayerShow);
        regionalLayerShow.activate();

        // Add municipality limits layer
        fms.municipalityLayer = new OpenLayers.Layer.WMS("municipality_limits",
            URBIS_URL + "geoserver/wms",
            {layers: "urbis:URB_A_MU",
                format: "image/png",
                transparent: true},
            {buffer: 0, isBaseLayer: false, displayInLayerSwitcher: true, visibility: false}
        );
        this.map.addLayer(fms.municipalityLayer);

        var municiplaityLayerShow = new fms.MunicipalityLimitsLayerShowControl();
        this.map.addControl(municiplaityLayerShow);
        municiplaityLayerShow.activate();

        // Base layer
        var base = new OpenLayers.Layer.WMS(
            "base",
            this.options.urbisUrl,
            { layers: 'urbis' + LANGUAGE_CODE.toUpperCase() }
        );
        base.setZIndex(-100);
        this.map.addLayer(base);

        if(x && y) {
            this.map.setCenter(new OpenLayers.LonLat(x,y));
            this.map.zoomTo(6);
        } else {
            this.map.zoomToMaxExtent();
        }
    };

    fms.Map.prototype.reset = function(){
        this.map.removeLayer(this.draggableLayer);
        delete this.draggableLayer;
        this.map.removeLayer(this.markersLayer);
        delete this.markersLayer;
    };

    fms.Map.prototype.setCenter = function(x,y)
    {
        this.map.setCenter(new OpenLayers.LonLat(x,y));
        if(this.draggableMarker)
        {
            this.selectedLocation = {x:x,y:y};
            this.draggableLayer.destroyFeatures();

            this.draggableMarker = new OpenLayers.Geometry.Collection([new OpenLayers.Geometry.Point(x,y)]);
            this.draggableLayer.addFeatures([new OpenLayers.Feature.Vector(this.draggableMarker, null, draggableMarkerStyle)]);
        }
    };

    /* Center on the current draggable marker */
    fms.Map.prototype.centerOnDraggableMarker = function()
    {
        currentDraggableMarkerPoint = this.draggableMarker.components[0];
        this.map.panTo(new OpenLayers.LonLat(currentDraggableMarkerPoint.x, currentDraggableMarkerPoint.y));
    };

    fms.Map.prototype.center = function()
    {
        this.map.centerLayerContainer(new OpenLayers.LonLat(this.selectedLocation.x, this.selectedLocation.y));
    };

    fms.Map.prototype.zoomIn = function()
    {
        this.map.zoomIn();
    };

    fms.Map.prototype.zoomOut = function()
    {
        this.map.zoomOut();
    };

    /**
     * Add a draggable marker to the current map. Send a "markermoved" event to
     * the map element when the marker move.
     * @param x float define the position of the marker (in Lambert72 coordinate system)
     * @param y float define the position of the marker (in Lambert72 coordinate system)
     */
    fms.Map.prototype.addDraggableMarker = function(x,y)
    {
        var self = this;
        this.selectedLocation = {x:x,y:y};
        if(!this.draggableLayer)
        {
            this.draggableLayer = new OpenLayers.Layer.Vector( "Dragable Layer" );
            this.map.addLayer(this.draggableLayer);

            var dragControl = new OpenLayers.Control.DragFeature(this.draggableLayer,{
                onStart:function(){
                    $(self.element).trigger('markerdrag');
                },
                onComplete:function(feature,pixel){
                    var p = feature.geometry.components[0];
                    self.selectedLocation = {x:p.x,y:p.y};
                    $(self.element).trigger('markermoved', self.selectedLocation, self.draggableMarker);
                    // reverse_geocode(point);
                }
            });
            this.map.addControl(dragControl);
            //this.superControl.dragControl = dragControl;
            dragControl.activate();
        }
        this.draggableMarker = new OpenLayers.Geometry.Collection([new OpenLayers.Geometry.Point(x,y)]);
        this.dragfeature = new OpenLayers.Feature.Vector(this.draggableMarker, null, draggableMarkerStyle);
        this.draggableLayer.addFeatures([this.dragfeature]);
        if(this.selectFeature) {
            this.selectFeature.setLayer([this.markersLayer,this.draggableLayer]);
        }
    };

    fms.Map.prototype.getSelectedLocation = function()
    {
        return this.selectedLocation;
    };

    fms.Map.prototype.getSelectedAddress = function(language, callback)
    {
        var self = this;
        $.ajax({
            url: this.options.localizeUrl,
            type:'POST',
            dataType:'jsonp',
            data: {
                json: ['{',
                    '"language": "' + language + '",',
                    '"point":{x:' + this.selectedLocation.x + ',y:' + this.selectedLocation.y + '}',
                    '}'].join('\n')
            },
            success:function(response)
            {
                self.markersLayer = new OpenLayers.Layer.Vector( "Reports Layer", {strategies:[new OpenLayers.Strategy.Cluster({distance:10,threshold:2})]});
                self.map.addLayer(self.markersLayer);
                callback(language, response);
            },
            error:function()
            {
                callback(language, {
                    error:true,
                    status:"Unexpected error"
                });
            }
        });
    };

    /**
     * Add a marker to the current map, if fixed is true, the marker will be green, if not it will be red.
     * @param report the report to add
     * @param index the report index
     * @param proVersion true if the application is running the pro version
     */
    fms.Map.prototype.addReport = function(report,index,proVersion)
    {
        var self = this;
        if(!this.markersLayer)
        {
            var style = new OpenLayers.Style({
                    pointRadius: "${radius}",
                    fillColor: "#ffcc66",
                    fillOpacity: 0.8,
                    strokeColor: "#cc6633",
                    strokeWidth: "${width}",
                    strokeOpacity: 0.8,
                    label :"${count}"
                }, {
                    context: {
                        width: function(feature) {
                            return (feature.cluster) ? 2 : 1;
                        },
                        radius: function(feature) {
                            var pix = 2;
                            if(feature.cluster) {
                                pix = (feature.attributes.count/10+7);
                            }
                            return pix;
                        },
                        count: function(feature) {
                            return feature.attributes.count;
                        }
                    }
                });
            this.markersLayer = new OpenLayers.Layer.Vector( "Reports Layer", {strategies:[new OpenLayers.Strategy.Cluster({distance:50,threshold:2})],styleMap: new OpenLayers.StyleMap({
                        "default": style,
                        "select": style
                    })});
            //NEW APPROACH
            /*this.markersLayer = new OpenLayers.Layer.Markers( "zaza" );
            marker  = new OpenLayers.Marker(new OpenLayers.LonLat(report.point.x, report.point.y),
                new OpenLayers.Icon("/static/images/pin-red-XS.png",32,16).clone());
            this.markersLayer.addMarker(marker);
            marker.events.register('click',marker,function(){
                alert('ok');
            });
            this.map.addLayer(this.markersLayer);*/
            /*
            !WTF! from http://docs.openlayers.org/library/overlays.html:
            As of OpenLayers 2.7, there is no support for selecting features from more than a single vector
            layer at a time. The layer which is currently being used for selection is the last one on which
            the .activate() method of the attached select feature control was called.
            */
            /*this.markersLayer.events.on({featureselected: function(event) {alert('ok');
                // should be event.xy, but it's not available currently
                //     var pixel = control.handlers.feature.evt.xy;
                //         var location = map.getLonLatFromPixel(pixel);
                //             alert("You clicked near " + location);
                }});*/
            this.map.addLayer(this.markersLayer);

            this.selectFeature = new OpenLayers.Control.SelectFeature(this.markersLayer,{
                onSelect: function(feature){
                    if(feature.layer.name != "Dragable Layer" && !feature.cluster){
                        $.ajax({
                            type:'GET',
                            url:"/"+getCurrentLanguage()+((proVersion)?"/pro":"")+"/ajax/reportPopupDetails/",
                            data:{'report_id':feature.attributes.report.id},
                            datatype:"json",
                            success:function(data){
                                feature.attributes.report = data;
                                domElementUsedToAnchorTooltip = $(document.getElementById(feature.geometry.components[0].id));

                                var imageLink = "/static/images/no-photo-yellow-line.png";

                                if (feature.attributes.report.thumb != 'null') {
                                    imageLink = feature.attributes.report.thumb;
                                }

                                var popoverContent = '<p style="float: left;margin-right: 15px;"><img src="' + imageLink +'"/></p>' +
                                        "<p>" + feature.attributes.report.address_number + ', ' +
                                        feature.attributes.report.address + ' ' + "<br/>" +
                                        feature.attributes.report.postalcode + ' ' +
                                        feature.attributes.report.address_commune_name + "</p>" +

                                        "<p>" + feature.attributes.report.category + "</p>" +

                                        "<ul>" +
                                        "<li style='display:inline'>" + feature.attributes.report.address_regional + "</li>" +
                                        "<li style='display:inline'>" + feature.attributes.report.contractor + "</li>" +
                                        "<li style='display:inline'>" + feature.attributes.report.date_planned + "</li>";

                                // If Pro, there are priority and citizen values
                                if (feature.attributes.report.priority) {
                                    popoverContent += "<li style='display:inline'>" + feature.attributes.report.is_closed + "</li>" +
                                        "<li style='display:inline'>" + feature.attributes.report.citizen + "</li>" +
                                        "<li style='display:inline'>" + feature.attributes.report.priority + "</li>";
                                }
                                popoverContent += "</ul>";
                                popoverContent += "<p><a href='/"+getCurrentLanguage()+((proVersion)?"/pro":"")+"/report/search?report_id="+feature.attributes.report.id+"'>More details</a></p>";

                                var popup = new OpenLayers.Popup.Popover(
                                    "popup",
                                    new OpenLayers.LonLat(feature.attributes.report.point.x, feature.attributes.report.point.y),
                                    popoverContent,
                                    "#" + feature.attributes.report.id,
                                    function() { // Click close button
                                        feature.unselectAll();
                                    }
                                );

                                fms.currentMap.map.addPopup(popup);
                                fms.currentMap.map.events.register("zoomend", fms.currentMap.map, function() {
                                    console.log('destroy');
                                    this.removePopup(popup);
                                    popup.destroy();
                                });
                            }
                        });
                    }

                    if(feature.cluster){
                        if(this.map.zoom == this.map.numZoomLevels){
                            var content = "<ul>";
                            for(var i = 0; i< feature.cluster.length; i++){
                                content +="<li><a href='/"+getCurrentLanguage()+((proVersion)?"/pro":"")+"/report/search?report_id="+feature.cluster[i].data.report.id+"'>Report #"+feature.cluster[i].data.report.id+"</a></li>";
                            }
                            var popup = new OpenLayers.Popup.Popover(
                                    "popup",
                                    new OpenLayers.LonLat(feature.geometry.x, feature.geometry.y),
                                    content,
                                    "Reports at this location:"
                                );
                            fms.currentMap.map.addPopup(popup);
                            fms.currentMap.map.events.register("zoomend", fms.currentMap.map, function() {
                                console.log('destroy');
                                this.removePopup(popup);
                                popup.destroy();
                            });
                        }
                        else{
                            this.map.setCenter(feature.geometry.getBounds().getCenterLonLat());
                            this.map.zoomIn();
                        }
                    }
                },
                onUnselect: function(feature){
                    for(var i=0, length=this.map.popups.length; i < length; i++) {
                        var popup = this.map.popups[i];
                        this.map.removePopup(popup);
                        popup.destroy();
                    }
                }
            });

            this.map.addControl(this.selectFeature);
            this.selectFeature.activate();

        }
        var markerPoint = new OpenLayers.Geometry.Point(report.point.x,report.point.y);
        var newMarker = new OpenLayers.Geometry.Collection([markerPoint]);

        //Can be either orange, red or green and in the set of regional route or not.
        var markerConf;

        if (proVersion) {
            if (!report.address_regional) {
                //NOT ROUTE REGIONALE
                if (report.citizen == 'true') {
                    markerConf = (report.status == 3 || report.status == 9) ? fixedMarkerStyle : report.status == 1 ? defaultMarkerStyle : (report.status==5 || report.status ==6) ? pendingExecutedMarkerStyle : pendingMarkerStyle;
                } else {
                   markerConf = (report.status == 3 ||report.status == 9) ? fixedMarkerStylePro : report.status == 1 ? defaultMarkerStylePro : (report.status==5 || report.status ==6) ? pendingExecutedMarkerStylePro : pendingMarkerStylePro;
                }
            } else {
               //ROUTE REGIONALE
               markerConf = (report.status == 3 || report.status == 9) ? fixedMarkerStyleReg : report.status == 1 ? defaultMarkerStyleReg : (report.status==5 || report.status ==6) ? pendingExecutedMarkerStyleReg :pendingMarkerStyleReg;
            }
                return new OpenLayers.Feature.Vector(newMarker, {'report':report}, markerConf);
                // self.markersLayer.addFeatures(vectorOfMarkers);
        } else {
            //Non pro version
            if (report.citizen == 'true') {
                markerConf = (report.status == 3 || report.status == 9) ? fixedMarkerStyle : report.status == 1 ? defaultMarkerStyle : pendingMarkerStyle;
            } else {
                markerConf = (report.status == 3 || report.status == 9) ? fixedMarkerStylePro : report.status == 1 ? defaultMarkerStylePro : pendingMarkerStylePro;
            }
            var vectorOfMarkers = new OpenLayers.Feature.Vector(newMarker, {'report':report}, markerConf);
            return vectorOfMarkers;
            // self.markersLayer.addFeatures(vectorOfMarkers);
        }
    };

    /**
     * Add a simple indiocator to the current map.
     * @param pnt object define the x, y position of the marker (in Lambert72 coordinate system)
     */
    fms.Map.prototype.addIndicator = function(pnt)
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
    };

    /**
     * Add a shape to the current map.
     * @param geometry a standart shape json object.
     */
    fms.Map.prototype.highlightArea = function(featureId)
    {
        //municipalities layer
        var municipalities = new OpenLayers.Layer.WMS(
            "Municipalities",
            this.options.urbisUrl,
            {layers: 'urbis:URB_A_MU', styles: 'fixms_municipalities', transparent: 'true', featureId: featureId},
            {singleTile: true, ratio: 1.25, isBaseLayer: false}
        );
        this.map.addLayer(municipalities);
    };

    /**
     * Private function, add a polygon to the current map
     */
    fms.Map.prototype._addPolygon = function(polygon,layer){
        for(var j in polygon){
            var area = polygon[j];
            var points = [];
            for(var i in area){
                var p = area[i];
                points.push(new OpenLayers.Geometry.Point(p[0],p[1]));
            }

            var ring = new OpenLayers.Geometry.LinearRing(points);
            var featurePolygon = new OpenLayers.Feature.Vector(ring, null, areaStyle);
            layer.addFeatures(featurePolygon);
        }
    };


}());

