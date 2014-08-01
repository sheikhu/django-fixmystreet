L.FixMyStreet = L.FixMyStreet || {};

L.FixMyStreet.Map = L.Map.extend({
  DEFAULTS: {
    animate: true,
    center: [50.84535101789271, 4.351873397827148],
    cssSizeRegex: /(^|\s)map-size-\S+/g,
    minZoom: 10,
    maxBounds: [
      [50.95323634832283, 4.7618865966796875],
      [50.736455137010665, 3.9420318603515625],
    ],
    zoom: 14,

    // Layers loaded during initialize
    urbisLayersToLoad: [
      'base-map-fr',
      'municipal-boundaries',
      'regional-roads',
    ],
  },

  options: {
    newIncidentMarker: {
      icon: L.icon({
        iconUrl: STATIC_URL + 'images/pin-fixmystreet-L.png',
        iconAnchor: [20, 52],
        popupAnchor: [0, -35],
      }),
      popupTemplate: '<h5>New Incident</h5>',
    },
  },

  // Config per incident type
  incidentTypes: {
    reported: {
      title: gettext('Created'),
      color: '#c3272f',
      filterTitle: '<span class="type-reported"><img src="' + STATIC_URL + 'images/marker-red-xxs.png" />' + gettext('Created') + '</span>',
      icon: L.icon({
        iconUrl: STATIC_URL + 'images/pin-red-L.png',
        iconAnchor: [20, 52],
        popupAnchor: [0, -35],
      }),
      popupTemplate: '<h3><%this.type%></h3>' +
                     '<div><strong>ID:</strong> <%this.id%></div>',
    },
    ongoing: {
      title: gettext('In progress'),
      color: '#f79422',
      filterTitle: '<span class="type-ongoing"><img src="' + STATIC_URL + 'images/marker-orange-xxs.png" />' + gettext('In progress') + '</span>',
      icon: L.icon({
        iconUrl: STATIC_URL + 'images/pin-orange-L.png',
        iconAnchor: [20, 52],
        popupAnchor: [0, -35],
      }),
      popupTemplate: '<h3><%this.type%></h3>' +
                     '<div><strong>ID:</strong> <%this.id%></div>',
    },
    closed: {
      title: gettext('Closed'),
      color: '#3cb64b',
      filterTitle: '<span class="type-closed"><img src="' + STATIC_URL + 'images/marker-green-xxs.png" />' + gettext('Closed') + '</span>',
      icon: L.icon({
        iconUrl: STATIC_URL + 'images/pin-green-L.png',
        iconAnchor: [20, 52],
        popupAnchor: [0, -35],
      }),
      popupTemplate: '<h3><%this.type%></h3>' +
                     '<div><strong>ID:</strong> <%this.id%></div>',
    },
  },

  _incidentLayers: {},
  incidents: [],

  initialize: function (id, options) {  // (HTMLElement or String, Object)
    options = $.extend(true, {}, this.DEFAULTS, options);
    L.Map.prototype.initialize.call(this, id, options);

    this._namedLayers = {};
    this._templateCache = {};

    this.attributionControl.setPosition('bottomleft');
    this._initUrbisLayers();
    this._initIncidentLayers();
    this.initIncidentTypeFilter();
  },

  setOptions: function (options) {
    options = options || this.DEFAULTS;

    // Center AND zoom available
    if (options.center && options.zoom !== undefined) {
      this.setView(L.latLng(options.center), options.zoom, {reset: true});
    } else {
      // Only zoom available
      if (options.zoom) {
        this.setZoom(options.zoom);
      }
      // Only center available
      if (options.center) {
        this.panTo(L.latLng(options.center));
      }
    }
  },

  // NAMED LAYERS --------------------------------------------------------------

  toggleNamedLayer: function (key, visibility) {  // (String, Boolean)
    if (this.hasNamedLayer(key)) {
      $(this._namedLayers[key].getContainer()).toggle(visibility);
    } else if (visibility !== false) {
      this.loadNamedLayer(key);
    }
  },

  hasNamedLayer: function (key) {  // (String)
    return (key in this._namedLayers);
  },

  getNamedLayer: function (key) {  // (String)
    if (!this.hasNamedLayer(key)) { return; }
    return this._namedLayers[key];
  },

  loadNamedLayer: function (key, options) {  // (String, Object)
    var layer;
    if (options === undefined) {
      options = this.getNamedLayerSettings(key);
    }

    // If options contains a `key` parameter, use it for named layers.
    // This allows to define groups of layers that act like a "singleton" (only one of them is loaded).
    // Example: Base map available in different languages or visualizations (map or satellite view).
    key = options.key || key;

    // Factory based on layer type
    switch (options.type) {
      case 'wms': layer = L.tileLayer.wms(options.url, options.options); break;
      default: layer = L.tileLayer(options.url, options.options);
    }

    // Load map options provided by the layer
    if (options.mapOptions !== undefined) {
      this.setOptions(options.mapOptions);
    }

    // Register as named layer
    this._setNamedLayer(key, layer);
  },

  unloadNamedLayer: function (key) {  // (String)
    this._unsetNamedLayer(this.getNamedLayerKey(key));
  },

  getNamedLayerKey: function (key) {  // (String)
    if (key in this._namedLayers) {
      return key;
    }
    if (key in L.FixMyStreet.Map.namedLayersSettings && L.FixMyStreet.Map.namedLayersSettings[key].key) {
      return L.FixMyStreet.Map.namedLayersSettings[key].key;
    }
    throw new Error('Invalid key "' + key + '".');
  },

  getNamedLayerSettings: function (key) {  // (String)
    if (!(key in L.FixMyStreet.Map.namedLayersSettings)) {
      throw new Error('Layer settings not found for "' + key + '".');
    }
    return L.FixMyStreet.Map.namedLayersSettings[key];
  },

  _setNamedLayer: function (key, layer) {  // (String, L.ILayer)
    if (this.hasNamedLayer(key)) {
      if (this._namedLayers[key] === layer) { return; }
      this._unsetNamedLayer(key);
    }

    this.addLayer(layer);
    this._namedLayers[key] = this._layers[L.stamp(layer)];
  },

  _unsetNamedLayer: function (key) {  // (String)
    if (!this.hasNamedLayer(key)) { return; }
    this.removeLayer(this._namedLayers[key]);
    delete this._namedLayers[key];
  },

  // MARKERS -------------------------------------------------------------------

  addMarker: function (latlng, options) {  // ([L.LatLng or Object], [Object], [L.ILayer])
    var model = null;

    // @FIXME: Fix arguments detection/swapping. Or use an "options" arg for all non-mandatory parameters.
    if (latlng !== undefined && !(latlng instanceof L.LatLng)) {
      model = latlng;
      latlng = this.toLatLng(model.latlng);
    }
    if ('_layerAdd' in options) {  // @FIXME: Should test `instanceof L.ILayer`
      container = options;
      options = {};
    }

    latlng = latlng || this.getCenter();
    options = options || {};
    // container = container || this;

    var m = new L.FixMyStreet.Marker(latlng, options, model);
    // container.addLayer(m);
    return m;
  },

  // INCIDENTS -----------------------------------------------------------------

  addIncident: function (model, options) {  // (Object, [Object])
    if (!(model.type in this.incidentTypes)) {
      console.log('ERROR: Invalid incident type "' + model.type + '".');
      return;
    }

    options = options || {};

    var that = this;
    var markerOptions = $.extend(true, {
      icon: this.incidentTypes[model.type].icon,
      popupTemplate: this.incidentTypes[model.type].popupTemplate,
    }, options);

    var m = this.addMarker(model, markerOptions).addTo(this._incidentLayers[model.type]);

    m.on('click', function (evt) {
      that._incident_onClick(evt);
    });

    this.incidents.push(m);
    return m;
  },

  addIncidents: function (incidents, baseOptions) {  // (Object, [Object])
    baseOptions = baseOptions || {};

    for (var i = 0; i < incidents.length; i++) {
      var model = 'model' in incidents[i] ? incidents[i].model
                                          : incidents[i];
      var options = $.extend(true, {}, baseOptions, incidents[i].options || {});
      this.addIncident(model, options);
    }
  },

  addIncidentsFromGeoJson: function (data, baseOptions) {  // (String or Object, [Object])
    if (typeof data === 'string') {
      this._addIncidentsFromGeoJsonUrl(data, baseOptions);
    } else {
      this._addIncidentsFromGeoJson(data, baseOptions);
    }
  },

  removeAllIncidents: function () {
    for (var incidentType in this.incidentTypes) {
      this._incidentLayers[incidentType].clearLayers();
    }
    while (this.incidents.length > 0) {
      this.incidents.pop();
    }
  },

  addNewIncidentMarker: function (latlng, options) {
    if (this.newIncidentMarker) {
      console.log('WARNING: A new incident marker is already loaded.');
      return;
    }

    latlng = this.toLatLng(latlng);
    options = options || {};

    var that = this;
    var markerOptions = $.extend(true, {
      draggable: true,
      icon: this.options.newIncidentMarker.icon,
      popupTemplate: this.options.newIncidentMarker.popupTemplate,
    }, options);

    this.newIncidentMarker = this.addMarker(latlng, markerOptions).addTo(this);

    this.newIncidentMarker.on('dragend', function (evt) {
      that._newIncidentMarker_onDragEnd(evt);
    });

    return this.newIncidentMarker;
  },

  removeNewIncidentMarker: function () {
    this.removeLayer(this.newIncidentMarker);
    this.newIncidentMarker = null;
  },

  _addIncidentsFromGeoJson: function (geoJson, baseOptions) {  // (Object, [Object])
    var that = this;
    baseOptions = baseOptions || {};

    var geoJsonOptions = {
      pointToLayer: function (featureData, latlng) {
        var model = $.extend({}, featureData.properties, {
          latlng: latlng,
        });
        return that.addIncident(model);
      },
    };

    L.geoJson(geoJson, geoJsonOptions);
  },

  _addIncidentsFromGeoJsonUrl: function (url, baseOptions) {  // (String, [Object])
    var that = this;

    console.log('Loading GeoJSON from %s...', url);
    $.get(url, function (geoJson) {
      console.log('GeoJSON received...');
      that._addIncidentsFromGeoJson(geoJson, baseOptions);
    }).fail(function() {
      console.log('ERROR:', argument);
    });
  },

  // CONTROLS ------------------------------------------------------------------

  initIncidentTypeFilter: function (options) {
    if ($.isEmptyObject(this._incidentLayers)) { return; }

    var that = this;
    var baseLayers = null;
    var overlays = {};

    options = $.extend({
      collapsed: false,
      position: 'bottomleft',
    }, options);

    $.each(this.incidentTypes, function (k, v) {
      var title = v.filterTitle || v.title || k;
      overlays[title] = that._incidentLayers[k];
    });

    L.control.layers(baseLayers, overlays, options).addTo(this);
  },

  // HELPERS -------------------------------------------------------------------

  latLngToString: function (latlng) {
    return latlng.lat + ',' + latlng.lng;
  },

  latLngFromString: function (s) {
    var chunks = s.split(/,\s*/);
    return new L.LatLng(parseFloat(chunks[0]), parseFloat(chunks[1]));
  },

  toLatLng : function (latlng) {  // (L.LatLng or String or Object)
    if (latlng === undefined || latlng instanceof L.LatLng) { return latlng; }
    if (typeof latlng === 'string') { return this.latLngFromString(latlng); }
    if (typeof latlng === 'object') {
      if ('lat' in latlng && 'lng' in latlng) { return new L.LatLng(latlng.lat, latlng.lng); }
      else if (0 in latlng && 1 in latlng) { return new L.LatLng(latlng[0], latlng[1]); }
    }
    throw new Error('Invalid parameter. Expect L.LatLng or String ("0.123,-45.678") or Object ({lat: 0.123, lng: -45.678}) or Object ([0.123, -45.678]).');
  },

  centerMapOnMarker: function (marker) {
    this.panTo(marker.getLatLng());
  },

  setCssSize: function (cls) {  // (String)
    var that = this;
    this.$container.removeClass(function (index, css) {
      return (css.match(that.options.cssSizeRegex) || []).join(' ');
    });
    if (cls) {
      this.$container.addClass(cls);
    }
    this.invalidateSize(this.options.animate);
  },

  // INITIALIZATION ------------------------------------------------------------

  _initContainer: function (id) {  // (String)
    L.Map.prototype._initContainer.call(this, id);
    this.$container = $(this._container);
  },

  _initUrbisLayers: function () {
    var that = this;

    // Customize `L.FixMyStreet.Map.namedLayersSettings`
    L.FixMyStreet.Map.namedLayersSettings['regional-roads']['options']['opacity'] = 0.5;
    L.FixMyStreet.Map.namedLayersSettings['regional-roads']['options']['filter'] =
      '<ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">' +
        '<ogc:PropertyIsEqualTo matchCase="true">' +
          '<ogc:PropertyName>ADMINISTRATOR</ogc:PropertyName>' +
          '<ogc:Literal>REG</ogc:Literal>' +
        '</ogc:PropertyIsEqualTo>' +
      '</ogc:Filter>';

    // Load initial UrbIS layers
    $.each(this.options.urbisLayersToLoad, function (k, v) {
      that.loadNamedLayer(v, L.FixMyStreet.Map.namedLayersSettings[v]);
    });
  },

  _initIncidentLayers: function () {
    var that = this;

    this._incidentLayers = {};
    $.each(this.incidentTypes, function (k, v) {
      that._incidentLayers[k] = new L.FixMyStreet.Map.MarkerClusterGroup();
      that._incidentLayers[k].on('clusterclick', function (evt) {
        that._cluster_onClick(evt);
      });
      that._incidentLayers[k].addTo(that);
    });
  },

  // EVENT HANDLERS ------------------------------------------------------------

  _cluster_onClick: function (evt) {  // layer.clusterclick
  },

  _incident_onClick: function (evt) {  // marker.click
    this.centerMapOnMarker(evt.target);
  },

  _newIncidentMarker_onDragEnd: function (evt) {  // marker.dragend
    var marker = evt.target;
    var position = marker.getLatLng();
    marker.setLatLng(new L.LatLng(position.lat, position.lng), {draggable: 'true'});
    this.panTo(new L.LatLng(position.lat, position.lng));
  },

  // STATIC --------------------------------------------------------------------

  statics: {
    namedLayersSettings: {},
  },
});


L.FixMyStreet.Marker = L.Marker.extend({
  initialize: function (latlng, options, model) {
    L.Marker.prototype.initialize.call(this, latlng, options);
    this.model = model || {};

    if (this.options.iconOptions) {
      L.setOptions(this.options.icon, this.options.iconOptions);
    }
    if (this.options.popup || this.options.popupTemplate) {
      this.bindPopup(this.options.popup, this.options.popupOptions);
    }
  },

  openPopup: function (latlng) {
    if (this.options.popupTemplate) {
      var that = this;
      L.FixMyStreet.Template.render(this.options.popupTemplate, this.model, function (error, html) {
        that.setPopupContent(html);
      });
    }
    L.Marker.prototype.openPopup.call(this, latlng);
    return this;
  },
});


L.FixMyStreet.Map.MarkerClusterGroup = L.MarkerClusterGroup.extend({
  iconCreateFunction: function(cluster) {
    return new L.DivIcon({ html: '<b style="">' + cluster.getChildCount() + '</b>' });
  }
});


L.FixMyStreet.IncidentMarker = L.Marker.extend({
});


L.FixMyStreet.Template = {
  _cache: {},

  render: function(html, options, done) {
    // See: https://github.com/tunnckoCore/octet (+ added cache)
    // Alternative: http://ejohn.org/blog/javascript-micro-templating/
    if (!(html in L.FixMyStreet.Template._cache)) {
      var re = /<%([^%>]+)?%>/g;
      var reExp = /(^( )?(if|for|else|switch|case|break|{|}))(.*)?/g;
      var code = 'var r=[];\n';
      var cursor = 0;
      var add = function(line, js) {
        js? (code += line.match(reExp) ? line + '\n' : 'r.push(' + line + ');\n') :
            (code += line ? 'r.push("' + line.replace(/"/g, '\\"') + '");\n' : '');
        return add;
      };
      while (match = re.exec(html)) {
        add(html.slice(cursor, match.index))(match[1], true);
        cursor = match.index + match[0].length;
      }
      add(html.substr(cursor, html.length - cursor));
      code += 'return r.join("");';
      L.FixMyStreet.Template._cache[html] = new Function(code.replace(/[\r\t\n]/g, ''));
    }
    try {
      var result = L.FixMyStreet.Template._cache[html].apply(options, [options]);
      if ('function' === typeof done) return done(null, result);
      else return {err: null, res: result};
    } catch(err) {
      if ('function' === typeof done) return done(err, null);
      console.error("'" + err.message + "'", " in \n\nCode:\n", code, "\n");
      return {err: err, res: null};
    }
  },
};
