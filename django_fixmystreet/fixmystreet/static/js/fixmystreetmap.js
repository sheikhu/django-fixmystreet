// required : -http://openlayers.org/dev/OpenLayers.js
//              -http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.min.js

if (!('fms' in window)) {
    window.fms = {};
    //A local cache to avoid multiple calls to backend system when clicking on filters
    window.fms.cachedElements = false;
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

fms.filterMapWithStatus = function(callback){ 
    if (fms.cachedElements === false) {  
        $.ajax({
            url:"/"+LANGUAGE_CODE+"/ajax/map/filter/",
            type:'GET',
            datatype:"json",
            success: function(data){
                if (fms.currentMap.markersLayer) {
                    fms.currentMap.markersLayer.destroyFeatures();
                }
                fms.currentMap.addReportCollection(data);
                fms.cachedElements = true;
            },
            error: function(data) {
                if(fms.currentMap.markersLayer){
                    fms.currentMap.markersLayer.destroyFeatures();
                }
            },
            complete: function() {
                if (callback) {
                    callback();
                }
            }
        });
    } else {
        fms.currentMap.markersLayer.redraw(true);

        //As recalculate does not exists in openlayers 2.12
        //fms.currentMap.strategy.distance=fms.currentMap.strategy.distance===50?49:50;
        //fms.currentMap.strategy.layer.redraw(true);
        //fms.currentMap.strategy.recluster();
        callback();
    }
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
            createdMarkerStyle = cloneObj(defaultMarkerStyle),
            fixedMarkerStyle = cloneObj(defaultMarkerStyle),
            pendingMarkerStyle = cloneObj(defaultMarkerStyle),
            draggableMarkerStyle = cloneObj(defaultMarkerStyle);

        createdMarkerStyle.externalGraphic = "/static/images/pin-red-L.png";
        createdMarkerStyle.display = "";

        fixedMarkerStyle.externalGraphic = "/static/images/pin-green-L.png";
        fixedMarkerStyle.display = "";

        pendingMarkerStyle.externalGraphic = "/static/images/pin-orange-L.png";
        pendingMarkerStyle.display = "";

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

        //Center Button
        var centerMapButton = new OpenLayers.Control.Button({
            displayClass: 'olControlBtnCenterOnCursor',
            id: 'btnCenterOnCursor',
            trigger: function() {fms.currentMap.centerOnDraggableMarker()}
        });
        //centerMapButton.panel_div.innerHTML = "zaza";
        //Center Panel
        var centerPanel = new OpenLayers.Control.Panel(
            {
                defaultControl: centerMapButton
            }
        )

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
                new OpenLayers.Control.Zoom(),
                //Center button
                centerPanel
            ],
            numZoomLevels:9
        });

        centerPanel.addControls([centerMapButton]);
        this.centerPanel = centerPanel;


        //Filter flags
        this.flagCreated = true;
        this.flagInProgress = true;
        this.flagClosed = true;

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

        // Add municipality limits layer
        fms.municipalityLayer = new OpenLayers.Layer.WMS("municipality_limits",
            URBIS_URL + "geoserver/wms",
            {layers: "urbis:URB_A_MU",
                format: "image/png",
                styles: "fixmystreet_municipalities",
                transparent: true},
            {buffer: 0, isBaseLayer: false, displayInLayerSwitcher: true, visibility: false}
        );
        this.map.addLayer(fms.municipalityLayer);

        // Base layer
        var base = new OpenLayers.Layer.WMS(
            "base",
            this.options.urbisUrl,
            {layers: 'urbis' + LANGUAGE_CODE.toUpperCase()},
            {displayInLayerSwitcher: false}
        );
        base.setZIndex(-100);
        this.map.addLayer(base);

        if(x && y) {
            this.map.setCenter(new OpenLayers.LonLat(x,y));
            this.map.zoomTo(6);
        } else {
            this.map.setCenter(new OpenLayers.LonLat(148894,170714));
            this.map.zoomTo(3);
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

    /* Method to toogle created filter element */
    fms.Map.prototype.toogleCreated = function()
    {
        fms.currentMap.flagCreated = !fms.currentMap.flagCreated;

        for (cptRules in fms.currentMap.markersLayer.styleMap.styles.default.rules) {
            if (fms.currentMap.markersLayer.styleMap.styles.default.rules[cptRules].name === 'rule-created') {
                fms.currentMap.markersLayer.styleMap.styles.default.rules[cptRules].symbolizer.display = (fms.currentMap.flagCreated === true?"":"none");
            }
        }

        fms.Map.prototype.refreshCluster();
    };
    /* Method to toogle in progress filter element */
    fms.Map.prototype.toogleInProgress = function()
    {
        fms.currentMap.flagInProgress = !fms.currentMap.flagInProgress;

        for (cptRules in fms.currentMap.markersLayer.styleMap.styles.default.rules) {
            if (fms.currentMap.markersLayer.styleMap.styles.default.rules[cptRules].name === 'rule-in-progress') {
                fms.currentMap.markersLayer.styleMap.styles.default.rules[cptRules].symbolizer.display = (fms.currentMap.flagInProgress === true?"":"none");
            }
        }

        fms.Map.prototype.refreshCluster();
    };
    /* Method to toogle closed filter element */
    fms.Map.prototype.toogleClosed = function()
    {
        fms.currentMap.flagClosed = !fms.currentMap.flagClosed;

        for (cptRules in fms.currentMap.markersLayer.styleMap.styles.default.rules) {
            if (fms.currentMap.markersLayer.styleMap.styles.default.rules[cptRules].name === 'rule-processed') {
                fms.currentMap.markersLayer.styleMap.styles.default.rules[cptRules].symbolizer.display = (fms.currentMap.flagClosed === true?"":"none");
            }
        }

        fms.Map.prototype.refreshCluster();
    };
    /* Method to refresh the cluster content */
    fms.Map.prototype.refreshCluster = function()
    {
        fms.currentMap.strategy.features = [];
        
        for (featureIndex in fms.currentMap.features) {
            var rulesTestValue = false;
            RULES: for (currentRuleIndex in fms.currentMap.markersLayer.styleMap.styles.default.rules) {if (featureIndex === 1) debugger;
                if (fms.currentMap.markersLayer.styleMap.styles.default.rules[currentRuleIndex].evaluate(fms.currentMap.features[featureIndex])) {
                    fms.currentMap.strategy.features[fms.currentMap.strategy.features.length] = fms.currentMap.features[featureIndex];
                    break RULES;
                }
            }
        }
        fms.currentMap.strategy.layer.removeAllFeatures();
        fms.currentMap.strategy.layer.redraw(true);
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

        // If one draggableLayer already exists, remove it
        if(this.draggableLayer)
        {
            this.map.removeLayer(this.draggableLayer);
            delete this.draggableLayer;
        }

        this.draggableLayer = new OpenLayers.Layer.Vector( "Dragable Layer", {displayInLayerSwitcher: false} );
        this.map.addLayer(this.draggableLayer);

        var dragControl = new OpenLayers.Control.DragFeature(this.draggableLayer,{
            onStart:function(){
                //Not used.
                //$(self.element).trigger('markerdrag');
                // Remove all popups
                while(this.map.popups.length) {
                     this.map.removePopup(this.map.popups[0]);
                }
            },
            onComplete:function(feature,pixel){
                var p = feature.geometry.components[0];
                self.selectedLocation = {x:p.x,y:p.y};
                $(self.element).trigger('markermoved', self.selectedLocation, self.draggableMarker);
                // reverse_geocode(point);
            },
            onDrag:function(event){
                //~ var markerBounds = event.geometry.bounds;
                //~ var mapBounds = this.map.getExtent();
                //~ var delta = 100;
                //~ if(mapBounds.left+delta > markerBounds.left) {
                    //~ this.map.pan(-100,0,{});
                //~ }
                //~ else if (mapBounds.right-delta < markerBounds.right){
                    //~ this.map.pan(100,0,{});
                //~ }
                //~ else if (mapBounds.top-delta < markerBounds.top){
                    //~ this.map.pan(0,-100,{});
                //~ }
                //~ else if(mapBounds.bottom + delta > markerBounds.bottom){
                    //~ this.map.pan(0,100,{});
                //~ }
            }
        });

        this.map.addControl(dragControl);
        dragControl.activate();

        this.draggableMarker = new OpenLayers.Geometry.Collection([new OpenLayers.Geometry.Point(x,y)]);
        this.dragfeature = new OpenLayers.Feature.Vector(this.draggableMarker, null, draggableMarkerStyle);
        this.draggableLayer.addFeatures([this.dragfeature]);
        if(this.selectFeature) {
            this.selectFeature.setLayer([this.markersLayer,this.draggableLayer]);
        }

        //Allow button center on draggable marker when visible
        this.centerPanel.controls[0].activate();
        //Update size of all layers as when updating main map component size, sometimes openlayers keeps old values
        this.map.updateSize();

        return this.draggableMarker;
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
                self.markersLayer = new OpenLayers.Layer.Vector( "Reports Layer",
                    {
                        strategies:[new OpenLayers.Strategy.Cluster({
                            distance:10,
                            threshold:2
                        })],
                        displayInLayerSwitcher: false
                    }
                );
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
     */
    fms.Map.prototype.addReportCollection = function(reports)
    {
        for (filterCpt in reports) {
            this.addReport(reports[filterCpt], filterCpt, false);
        }
        this.markersLayer.addFeatures(this.features);
    }
    /**
     * Add a marker to the current map, if fixed is true, the marker will be green, if not it will be red.
     * @param report the report to add
     * @param index the report index
     * @param proVersion true if the application is running the pro version
     */
    fms.Map.prototype.addReport = function(report,index,proVersion,isIconsOnly)
    {
        var self = this;
        if(!this.markersLayer)
        {
            var clusterStyle = new OpenLayers.Style({
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
            var markerStyle = new OpenLayers.Style({}, {
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
                    },
                    rules: [
                        //IN PROGRESS
                        new OpenLayers.Rule({
                            name: "rule-in-progress",
                            filter: new OpenLayers.Filter({
                                evaluate: function (context) {
                                    if (fms.currentMap.flagInProgress === false) return false;
                                    var returnValue = context.report /*&& window.fms.currentMap.flagClosed === true*/ && [2, 4, 5, 6, 7].indexOf(context.report.status) >= 0;                                  
                                    /*if (typeof context.report !== 'undefined')
                                        context.report.display = (returnValue === true?"":"none");*/
                                    return returnValue;
                                }
                            }),
                            symbolizer: pendingMarkerStyle,
                            elseFilter: true
                        }),
                        //CREATED
                        new OpenLayers.Rule({
                            name: "rule-created",
                            filter: new OpenLayers.Filter({
                                evaluate: function (context) {  
                                    if (fms.currentMap.flagCreated === false) return false; 
                                    var returnValue = context.report /*&& window.fms.currentMap.flagClosed === true*/ && context.report.status === 1;
                                    /*if (typeof context.report !== 'undefined')
                                        context.report.display = (returnValue === true?"":"none");*/
                                    return returnValue;
                                }
                            }),
                            symbolizer: createdMarkerStyle,
                            elseFilter: true
                        }),
                        //PROCESSED
                        new OpenLayers.Rule({
                            name: "rule-processed",
                            filter: new OpenLayers.Filter({
                                evaluate: function (context) {
                                    if (fms.currentMap.flagClosed === false) return false;
                                    var returnValue = context.report /*&& window.fms.currentMap.flagClosed === true*/ && [3, 8].indexOf(context.report.status) >= 0;
                                    /*if (typeof context.report !== 'undefined')
                                        context.report.display = (returnValue === true?"":"none");*/
                                    return returnValue;
                                }
                            }),
                            symbolizer: fixedMarkerStyle,
                            elseFilter: true
                        }),
                        //CLUSTER
                        new OpenLayers.Rule({
                            name: "rule-cluster",
                            filter: new OpenLayers.Filter({
                                evaluate: function (context) {
                                    return context.count;
                                }
                            }),
                            symbolizer: {
                                pointRadius: "${radius}",
                                fillColor: "#ffcc66",
                                fillOpacity: 0.8,
                                strokeColor: "#cc6633",
                                strokeWidth: "${width}",
                                strokeOpacity: 0.8,
                                label :"${count}"
                            },
                            elseFilter: true
                        })
                    ]
                });
            self.strategy = new OpenLayers.Strategy.Cluster({
                distance:50,
                threshold:2,
                clustering:false,
                rules:markerStyle.rules
            });

            this.markersLayer = new OpenLayers.Layer.Vector("Reports Layer",
                {
                    strategies: [self.strategy],
                    styleMap: new OpenLayers.StyleMap({
                            "default": markerStyle,
                            "select": markerStyle
                    }),
                    displayInLayerSwitcher: false
                }
            );
            this.map.addLayer(this.markersLayer);

            var self = this;
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
                                domElementUsedToAnchorTooltip = $(document.getElementById(feature.geometry/*.components[0]*/.id));

                                var imageLink = "/static/images/no-pix.png";

                                if (feature.attributes.report.thumb != 'null') {
                                    imageLink = feature.attributes.report.thumb;
                                }

                                // Set content of popover
                                var popoverTitle   = "";
                                var popoverContent = "";
                                var popoverIcons   = "";
                                var popoverSize    = new OpenLayers.Size(200,50);

                                if (!isIconsOnly) {
                                    popoverSize  = new OpenLayers.Size(400,220);
                                    popoverTitle = "<h2>Incident #" + feature.attributes.report.id + " </h2>";

                                    popoverContent = '<div class="details-popup"><p style="float: right;margin-left: 15px;"><img class="thumbnail" src="' + imageLink +'"/></p>' +
                                        "<a class='moreDetails' style='clear:both; float: right;margin-left: 15px;' href='/"+getCurrentLanguage()+((proVersion)?"/pro":"")+"/report/search?report_id="+feature.attributes.report.id+"'>Details</a>" +
                                        "<strong class='popup_adress'>" + feature.attributes.report.address_number + ', ' +
                                        feature.attributes.report.address + ' ' + "<br/>" +
                                        feature.attributes.report.postalcode + ' ' +
                                        feature.attributes.report.address_commune_name + "</strong>" +


                                        "<p class='categoryPopup'>" + feature.attributes.report.category + "</p></div>          ";
                                }

                                var popoverIcons = "<ul class='iconsPopup'>";
                                        //"<li class='addressRegional'>" + feature.attributes.report.address_regional + "</li>";

                                if (feature.attributes.report.address_regional != 'null'){
                                    popoverIcons += "<li class='addressRegional' data-placement='bottom' data-toggle='tooltip' data-original-title='This incident is located on a regional zone'><img src='/static/images/addressRegional.png' /></li>";
                                }

                                if (feature.attributes.report.contractor != 'null'){
                                    popoverIcons += "<li class='contractorAssigned'><img src='/static/images/contractorAssigned.png' /></li>";
                                }

                                if (feature.attributes.report.date_planned){
                                    popoverIcons += "<li class='datePlanned'>" + feature.attributes.report.date_planned + "</li>";
                                }

                                // If Pro, there are priority and citizen values
                                if (feature.attributes.report.priority) {
                                    if (feature.attributes.report.is_closed != 'null'){
                                        popoverIcons += "<li class='isClosed'><img src='/static/images/isClosed.png' /></li>";
                                    }
                                    if (feature.attributes.report.citizen != 'null'){
                                        popoverIcons += "<li class='fromPro'><img src='/static/images/fromPro.png' /></li>";
                                    }
                                    if (feature.attributes.report.priority <= '2'){
                                        popoverIcons += "<li class='priority'><img src='/static/images/lowPriority.png' />" + feature.attributes.report.priority + "</li>";
                                    }
                                    else if (feature.attributes.report.priority <= '6'){
                                        popoverIcons += "<li class='priority'><img src='/static/images/mediumPriority.png' />" + feature.attributes.report.priority + "</li>";
                                    }
                                    else {
                                        popoverIcons += "<li class='priority'><img src='/static/images/highPriority.png' />" + feature.attributes.report.priority + "</li>";
                                    }
                                    //popoverIcons += "<li>" + feature.attributes.report.is_closed + "</li>" +
                                    //popoverIcons += "<li>" + feature.attributes.report.citizen + "</li>" +
                                    //popoverIcons += "<li>" + feature.attributes.report.priority + "</li>";
                                }
                                popoverIcons += "</ul>";

                                var popup = new OpenLayers.Popup(
                                    "popup",
                                    new OpenLayers.LonLat(feature.attributes.report.point.x, feature.attributes.report.point.y),
                                    popoverSize,
                                    '<div class="in-popup">' + popoverTitle + popoverContent + popoverIcons + '</div>',
                                    true,
                                    function closeMe() {
                                        self.selectFeature.onUnselect(feature);
                                    }
                                );
                                
                                popup.div.className = 'reports';
                                popup.panMapIfOutOfView = true;

                                fms.currentMap.map.addPopup(popup);
                                fms.currentMap.map.events.register("zoomend", null, function() {
                                    self.selectFeature.onUnselect(feature);
                                });
                            }
                        });
                    }

                    if(feature.cluster){
                        if(this.map.zoom == this.map.numZoomLevels){
                            var content = "<h2>Reports at this location:</h2><ul>";
                            for(var i = 0; i< feature.cluster.length; i++){
                                content +="<li><a href='/"+getCurrentLanguage()+((proVersion)?"/pro":"")+"/report/search?report_id="+feature.cluster[i].data.report.id+"'>Report #"+feature.cluster[i].data.report.id+"</a></li>";
                            }
                            var popup = new OpenLayers.Popup(
                                "popup",
                                new OpenLayers.LonLat(feature.geometry.x, feature.geometry.y),
                                new OpenLayers.Size(400,220),
                                content,
                                true,
                                function closeMe() {
                                    self.selectFeature.onUnselect(feature);
                                }
                            );
                            popup.panMapIfOutOfView = true;

                            fms.currentMap.map.addPopup(popup);
                            fms.currentMap.map.events.register("zoomend", null, function() {
                                self.selectFeature.onUnselect(feature);
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
            this.features = [];

        }
        var markerPoint = new OpenLayers.Geometry.Point(report.point.x,report.point.y);
        var newMarker = new OpenLayers.Feature.Vector(markerPoint, {'report':report});
        this.features.push(newMarker);

        return newMarker;
        // console.log(this.markersLayer);

        //Can be either orange, red or green and in the set of regional route or not.
        // var markerConf;

        // markerConf = (report.status == 3 || report.status == 9) ? fixedMarkerStyle : report.status == 1 ? defaultMarkerStyle : (report.status==5 || report.status ==6) ? pendingMarkerStyle : pendingMarkerStyle;
        // return new OpenLayers.Feature.Vector(newMarker, {'report':report}, markerConf);
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