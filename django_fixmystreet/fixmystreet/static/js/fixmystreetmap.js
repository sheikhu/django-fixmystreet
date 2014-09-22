// required : -http://openlayers.org/dev/OpenLayers.js
//              -http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.min.js

if (!('fms' in window)) {
    window.fms = {};
    //A local cache to avoid multiple calls to backend system when clicking on filters
    window.fms.cachedElements = false;
    window.fms.city_geo_center = [];
    window.fms.city_geo_center["M1070"] = {x:"145367.6654217966",y:"168649.68734662264"}; //Anderlecht
    window.fms.city_geo_center["M1160"] = {x:"154046.91650777997",y:"167337.15162906327"}; //Auderghem
    window.fms.city_geo_center["M1082"] = {x:"144863.51262962123",y:"172813.29402682924"}; //Berchem
    window.fms.city_geo_center["M1130"] = {x:"153831.7823421533",y:"175129.78918397945"}; //Haren
    window.fms.city_geo_center["M1020"] = {x:"149092.31148122973",y:"175999.01813600562"}; //Laeken
    window.fms.city_geo_center["M1120"] = {x:"151371.86440791885",y:"176103.325610249"}; //Never
    window.fms.city_geo_center["M1000"] = {x:"148605.543268095",y:"170874.91346381"}; //Bxl Ville
    window.fms.city_geo_center["M1040"] = {x:"151510.94104024282",y:"168866.99458462943"}; //Etterbeek
    window.fms.city_geo_center["M1140"] = {x:"152629.7842298689",y:"173392.55983061116"}; //Evere
    window.fms.city_geo_center["M1190"] = {x:"147023.54657540703",y:"167176.34427293818"}; //Forest
    window.fms.city_geo_center["M1083"] = {x:"145841.39520065105",y:"173778.13816357817"}; //Ganshoren
    window.fms.city_geo_center["M1050"] = {x:"149370.46474587804",y:"167732.65080223506"}; //Ixelles
    window.fms.city_geo_center["M1090"] = {x:"147375.58430097767",y:"174064.98371774668"}; //Jette
    window.fms.city_geo_center["M1081"] = {x:"146814.9316269208",y:"172639.4482364241"}; //Koekelberg
    window.fms.city_geo_center["M1080"] = {x:"146793.20090312013",y:"171522.48903306987"}; //Molenbeek
    window.fms.city_geo_center["M1060"] = {x:"148283.92855584505",y:"168719.2256627849"}; //Saint Gilles
    window.fms.city_geo_center["M1210"] = {x:"149842.02145235223",y:"171587.68120447194"}; //Saint Josse
    window.fms.city_geo_center["M1030"] = {x:"151465.0174341536",y:"172366.8696672201"}; //Schaerbeek
    window.fms.city_geo_center["M1180"] = {x:"149305.27257447632",y:"165224.92527563902"}; //Uccle
    window.fms.city_geo_center["M1170"] = {x:"153173.34141099357",y:"165011.96418239252"}; //Watermael
    window.fms.city_geo_center["M1200"] = {x:"155011.7606445293",y:"170787.99056860784"}; //Woluwe Saint Lambert
    window.fms.city_geo_center["M1150"] = {x:"154577.14616851608",y:"168788.76397894725"}; //Woluwe Saint Pierre
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

var tooltipRegional       = gettext('This incident is located on a regional zone'),
    tooltipPro            = gettext('This incident has been signaled by a pro'),
    tooltipContractor     = gettext('This incident is assigned to'),
    tooltipDatePlanned    = gettext('Date planned'),
    tooltipSolved         = gettext('This incident has been signaled as solved'),
    tooltipNoPriority     = gettext('This incident has no defined priority'),
    tooltipLowPriority    = gettext('This incident has a low priority'),
    tooltipMediumPriority = gettext('This incident has a medium priority'),
    tooltipHighPriority   = gettext('This incident has a serious priority');

var lastpopup;


/**
 * Method used to store datatable sort preferences
 */
fms.storeTablePreferences = function(argElement) {
    if (typeof localStorage !== 'undefined') {
        if (typeof argElement.sort !== 'undefined') {
            localStorage.setItem("fms-table-column-sort", JSON.stringify({'idx':argElement.sort[0][0], 'sortType':argElement.sort[0][1]/*asc or desc*/}));
        }
        if (typeof argElement.unselectedColumn !== 'undefined') {
            localStorage.setItem("fms-table-column-inactive", JSON.stringify(argElement.unselectedColumn));
        }
    } else {
        return null;
    }
};

/**
 * Method used to get datatable sort preferences
 */
fms.restoreTablePreferences = function() {
    if (typeof localStorage !== 'undefined') {
        var argElements = {};
        argElements.sort = null;
        argElements.unselectedColumn = null;
        argElements.sort = JSON.parse(localStorage.getItem("fms-table-column-sort"));
        argElements.unselectedColumn = JSON.parse(localStorage.getItem("fms-table-column-inactive"));
        return argElements;
    } else {
        return null;
    }
};

fms.filterMapWithStatus = function(callback){
    if (fms.cachedElements === false) {
        $.ajax({
            url:"/"+LANGUAGE_CODE+"/ajax/map/filter/",
            type:'GET',
            datatype:"json",
            success: function(data){
                // if (fms.currentMap.markersLayer) {
                //     fms.currentMap.markersLayer.destroyFeatures();
                // }
                // fms.currentMap.addReportCollection(data);
                // fms.cachedElements = true;
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
};

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
        // urbisUrl = "http://geoserver.gis.irisnet.be/geoserver/wms",
        apiLang = "fr",
        showControl = true,
        createdMarkerStyle = cloneObj(defaultMarkerStyle),
        fixedMarkerStyle = cloneObj(defaultMarkerStyle),
        rejectedMarkerStyle = cloneObj(defaultMarkerStyle),
        pendingMarkerStyle = cloneObj(defaultMarkerStyle),
        draggableMarkerStyle = cloneObj(defaultMarkerStyle),

        createdRule = new OpenLayers.Rule({
            name: "rule-created",
            filter: new OpenLayers.Filter({
                evaluate: function (context) {
                    return context.created;
                }
            }),
            symbolizer: createdMarkerStyle,
            elseFilter: true
        }),
        inProgressRule = new OpenLayers.Rule({
            name: "rule-in-progress",
            filter: new OpenLayers.Filter({
                evaluate: function (context) {
                    return context.inProgress;
                }
            }),
            symbolizer: pendingMarkerStyle,
            elseFilter: true
        }),
        processedRule = new OpenLayers.Rule({
            name: "rule-processed",
            filter: new OpenLayers.Filter({
                evaluate: function (context) {
                    return context.processed;
                }
            }),
            symbolizer: fixedMarkerStyle,
            elseFilter: true
        }),
        rejectedRule = new OpenLayers.Rule({
            name: "rule-rejected",
            filter: new OpenLayers.Filter({
                evaluate: function (context) {
                    return context.rejected;
                }
            }),
            symbolizer: rejectedMarkerStyle,
            elseFilter: true
        });

    createdMarkerStyle.externalGraphic = "/static/images/pin-red-L.png";
    createdMarkerStyle.display = "";

    rejectedMarkerStyle.externalGraphic = "/static/images/pin-gray-L.png";
    rejectedMarkerStyle.display = "";

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
            trigger: function() {
                fms.currentMap.centerOnDraggableMarker();
            }
        });
        //centerMapButton.panel_div.innerHTML = "zaza";
        //Center Panel
        var centerPanel = new OpenLayers.Control.Panel({
            defaultControl: centerMapButton
        });

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
        var regionalLimitsTitle = gettext("regional_limits");
        var municipalityLimitsTitle = gettext("municipality_limits");


        // Add regional limits layer
        fms.regionalLayer = new OpenLayers.Layer.WMS(regionalLimitsTitle,
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
        fms.municipalityLayer = new OpenLayers.Layer.WMS(municipalityLimitsTitle,
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

        this.element.addEventListener('transitionend', function () {
            fms.currentMap.map.updateSize();
        });
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

    fms.Map.prototype.centerOnMunicipality = function(argMunicipalityCode)
    {
        //Prefixed by M to avoid big array creation (as idnex integer based)
        this.map.panTo(new OpenLayers.LonLat(window.fms.city_geo_center["M"+argMunicipalityCode].x, window.fms.city_geo_center["M"+argMunicipalityCode].y));

        //this.map.zoomTo(6);
        //Show draggable Marker.
        this.addDraggableMarker(window.fms.city_geo_center["M"+argMunicipalityCode].x, window.fms.city_geo_center["M"+argMunicipalityCode].y);
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
    fms.Map.prototype.toogleCreated = function(show)
    {
        this.flagCreated = show;
        createdRule.symbolizer.display = show || "none";
        this.refreshCluster();
    };
    /* Method to toogle in progress filter element */
    fms.Map.prototype.toogleInProgress = function(show)
    {
        this.flagInProgress = show;
        inProgressRule.symbolizer.display = show || "none";
        this.refreshCluster();
    };
    /* Method to toogle closed filter element */
    fms.Map.prototype.toogleClosed = function(show)
    {
        this.flagClosed = show;
        processedRule.symbolizer.display = show || "none";
        this.refreshCluster();
    };
    /* Method to refresh the cluster content */
    fms.Map.prototype.refreshCluster = function()
    {
        var features = [];

        for (var featureIndex in this.markers) {
            var currentFeature = this.markers[featureIndex];
            var report = currentFeature.attributes;
            if (
                (this.flagInProgress && report.inProgress) ||
                (this.flagCreated && report.created) ||
                (this.flagClosed && report.processed) || report.rejected
            ) {
                features.push(currentFeature);
            }
        }
        this.strategy.features = features;
        // this.strategy.layer.removeAllFeatures();
        this.strategy.layer.redraw(true);
    };



    /**
     * Add a draggable marker to the current map. Send a "markermoved" event to
     * the map element when the marker move.
     * @param x float define the position of the marker (in Lambert72 coordinate system)
     * @param y float define the position of the marker (in Lambert72 coordinate system)
     */
    fms.Map.prototype.addDraggableMarker = function(x, y)
    {
        var self = this;
        this.selectedLocation = {x:x, y:y};

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
                // Remove all popups
                while(this.map.popups.length) {
                     this.map.removePopup(this.map.popups[0]);
                }
            },
            onComplete:function(feature,pixel){
                var p = feature.geometry.components[0];
                self.selectedLocation = {x:p.x,y:p.y};
                $(self.element).trigger('markermoved', self.selectedLocation, self.draggableMarker);
            },
            onDrag:function(event){
                // var markerBounds = event.geometry.bounds;
                // var mapBounds = this.map.getExtent();
                // var delta = 100;
                // if(mapBounds.left+delta > markerBounds.left) {
                //     this.map.pan(-100,0,{});
                // }
                // else if (mapBounds.right-delta < markerBounds.right){
                //     this.map.pan(100,0,{});
                // }
                // else if (mapBounds.top-delta < markerBounds.top){
                //     this.map.pan(0,-100,{});
                // }
                // else if(mapBounds.bottom + delta > markerBounds.bottom){
                //     this.map.pan(0,100,{});
                // }
            }
        });

        this.map.addControl(dragControl);
        dragControl.activate();

        this.draggableMarker = new OpenLayers.Geometry.Collection([new OpenLayers.Geometry.Point(x,y)]);
        this.dragfeature = new OpenLayers.Feature.Vector(this.draggableMarker, null, draggableMarkerStyle);
        this.draggableLayer.addFeatures([this.dragfeature]);
        if(this.selectFeature) {
            this.selectFeature.setLayer([this.markersLayer, this.draggableLayer]);
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
                    status:gettext("Unexpected error")
                });
            }
        });
    };

    /**
     */
    fms.Map.prototype.addReportCollection = function(reports)
    {
        // Clean features
        if(fms.currentMap.markersLayer) {
            this.markers = [];
            fms.currentMap.markersLayer.destroyFeatures();
            // this.map.removeLayer(this.markersLayer);
            // this.markersLayer.destroy();
        }
        for (var filterCpt in reports) {
            this.addReport(reports[filterCpt]);
        }
        this.markersLayer.addFeatures(this.markers);
        this.refreshCluster();
    };
    /**
     * Add a marker to the current map, if fixed is true, the marker will be green, if not it will be red.
     * @param report the report to add
     * @param proVersion true if the application is running the pro version
     */
    fms.Map.prototype.addReport = function(report)
    {
        var self = this;
        if(!this.markersLayer)
        {
            this.markers = [];
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
                        inProgressRule,
                        createdRule,
                        processedRule,
                        rejectedRule,
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
            this.strategy = new OpenLayers.Strategy.Cluster({
                distance:50,
                threshold:2,
                clustering:false,
                rules:markerStyle.rules,
                deactivate: function() {
                    var deactivated = OpenLayers.Strategy.prototype.deactivate.call(this);
                    if(deactivated) {
                        //this.layer.removeAllFeatures();
                        this.layer.events.on({
                            "beforefeaturesadded": this.cacheFeatures,
                            "moveend": this.cluster,
                            scope: this
                        });
                        this.layer.addFeatures(self.strategy.features);
                        this.clearCache();
                    }
                    return deactivated;
                },
                activate: function() {
                    var activated = OpenLayers.Strategy.prototype.activate.call(this);
                    if(activated) {
                        this.layer.events.on({
                            "beforefeaturesadded": this.cacheFeatures,
                            "moveend": this.cluster,
                            scope: this
                        });
                        //this.layer.removeAllFeatures();
                        this.clearCache();
                        self.refreshCluster();
                        this.layer.addFeatures(self.strategy.features);
                    }
                    return activated;
                }
            });

            this.map.events.register("zoomend", null, function() {
                var zoom = self.map.getZoom();

                  if (zoom > 5) {
                    self.strategy.deactivate();
                 } else {
                    self.strategy.activate();
                 }
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

            if (typeof DETAILS_MODE === 'undefined') {
                this.selectFeature = new OpenLayers.Control.SelectFeature(this.markersLayer, {
                    onSelect: function (feature) {
                        //Not available in details mode
                        self.showPopover(feature);
                    },
                    onUnselect: function(feature) {
                        if (lastpopup) {
                            this.map.removePopup(lastpopup);
                            lastpopup.destroy();
                        }
                    }
                });

                self.map.events.register("zoomend", null, function() {
                    if (self.selectFeature && lastpopup) {
                        self.map.removePopup(lastpopup);
                        lastpopup.destroy();
                    }
                });
                this.map.addControl(this.selectFeature);
                this.selectFeature.activate();
            }


        }

        var markerPoint = new OpenLayers.Geometry.Point(report.point.x, report.point.y);

        var status = report.status;
        report.created = status === 1;
        report.inProgress = status === 2 ||
                            status === 4 ||
                            status === 5 ||
                            status === 6 ||
                            status === 7;
        report.rejected = status === 9;
        report.processed = status === 3;

        var newMarker = new OpenLayers.Feature.Vector(markerPoint, report);
        this.markers.push(newMarker);

        return newMarker;
    };

    fms.Map.prototype.showPopover = function(feature) {
        var self = this;

        if(feature.layer.name != "Dragable Layer" && !feature.cluster){
            $.ajax({
                type:'GET',
                url:"/"+getCurrentLanguage()+((BACKOFFICE)?"/pro":"")+"/ajax/reportPopupDetails/",
                data:{'report_id':feature.attributes.id},
                datatype:"json",
                success:function(data){
                    var report = data;

                    var imageLink = "/static/images/no-pix.png";

                    if (report.thumb != 'null') {
                        imageLink = report.thumb;
                    }

                    // Set content of popover
                    var popoverTitle   = "";
                    var popoverContent = "";
                    var popoverIcons   = "";
                    var popoverSize  = new OpenLayers.Size(400,220);

                    popoverTitle = "<h2>" + gettext('Report') + " #" + report.id + " </h2>";

                    popoverContent = '<div class="details-popup"><p style="float: right;margin-left: 15px;"><img class="thumbnail" src="' + imageLink +'"/></p>' +
                        "<a class='moreDetails' style='clear:both; float: right;margin-left: 15px;' href='/"+getCurrentLanguage()+((BACKOFFICE)?"/pro":"")+"/report/search?report_id="+report.id+"'>" + gettext('Details') + "</a>" +
                        "<strong class='popup_adress'>" + report.address_number + ', ' +
                        report.address + ' ' + "<br/>" +
                        report.postalcode + ' ' +
                        report.address_commune_name + "</strong>" +


                        "<p class='categoryPopup'>" + report.category + "</p></div>";

                    popoverIcons += "<ul class='iconsPopup'>";


                    //CONTENU DES ICONES
                    //******************
                    if (report.address_regional === true){
                        popoverIcons += "<li class='addressRegional'><img title='"+tooltipRegional+"' src='/static/images/regional_on.png' /></li>";
                    }

                    if (report.citizen === false) {
                        popoverIcons += "<li class='contractorAssigned'><img title='"+tooltipPro+"' src='/static/images/pro_on.png' /></li>";
                    }

                    if (report.contractor === true){
                        popoverIcons += "<li class='contractorAssigned'><img title='"+tooltipContractor+"' src='/static/images/contractorAssigned_on.png' /></li>";
                    }

                    if (report.date_planned){
                        popoverIcons += "<li class='datePlanned_on'>"+report.date_planned+"</li>";
                    }


                    if (BACKOFFICE) {
                        popoverIcons += "<li>";
                        if (report.priority === 0){
                            popoverIcons += "<img title='"+tooltipNoPriority+"' src='/static/images/prior_off.png' class='priorityLevel' />";
                        } else if (report.priority <= 2){
                            popoverIcons += "<img title='"+tooltipLowPriority+"' src='/static/images/prior_on_1.png' class='priorityLevel' />";
                        } else if (report.priority <= 8){
                            popoverIcons += "<img title='"+tooltipMediumPriority+"' src='/static/images/prior_on_2.png' class='priorityLevel' />";
                        } else {
                            popoverIcons += "<img title='"+tooltipHighPriority+"' src='/static/images/prior_on_3.png' class='priorityLevel' />";
                        }
                        popoverIcons += "</li>";

                        if (report.isSolved) {
                            popoverIcons += "<li class='isSolved'><img title='"+tooltipSolved+"' src='/static/images/is_resolved_on.png' /></li>";

                        }

                    }

                    //FIN CONTENU DES ICONES
                    //**********************
                    popoverIcons += "</ul>";

                    var popup = new OpenLayers.Popup(
                        "popup",
                        new OpenLayers.LonLat(report.point.x, report.point.y),
                        popoverSize,
                        '<div class="in-popup">' + popoverTitle + popoverContent + popoverIcons + '</div>',
                        true,
                        function closeMe() {
                            self.selectFeature.onUnselect(feature);
                        }
                    );
                    lastpopup = popup;

                    popup.div.className = 'reports';
                    popup.panMapIfOutOfView = true;

                    self.map.addPopup(popup);
                }
            });
        }

        if(feature.cluster){
            if(this.map.zoom == this.map.numZoomLevels){
                var content = "<h2>" + gettext('Reports at this location') + ":</h2><ul>";
                for(var i = 0; i< feature.cluster.length; i++){
                    content +="<li><a href='/"+getCurrentLanguage()+((BACKOFFICE)?"/pro":"")+"/report/search?report_id="+feature.cluster[i].data.report.id+"'>" + gettext('Report') + " #"+feature.cluster[i].data.report.id+"</a></li>";
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