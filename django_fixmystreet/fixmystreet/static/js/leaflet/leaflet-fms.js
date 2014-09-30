/* @TODO
- L.FixMyStreet.Util.urbisResultToAddress(): Retrieve it according to postal code.

# Bugs & co
- Weird behavior of auto panning, especially with open pop-ups.
    - L.FixMyStreet.centerOnMarker(): Check if popup is opened and adapt LatLng accordingly.

# Improvements
- L.FixMyStreet.Map.options.myLayers: Rename variable.
- Document library (inline?)

# Refactoring
- Split this file?
- Review what's in this.options => should be an object attribute?
- L.FixMyStreet.Marker.toggle(): Refactor?
- L.FixMyStreet.Map "controls": Refactor as L.FixMyStreet.*Control.
- L.FixMyStreet._toggleLayer(): Refactor?
- L.FixMyStreet.NewIncidentMarker.onAdd(): Workaround, otherwise LocateOnMap doesn't work.
- L.FixMyStreet.NewIncidentMarker._onDragEnd() & L.FixMyStreet.NewIncidentPopup.activate(): Bug but workaround in place.
- L.FixMyStreet.NewIncidentPopup.autoPanDisabled: Refactor? Isn't there a better way?
- L.FixMyStreet.Util.mergeExtendedOptions(): Refactor? Isn't there a better way?
- L.FixMyStreet.Util.openStreetView(): Refactor? Improve URL generation?

# Discarded
- UrbIS layer 'street-names': Not working well. Names not displayed at zoom > 16.
- UrbIS layer 'street-numbers': Not working. Nothing visible.
*/


// DJANGO COMPAT

if (LANGUAGE_CODE === undefined) { var LANGUAGE_CODE = 'fr'; }
if (STATIC_URL === undefined) { var STATIC_URL = '/static/'; }
if (DEBUG === undefined) { var DEBUG = false; }
if (gettext === undefined) { function gettext(s) { return s; } }


// INIT

L.FixMyStreet = L.FixMyStreet || {};
if (NEW_INCIDENT_URL === undefined) { var NEW_INCIDENT_URL = ''; }
if (URBIS_URL === undefined) { var URBIS_URL = 'http://gis.irisnet.be/'; }


// URBIS LAYERS ================================================================

L.FixMyStreet.UrbisLayersSettings = {
  'map-street-fr': {
    title: 'Street',
    type: 'wms',
    url: URBIS_URL + 'geoserver/gwc/service/wms',
    options: {
      layers: 'urbisFR',
      format: 'image/png',
      transparent: true,
      crs: L.CRS.EPSG3857,  // L.CRS.EPSG31370
      attribution: 'Realized by means of Brussels UrbIS &copy; &reg;',
    },
  },

  'map-street-nl': {
    title: 'Street',
    type: 'wms',
    url: URBIS_URL + 'geoserver/gwc/service/wms',
    options: {
      layers: 'urbisNL',
      format: 'image/png',
      transparent: true,
      crs: L.CRS.EPSG3857,  // L.CRS.EPSG31370,
      attribution: 'Realized by means of Brussels UrbIS &copy; &reg;',
    },
  },

  'map-ortho': {
    title: 'Orthographic',
    type: 'wms',
    url: URBIS_URL + 'geoserver/gwc/service/wms',
    options: {
      layers: 'urbisORTHO',
      format: 'image/png',
      transparent: true,
      crs: L.CRS.EPSG3857,  // L.CRS.EPSG31370,
      attribution: 'Realized by means of Brussels UrbIS &copy; &reg;',
    },
  },

  'regional-roads': {
    overlay: true,
    title: 'Regional roads',
    type: 'wms',
    url: URBIS_URL + 'geoserver/wms',
    options: {
      layers: 'urbis:URB_A_SS',
      styles: 'URB_A_SS_FIXMYSTREET',
      format: 'image/png',
      transparent: true,
      opacity: 0.5,
      filter: '<ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">' +
                '<ogc:PropertyIsEqualTo matchCase="true">' +
                  '<ogc:PropertyName>ADMINISTRATOR</ogc:PropertyName>' +
                  '<ogc:Literal>REG</ogc:Literal>' +
                '</ogc:PropertyIsEqualTo>' +
              '</ogc:Filter>',
    },
  },

  'municipal-boundaries': {
    overlay: true,
    title: 'Municipal boundaries',
    type: 'wms',
    url: URBIS_URL + 'geoserver/wms',
    options: {
      layers: 'urbis:URB_A_MU',
      styles: 'fixmystreet_municipalities',
      format: 'image/png',
      transparent: true,
    },
  },

  // @TODO: Not working well. Names not displayed at zoom > 16.
  // 'street-names': {
  //   overlay: true,
  //   title: 'Street names',
  //   type: 'wms',
  //   url: URBIS_URL + 'geoserver/wms',
  //   options: {
  //     layers: 'urbis:URB_A_MY_SA',
  //     format: 'image/png',
  //     transparent: true,
  //   },
  // },

  // @TODO: Not working. Nothing visible.
  // 'street-numbers': {
  //   overlay: true,
  //   title: 'Street numbers',
  //   type: 'wms',
  //   url: URBIS_URL + 'geoserver/wms',
  //   options: {
  //     layers: 'urbis:URB_A_ADPT',
  //     format: 'image/png',
  //     transparent: true,
  //   },
  // },
};


// TEMPLATE ====================================================================

L.FixMyStreet.Template = {
  /**
    * Stores cached templates.
    * @type {object}
    * @memberOf L.FixMyStreet.Template
    */
  _cache: {},

  /**
    * RegExp to identify partial templates (matched against the key).
    * @type {RegExp}
    * @memberOf L.FixMyStreet.Template
    */
  partialTemplateRegex: /^_.*_$/,

  /**
   * Renders a named template, that may include partials.
   *
   * @param {object} data - The data for the template.
   * @param {string} [key=base] - The key identifying the template to render.
   * @param {renderTemplateCallback} done - The callback that handles the rendered content.
   */
  /**
   * @callback renderTemplateCallback
   # @param {object} The error.
   # @param {string} The rendered content.
   */
  _render: function (data, key, done) {
    if (!this.options.templates) { return; }

    data = data || {};
    if (typeof key === 'function' && done === undefined) {
      done = key;
      key = null;
    }
    key = key || 'base';
    var template = this.options.templates[key] || this.options.templates.base;

    // Include the code of each partials in the main template.
    for (var k in this.options.templates) {
      if (this.partialTemplateRegex.test(k) === false) { continue; }
      template = template.replace(new RegExp('\\{' + k + '\\}', 'g'), this.options.templates[k]);
    }

    this._renderTemplate(template, data, done);
  },

  /**
   * Renders a template string.
   *
   * @see {@link https://github.com/tunnckoCore/octet}
   * @ssee {@link http://ejohn.org/blog/javascript-micro-templating/}
   *
   * @param {string} html - The template code.
   * @param {object} data - The data for the template.
   * @param {renderTemplateCallback} done - The callback that handles the rendered content.
   */
  _renderTemplate: function (html, options, done) {
    if (!(html in L.FixMyStreet.Template._cache)) {
      var re = /<%([^%>]+)?%>/g;
      var reExp = /(^( )?(if|for|else|switch|case|break|{|}))(.*)?/g;
      var code = 'var r=[];\n';
      var cursor = 0;
      var add = function(line, js) {
        if (js) {
          code += line.match(reExp) ? line + '\n' : 'r.push(' + line + ');\n';
        } else {
          code += line ? 'r.push("' + line.replace(/"/g, '\\"') + '");\n' : '';
        }
        return add;
      };
      while ((match = re.exec(html))) {
        add(html.slice(cursor, match.index))(match[1], true);
        cursor = match.index + match[0].length;
      }
      add(html.substr(cursor, html.length - cursor));
      code += 'return r.join("");';
      L.FixMyStreet.Template._cache[html] = new Function(code.replace(/[\r\t\n]/g, ''));
    }
    try {
      var result = L.FixMyStreet.Template._cache[html].apply(options, [options]);
      if (typeof done === 'function') {
        return done(null, result);
      } else {
        return {error: null, result: result};
      }
    } catch (error) {
      if (typeof done === 'function') {
        return done(error, null);
      }
      console.error("ERROR: '" + error.message + "'", " in \n\nCode:\n", code, "\n");
      return {error: error, result: null};
    }
  },
};


// MAP =========================================================================

L.FixMyStreet.Map = L.Map.extend({
  options: {
    animate: true,
    center: [50.84535101789271, 4.351873397827148],
    minZoom: 10,
    maxBounds: [
      [50.95323634832283, 4.7618865966796875],
      [50.736455137010665, 3.9420318603515625],
    ],
    //maxZoom: 18,  // Auto-detected
    zoom: 14,

    cssSizePrefix: 'fmsmap-size-',
    cssSizeRegex: /(^|\s)fmsmap-size-\S+/g,
    cssClasses: {
      button: 'fmsmap-button',
      buttonLocateOnMap: 'fmsmap-button-locateonmap',
      buttonSize: 'fmsmap-button-size',
      buttonStreetView: 'fmsmap-button-streetview',
      control: 'leaflet-control',
      controlButtons: 'fmsmap-control-buttons',
      panel: 'fmsmap-panel',
      panelSearch: 'fmsmap-panel-search',
    },
    controlsPosition: {
      attribution: 'bottomleft',
      buttons: 'bottomright',
      panels: 'bottomright',
      incident: 'bottomleft',
      layer: 'topright',
      opacitySlider: 'topleft',
      incidentType: 'bottomleft',
    },
    controlsLabel: {  // this.options.controlsLabel.
      locateOnMap: gettext('Locate on map'),
      streetView: 'Street View',
      sizeToggleExpand: gettext('Expand'),
      sizeToggleReduce: gettext('Reduce'),
    },
    overviewZoom: 12,
    newIncidentZoom: 17,
    newIncidentUrl: NEW_INCIDENT_URL,

    myLayers: {  // @TODO: Rename variable.
      'map-street': {
        visible: true,
        settings: L.FixMyStreet.UrbisLayersSettings['map-street-' + LANGUAGE_CODE],
      },
      'map-ortho': {
        visible: false,
        overlay: true,  // Make it an overlay...
        opacityControl: true,  // ... with an opacity slider
        settings: L.FixMyStreet.UrbisLayersSettings['map-ortho'],
      },
      'municipal-boundaries': {
        visible: false,
        settings: L.FixMyStreet.UrbisLayersSettings['municipal-boundaries'],
      },
      'regional-roads': {
        visible: false,
        settings: L.FixMyStreet.UrbisLayersSettings['regional-roads'],
      },
      // 'street-names': {  // @TODO: Not working well.
      //   visible: false,
      //   settings: L.FixMyStreet.UrbisLayersSettings['street-names'],
      // },
      // 'street-numbers': {  // @TODO: Not working.
      //   visible: false,
      //   settings: L.FixMyStreet.UrbisLayersSettings['street-numbers'],
      // },
    },

    incidentTypes: {
      reported: {
        title: gettext('Created'),
        color: '#c3272f',
        controlTitle: '<span class="type-reported"><img src="' + STATIC_URL + 'images/marker-red-xxs.png" />' + gettext('Created') + '</span>',
      },
      ongoing: {
        title: gettext('In progress'),
        color: '#f79422',
        controlTitle: '<span class="type-ongoing"><img src="' + STATIC_URL + 'images/marker-orange-xxs.png" />' + gettext('In progress') + '</span>',
      },
      closed: {
        title: gettext('Closed'),
        color: '#3cb64b',
        controlTitle: '<span class="type-closed"><img src="' + STATIC_URL + 'images/marker-green-xxs.png" />' + gettext('Closed') + '</span>',
      },
      other: {
        title: gettext('Other'),
        color: '#9b9b9b',
        controlTitle: '<span class="type-other"><img src="' + STATIC_URL + 'images/marker-gray-xxs.png" />' + gettext('Other') + '</span>',
        filtering: false,
      },
    },
  },

  initialize: function (id, options) {  // (HTMLElement or String, [Object])
    options = $.extend(true, {}, this.options, options);
    L.Map.prototype.initialize.call(this, id, options);

    // Leaflet handles only if both center and zoom are defined.
    if (this.options.center && this.options.zoom !== undefined) {
      // Handled by Leaflet
    } else if (this.options.zoom !== undefined) {
      this.setZoom(this.options.zoom);
    } else if (this.options.center) {
      this.panTo(L.latLng(this.options.center));
    }

    this.$container = $(this._container);
    this.incidents = {};
    for (var k in this.options.incidentTypes) {
      this.incidents[k] = [];
    }
    this.newIncidentMarker = null;
    this.opacitySlider = null;

    this._initLayers();
    this._initControls();
    this._initPopups();
  },

  // INCIDENTS -----------------------------------------------------------------

  addIncident: function (model, options) {  // (Object, [Object])
    var isNew = model.type === 'new';
    if (!isNew && !(model.type in this.incidents)) {
      throw new TypeError('Invalid incident type (' + model.type + ').');
    }
    if (isNew && this.newIncidentMarker !== null) {
      throw new Error('New incident marker already present, remove it first.');
    }

    var that = this;
    var container = isNew ? this : this._incidentLayer;

    var marker = this._markerFactory(model, options);

    marker.addTo(container);
    if (isNew) {
      this.newIncidentMarker = marker;
      this.setView(marker.getLatLng(), this.options.newIncidentZoom, {animate: true});
    } else {
      this.incidents[model.type].push(marker);
    }

    return marker;
  },

  addIncidentsFromGeoJson: function (data, baseOptions, next) {  // (String or Object, [Object], [Function])
    if (typeof data === 'string') {
      this._addIncidentsFromGeoJsonUrl(data, baseOptions, next);
    } else {
      this._addIncidentsFromGeoJson(data, baseOptions, next);
    }
  },

  removeAllIncidents: function () {
    this._incidentLayer.clearLayers();
    for (var k in this.incidents) {
      while (this.incidents[k].length > 0) {  // See http://stackoverflow.com/a/1232046/101831
        this.incidents[k].pop();
      }
    }
  },

  removeNewIncident: function () {
    if (!this.newIncidentMarker) { return; }
    this.removeLayer(this.newIncidentMarker);
    this.newIncidentMarker = null;
  },

  toggleIncidentType: function (type, visibility) {  // (String, [Boolean])
    if (!(type in this.incidents)) {
      throw new TypeError('Invalid incident type (' + type + ').');
    }
    var that = this;
    $.each(this.incidents[type], function (i, layer) {
      if (visibility) {
        layer.addTo(that._incidentLayer);
      } else {
        that._incidentLayer.removeLayer(layer);
      }
    });
  },

  _addIncidentsFromGeoJson: function (geoJson, baseOptions, next) {  // (Object, [Object], [Function])
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
    next();
  },

  _addIncidentsFromGeoJsonUrl: function (url, baseOptions, next) {  // (String, [Object], [Function])
    var that = this;
    if (DEBUG) { console.log('Loading GeoJSON from %s...', url); }
    $.get(url, function (geoJson) {
      if (DEBUG) { console.log('GeoJSON received from %s...', url); }
      that._addIncidentsFromGeoJson(geoJson, baseOptions, next);
    }).fail(function() {
      throw new Error('Failed to load GeoJSON from ' + url + ': ' + argument);
    });
  },

  // SEARCH -----------------------------------------------------------------

  addSearchResult: function (model, options) {  // (Object, [Object])
    var latlng = L.FixMyStreet.Util.toLatLng(model.latlng) || this.getCenter();
    var marker = new L.FixMyStreet.SearchResultMarker(latlng, options, model);
    marker.addTo(this._searchLayer);
    this.searchResults.push(marker);
  },

  addSearchResults: function (models, options) {  // (Object, [Object])
    var that = this;
    this.initSearchLayer();
    $.each(models, function (i, model) {
      that.addSearchResult(model, options);
    });
    this.fitToMarkers(this._searchLayer);

    options = $.extend(true, {
      position: this.options.controlsPosition.panels,
    }, options);
    this.searchPanel = new L.FixMyStreet.SearchPanel(options);
    this.searchPanel.addTo(this);
  },

  removeSearchResults: function () {
    if (this._searchLayer === undefined) { return; }
    this._searchLayer.clearLayers();
    this.searchPanel.remove();
    while (this.searchResults.length > 0) {  // See http://stackoverflow.com/a/1232046/101831
      this.searchResults.pop();
    }
  },

  // CONTROLS ------------------------------------------------------------------
  // @TODO: Refactor controls (filters, buttons, toggles) as L.FixMyStreet.*Control

  addButton: function (options) {  // ([Object])
    options = $.extend({
      position: this.options.controlsPosition.buttons,
      prepend: true,
    }, options);

    var that = this;
    var $container = this._getButtonsContainer();

    var $btn = $('<a />');
    $btn.html(options.label);
    if (options.attr) {
      $btn.attr(options.attr);
    }
    $btn.addClass(this.options.cssClasses.button);
    if (options.cls) {
      $btn.addClass(options.cls);
    }

    if (options.prepend === true) {
      $container.prepend($btn);
    } else {
      $container.append($btn);
    }

    return $btn;
  },

  addLocateOnMapButton: function (options) {  // ([Object])
    var that = this;

    options = $.extend({
      label: this.options.controlsLabel.locateOnMap,
    }, options);

    var buttonOptions = this._prepareButtonOptions({
      cls: this.options.cssClasses.buttonLocateOnMap,
    }, options);
    var $btn = this.addButton(buttonOptions);

    $btn.click(function (evt) {
      that._locateOnMapButton_onClick(evt);
    });

    return $btn;
  },

  addStreetViewButton: function (options) {  // ([Object])
    var that = this;

    options = $.extend({
      label: this.options.controlsLabel.streetView,
      //latlng: this.getCenter(),  // This fixes the latlng when the button is added. If undefined, latlng = map.center when clicking.
    }, options);

    var buttonOptions = this._prepareButtonOptions({
      cls: this.options.cssClasses.buttonStreetView,
    }, options);
    var $btn = this.addButton(buttonOptions);

    $btn.click(function (evt) {
      that._streetViewButton_onClick(evt, options.latlng);
    });

    return $btn;
  },

  addSizeToggle: function (options) {  // ([Object])
    var that = this;

    options = $.extend(true, {
      state1: {
        label: this.options.controlsLabel.sizeToggleExpand,
        size: 'medium',
      },
      state2: {
        label: this.options.controlsLabel.sizeToggleReduce,
        size: 'large',
      },
    }, options);

    var buttonOptions = this._prepareButtonOptions({
      label: options.state1.label,
      cls: this.options.cssClasses.buttonSize + ' size-' + options.state1.size + ' size-to-' + options.state2.size,
    }, options);
    var $btn = this.addButton(buttonOptions);

    $btn.click(function (evt) {
      that._sizeToggle_onClick(evt, $(this), options);
    });

    this.setCssSize(options.state1.size);

    return $btn;
  },

  addIncidentTypeControl: function (options) {  // ([Object])
    var that = this;
    options = $.extend(true, {
      position: this.options.controlsPosition.incidentType,
    }, options);

    var $container = this._getButtonsContainer();

    var $panel = $('<div/>').addClass('leaflet-control fmsmap-panel fmsmap-panel-incident-filter');
    $panel.append($('<div/>').addClass('fmsmap-panel-header').html(gettext('Incident filter')));
    var $body = $('<div/>').addClass('fmsmap-panel-body');
    $.each(this.options.incidentTypes, function (k, v) {
      if (v.filtering === false) { return; }
      var $input = $('<input type="checkbox" value="' + k + '" checked />');
      var $e = $('<label class="type-' + k +'">' + v.controlTitle + '</label>');
      $input.change(function (evt) {
        var $this = $(this);
        that.toggleIncidentType($this.val(), $this.prop('checked'));
      });
      $body.append($e.prepend($input));
    });
    $panel.append($body);

    this.insertByPosition(this.getLeafletCorner(options.position), $panel, options.position);

    $panel.find('input[type="checkbox"]').click(function (evt) {
    });
  },

  _prepareButtonOptions: function (buttonOptions, options) {  // ([Object], [Object])
    buttonOptions = buttonOptions || {};
    if (options !== undefined) {
      buttonOptions = $.extend({
        position: options.position,
        label: options.label,
        prepend: options.prepend,
      }, buttonOptions);
    }
    return buttonOptions;
  },

  // INIT ----------------------------------------------------------------------

  initSearchLayer: function () {
    if (this._searchLayer !== undefined) { return; }
    this._searchLayer = new L.FeatureGroup();
    this._searchLayer.addTo(this);
    this.searchResults = [];
  },

  _initLayers: function() {
    var that = this;
    $.each(this.options.myLayers, function (k, v) {
      v._layer = that._layerFactory(v.settings);
      if (v.visible === true) {
        that.addLayer(v._layer);
      }
      if (v.opacityControl === true) {
        that._initOpacityControl(v._layer);
      }
    });

    this._initIncidentLayer();
  },

  _initIncidentLayer: function () {
    if (this._incidentLayer !== undefined) { return; }
    var that = this;
    this._incidentLayer = new L.MarkerClusterGroup();
    this._incidentLayer.on('clusterclick', function (evt) {
      that._cluster_onClick(evt);
    });
    this._incidentLayer.addTo(this);
  },

  _initControls: function() {
    if (this.options.controlsPosition.attribution !== undefined) {
      this.attributionControl.setPosition(this.options.controlsPosition.attribution);
    }

    this._initLayerControl();
  },

  _initLayerControl: function() {
    var that = this;
    var baseLayers = {};
    var baseLayersCount = 0;
    var overlays = {};
    var options = {
      collapsed: true,
      position: this.options.controlsPosition.layer,
    };

    $.each(this.options.myLayers, function (k, v) {
      var title = that.getLayerTitleForControl(v);
      if (that.isOverlayLayer(v)) {
        overlays[title] = v._layer;
      } else {
        baseLayers[title] = v._layer;
        baseLayersCount++;
      }
    });

    if (baseLayersCount < 2) {
      baseLayers = null;
    }

    L.control.layers(baseLayers, overlays, options).addTo(this);
  },

  getLayerTitleForControl: function(layer) {
    return layer.controlTitle || layer.title || layer.settings.title;
  },

  isOverlayLayer: function(layer) {
    return layer.overlay === true || (layer.overlay === undefined && layer.settings.overlay === true);
  },

  _initOpacityControl: function (layer) {  // (L.ILayer)
    if (this.opacitySlider !== null) {
      throw new Error('Opacity slider already initialized.');
    }

    var that = this;
    this.opacitySlider = new L.Control.opacitySlider({position: this.options.controlsPosition.opacitySlider});
    layer.setOpacity(0.6);  // Default value in `L.Control.opacitySlider`.
    this.opacitySlider.setOpacityLayer(layer);

    this.on('overlayadd', function (evt) {
      if (evt.layer === layer) {
        that.addControl(that.opacitySlider);
      }
    });
    this.on('overlayremove', function (evt) {
      if (evt.layer === layer) {
        that.removeControl(that.opacitySlider);
      }
    });
  },

  _initPopups: function() {
    var that = this;
    this.on('popupopen', function(evt) {
      window.setTimeout(function () {  // Use timeout to wait that any previous "pan" is finished.
        evt.popup.saveDimensions();
        that.panBy([0, -(evt.popup._dimensions.height / 2)]);
      }, 500);
    });
    this.on('popupclose', function(evt) {
      window.setTimeout(function () {  // Use timeout to wait that any previous "pan" is finished.
        if (evt.popup.autoPanDisabled === true) { return; }
        that.panBy([0, (evt.popup._dimensions.height / 2)]);
      }, 500);
    });
  },

  _getButtonsContainer: function () {
    var $e = this.$container.find('.' + this.options.cssClasses.controlButtons);
    if ($e.length === 0) {
      $e = $('<div/>').addClass(this.options.cssClasses.control + ' ' + this.options.cssClasses.controlButtons);
      var position = this.options.controlsPosition.buttons;
      this.insertByPosition(this.getLeafletCorner(position), $e, position);
    }
    return $e;
  },

  // EVENT HANDLERS ------------------------------------------------------------

  _locateOnMapButton_onClick: function (evt) {  // locateOnMapButton.click
    this.addIncident({type: 'new'});
  },

  _streetViewButton_onClick: function (evt, latlng) {  // streetViewButton.click
    L.FixMyStreet.Util.openStreetView(latlng);
  },

  _sizeToggle_onClick: function (evt, $e, options) {  // sizeToggle.click
    var currentState = $e.data('state') || 1;
    var nextState = currentState == 2 ? 1 : 2;
    var opts = options['state' + nextState];
    this.setCssSize(opts.size);
    $e.html(opts.label);
    $e.removeClass('size-' + options['state' + currentState].size);
    $e.removeClass('size-to-' + options['state' + nextState].size);
    $e.addClass('size-' + opts.size);
    $e.addClass('size-to-' + options['state' + currentState].size);
    $e.data('state', nextState);
  },

  _cluster_onClick: function (evt) {  // layer.clusterclick
  },

  // HELPERS -------------------------------------------------------------------

  fitToMarkers: function (layer) {  // ([L.Layer])
    layer = layer || this._incidentLayer;
    this.fitBounds(layer.getBounds().pad(0.5));
  },

  centerOnLayer: function (layer, zoom) {  // (L.Layer, [Integer])
    var center = layer.getBounds().getCenter();
    if (zoom === undefined) {
      this.panTo(center);
    } else {
      this.setView(center, zoom, {animate: true});
    }
  },

  centerOnMarker: function (marker) {  // (Object)
    // @TODO: Check if popup is opened and adapt LatLng accordingly.
    this.panTo(marker.getLatLng());
  },

  setCssSize: function (cls) {  // (String)
    var that = this;
    this.$container.removeClass(function (index, css) {
      return (css.match(that.options.cssSizeRegex) || []).join(' ');
    });
    if (cls) {
      this.$container.addClass(this.options.cssSizePrefix + cls);
    }
    this.invalidateSize(this.options.animate);
  },

  getLeafletCorner: function (position) {  // (String)
    var corner = this._controlCorners[position];
    if (corner === undefined) {
      throw new TypeError('Invalid position (' + position + ').');
    }
    return $(corner);
  },

  insertByPosition: function ($container, $e, position, reference) {  // ($Element, $Element, String, String)
    reference = reference || 'bottom';
    if (position.indexOf(reference) !== -1) {
      $container.prepend($e);
    } else {
      $container.append($e);
    }
  },

  _layerFactory: function(settings) {  // (Object)
    switch (settings.type) {
      case 'wms': return L.tileLayer.wms(settings.url, settings.options);
      default: return L.tileLayer(settings.url, settings.options);
    }
  },

  _markerFactory: function(model, options) {  // (Object, Object)
    var marker;
    var latlng = L.FixMyStreet.Util.toLatLng(model.latlng) || this.getCenter();

    switch (model.type) {
      case 'new':
        if (model.url === undefined) {
          model.url = this.options.newIncidentUrl;
        }
        marker = new L.FixMyStreet.NewIncidentMarker(latlng, options, model);
        break;
      case 'reported':
        marker = new L.FixMyStreet.ReportedIncidentMarker(latlng, options, model);
        break;
      case 'ongoing':
        marker = new L.FixMyStreet.OngoingIncidentMarker(latlng, options, model);
        break;
      case 'closed':
        marker = new L.FixMyStreet.ClosedIncidentMarker(latlng, options, model);
        break;
      case 'other':
        marker = new L.FixMyStreet.OtherIncidentMarker(latlng, options, model);
        break;
      default: throw new TypeError('Invalid marker type (' + model.type + ').');
    }

    return marker;
  },

  _toggleLayer: function (layer, visibility) {  // (String, Boolean)
    // @TODO: Isn't there a better way?
    if (typeof layer !== undefined) {
      layer.toggle(visibility);
    } else if (typeof layer.getContainer !== undefined) {
      $(layer.getContainer()).toggle(visibility);
    } else {
      $(layer).toggle(visibility);
    }
  },
});


// CONTROLS ====================================================================

/* @TODO
See: http://gis.stackexchange.com/questions/60576/custom-leaflet-controls

L.FixMyStreet.Control = L.FixMyStreet.Control || {};


L.FixMyStreet.Control.Toggle = L.Control.extend({
  onAdd: function (map) {
    ...
  },
});


L.FixMyStreet.Control.toggle = function (options) {
  return new L.FixMyStreet.Control.Toggle(options);
};
*/


// ICONS =======================================================================

L.FixMyStreet.Icon = L.Icon.extend({
  options: {
    iconUrl: STATIC_URL + 'images/pin-fixmystreet-L.png',
    iconAnchor: [20, 52],
    popupAnchor: [0, -35],
  },
});


L.FixMyStreet.NewIncidentIcon = L.FixMyStreet.Icon.extend({});


L.FixMyStreet.ReportedIncidentIcon = L.FixMyStreet.Icon.extend({
  options: {
    iconUrl: STATIC_URL + 'images/pin-red-L.png',
  },
});


L.FixMyStreet.OngoingIncidentIcon = L.FixMyStreet.Icon.extend({
  options: {
    iconUrl: STATIC_URL + 'images/pin-orange-L.png',
  },
});


L.FixMyStreet.ClosedIncidentIcon = L.FixMyStreet.Icon.extend({
  options: {
    iconUrl: STATIC_URL + 'images/pin-green-L.png',
  },
});


L.FixMyStreet.OtherIncidentIcon = L.FixMyStreet.Icon.extend({
  options: {
    iconUrl: STATIC_URL + 'images/pin-gray-L.png',
  },
});


L.FixMyStreet.NumberedIcon = L.FixMyStreet.Icon.extend({
  // Inspired by https://gist.github.com/comp615/2288108

  options: {
    iconUrl: STATIC_URL + 'images/pin-blue-XS.png',
    iconAnchor: [15, 40],
    popupAnchor: [0, -28],
    number: 'A',
    className: 'fmsmap-numbered-icon',
  },

  createIcon: function () {
    var div = document.createElement('div');

    var img = this._createImg(this.options.iconUrl);
    div.appendChild(img);

    var label = document.createElement('div');
    label.setAttribute('class', 'number');
    label.innerHTML = this.options.number;
    div.appendChild(label);

    this._setIconStyles(div, 'icon');
    return div;
  },
});


L.FixMyStreet.SearchResultIcon = L.FixMyStreet.NumberedIcon.extend({
  options: {
    className: 'fmsmap-search-result-icon',
  },

  createIcon: function () {
    var div = L.FixMyStreet.NumberedIcon.prototype.createIcon.call(this);
    var $div = $(div);
    $div.attr('data-search-result', this.options.number);  // Doesn't work with .data('search-result')
    $div.mouseover(function (evt) {
      $('.fmsmap-panel-search').find('[data-search-result="' + $(this).data('search-result') + '"]').addClass('hover');
    });
    $div.mouseout(function (evt) {
      $('.fmsmap-panel-search').find('[data-search-result="' + $(this).data('search-result') + '"]').removeClass('hover');
    });
    return div;
  },
});


// MARKERS =====================================================================

L.FixMyStreet.Marker = L.Marker.extend({
  initialize: function (latlng, options, model) {  // (L.LatLng, [Object], [Object])
    var that = this;

    L.setOptions(this, options);
    L.Marker.prototype.initialize.call(this, latlng, options);

    this.$container = $(this._container);
    this.model = model || {};

    if (this.options.iconOptions) {
      L.setOptions(this.options.icon, this.options.iconOptions);
    }
    if (this.options.popup || this.options.popupTemplate) {
      this.options.popup.attachMarker(this);
      this.bindPopup(this.options.popup, this.options.popupOptions);
    }
    if (this.options.draggable) {
      this.on('dragstart', function (evt) {
        that._onDragStart(evt);
      });
      this.on('dragend', function (evt) {
        that._onDragEnd(evt);
      });
    }
    this.on('click', function (evt) {
      that._onClick(evt);
    });
  },

  getMap: function() {
    if (!this._map) {
      throw new Error('Marker is not visible on map, probably in a closed cluster.');
    }
    return this._map;
  },

  toggle: function (visibility) {  // ([Boolean])
    $(this._icon).toggle(visibility);  // @TODO: Isn't there a better way?
  },

  openPopup: function (latlng) {  // ([L.LatLng])
    if (!this._popup) { return; }
    this._popup.renderContent(this.model);
    L.Marker.prototype.openPopup.call(this, latlng);
    return this;
  },

  updatePopup: function () {
    this.closePopup();
    this.openPopup();
    return this;
  },

  // EVENT HANDLERS ------------------------------------------------------------

  _onClick: function (evt) {  // click
    this.centerMap();
  },

  _onDragStart: function (evt) {  // dragstart
  },

  _onDragEnd: function (evt) {  // dragend
    var marker = evt.target;
    var latlng = marker.getLatLng();
    marker.setLatLng(latlng);
    if (marker._map) {
      marker._map.panTo(latlng);
    }
  },

  // HELPERS -------------------------------------------------------------------

  centerMap: function() {
    this.getMap().centerOnMarker(this);
  },

  openStreetView: function() {
    var url = L.FixMyStreet.Util.getStreetViewUrl(this.getLatLng());
    window.open(url, '_blank');
  },
});


L.FixMyStreet.SearchResultMarker = L.FixMyStreet.Marker.extend({
  options: {
    icon: new L.FixMyStreet.SearchResultIcon(),
  },

  initialize: function (latlng, options, model) {  // (L.LatLng, [Object], [Object])
    model = model || {};
    if (model.number !== undefined) {
      this.options.iconOptions = this.options.iconOptions || {};
      this.options.iconOptions.number = model.number;
    }
    options = options || {};
    if (options.popup === undefined) {
      options.popup = new L.FixMyStreet.SearchResultPopup(options.popupOptions, this);
    }
    L.FixMyStreet.Marker.prototype.initialize.call(this, latlng, options, model);
  },
});


L.FixMyStreet.IncidentMarker = L.FixMyStreet.Marker.extend({
  initialize: function (latlng, options, model) {  // (L.LatLng, [Object], [Object])
    options = options || {};
    if (options.popup === undefined) {
      options.popup = this._popupFactory(options.popupOptions);
    }
    L.setOptions(this, options);
    L.FixMyStreet.Marker.prototype.initialize.call(this, latlng, options, model);
  },

  _popupFactory: function(options) {  // ([Object])
      return new L.FixMyStreet.IncidentPopup(options, this);
  },
});


L.FixMyStreet.NewIncidentMarker = L.FixMyStreet.IncidentMarker.extend({
  options: {
    draggable: true,
    icon: new L.FixMyStreet.NewIncidentIcon({
      popupAnchor: [0, -43],
    }),
  },

  initialize: function (latlng, options, model) {  // (L.LatLng, [Object], [Object])
    L.FixMyStreet.IncidentMarker.prototype.initialize.call(this, latlng, options, model);
    this._dragged = false;
  },

  onAdd: function (map) {  // (L.Map)
    var that = this;
    L.FixMyStreet.IncidentMarker.prototype.onAdd.call(this, map);
    window.setTimeout(function () { that.openPopup(); }, 250);  // @TODO: Workaround, otherwise LocateOnMap doesn't work.
  },

  _onDragStart: function (evt) {  // dragend
    var that = evt.target;
    that._dragged = true;
    that.getPopup().autoPanDisabled = true;  // @TODO: Isn't there a better way?
  },

  _onDragEnd: function (evt) {  // dragend
    var that = evt.target;
    var latlng = that.getLatLng();
    // @TODO: Not working. See L.FixMyStreet.NewIncidentPopup.activate()
    // if (that._dragged) {
    //   that.getPopup().activate();
    // }
    that.setLatLng(latlng);
    if (that._map) {
      that._map.panTo(latlng);
    }
    that.openPopup();
    that.getPopup().autoPanDisabled = false;  // @TODO: Isn't there a better way?
    if (that._dragged) {  // @TODO: Workaround, see above.
      that.getPopup().activate();
    }
    this._updateAddress();
  },

  _updateAddress: function() {
    var that = this;
    L.FixMyStreet.Util.getAddressFromLatLng(this.getLatLng(), function (address) {
      that.getPopup().updateAddress(address);
    });
  },

  _popupFactory: function(options) {  // ([Object])
    return new L.FixMyStreet.NewIncidentPopup(options, this);
  },
});


L.FixMyStreet.ReportedIncidentMarker = L.FixMyStreet.IncidentMarker.extend({
  options: {
    icon: new L.FixMyStreet.ReportedIncidentIcon(),
  },
});


L.FixMyStreet.OngoingIncidentMarker = L.FixMyStreet.IncidentMarker.extend({
  options: {
    icon: new L.FixMyStreet.OngoingIncidentIcon(),
  },
});


L.FixMyStreet.ClosedIncidentMarker = L.FixMyStreet.IncidentMarker.extend({
  options: {
    icon: new L.FixMyStreet.ClosedIncidentIcon(),
  },
});


L.FixMyStreet.OtherIncidentMarker = L.FixMyStreet.IncidentMarker.extend({
  options: {
    icon: new L.FixMyStreet.OtherIncidentIcon(),
  },
});


// POP-UPS =====================================================================

L.FixMyStreet.Popup = L.Popup.extend({
  options: {
    partialTemplateRegex: /^_.*_$/,
    templates: {
      base:
        '<div class="fmsmap-popup">' +
          '{_header_}' +
          '<div class="fmsmap-popup-body">{_body_}</div>' +
          '{_footer_}' +
        '</div>',
      _header_: '',  // <div class="fmsmap-popup-header">...</div>
      _footer_: '',  // <div class="fmsmap-popup-footer">...</div>
      _body_: '',
      _address_:
        '<% if (this.address) { %>' +
          '<% this.address.street %> <% this.address.number %><br />' +
          '<% this.address.postalCode %> <% this.address.city %>' +
        '<% } %>',
    }
  },

  initialize: function (options, source) {  // ([Object], [L.ILayer])
    L.FixMyStreet.Util.mergeExtendedOptions(this);
    L.setOptions(this, options);
    L.Popup.prototype.initialize.call(this, options, source);

    if (this._container) {
      this.$container = $(this._container);
    }
    this._marker = null;
  },

  onAdd: function (map) {  // (L.Map)
    L.Popup.prototype.onAdd.call(this, map);
    if (this.$container === undefined && this._container) {
      this.$container = $(this._container);
    }
    this._bindActions();
  },

  attachMarker: function (marker) {  // (L.Marker)
    this._marker = marker;
  },

  detachMarker: function () {
    this._marker = null;
  },

  renderContent: function(data, key) {  // ([Object], [String])
    var that = this;
    this._render(data, key, function (error, html) {
      if (!error) {
        that.setContent(html);
        that.saveDimensions();
        that.fire('popuprendered', {popup: that});
      }
    });
  },

  updateAddress: function (address) {
    var that = this;
    this._renderTemplate(this.options.templates._address_, {address: address}, function (error, html) {
      if (!error) {
        that.$container.find('.address').html(html);
      }
    });
  },

  saveDimensions: function () {
    this._dimensions = {
      height: this._container.clientHeight,
      width: this._container.clientWidth,
    };
    return this;
  },

  _bindActions: function (handlers) {
    if (!this._marker) { return; }
    if (!this._container) { return; }
    var that = this;

    $(this._container).find('[data-bind]').each(function (i, e) {
      var $this = $(this);
      var action = $this.data('bind');

      if (handlers !== undefined && handlers[action]) {
        $this.click(handlers[action]);
      } else {
        switch (action) {
          case 'center-map':
            $this.click(function (evt) {
              evt.preventDefault();
              that._marker.centerMap();
            });
            break;
          case 'street-view':
            $this.click(function (evt) {
              evt.preventDefault();
              that._marker.openStreetView();
            });
            break;
          case 'new-incident':
            $this.click(function (evt) {
              evt.preventDefault();
              that.removeNewIncident();
              that.addIncident({
                type: 'new',
                latlng: that._marker.getLatLng(),
              });
            });
            break;
          default:
            console.error('ERROR: Unknown bind type (%s).', $this.data('bind'));
        }
      }
    });
  },
});
L.FixMyStreet.Popup.include(L.FixMyStreet.Template);


L.FixMyStreet.SearchResultPopup = L.FixMyStreet.Popup.extend({
  extendedOptions: {
    templates: {
      base:
        '<div class="fmsmap-popup new">' +
          '<div class="fmsmap-popup-header clearfix">{_header_}</div>' +
          '<div class="fmsmap-popup-body clearfix">{_body_}</div>' +
          '<div class="fmsmap-popup-footer clearfix">{_footer_}</div>' +
        '</div>',
      _header_:
        gettext('Search result <% this.number %>'),
      _body_:
        '<p class="address">{_address_}</p>',
      _footer_:
        '<div class="pull-left">' +
          '<a href="#" data-bind="street-view" title="' + gettext('Open Street View') + '"><i class="icon-streetview"></i></a>' +
          '<a href="#" data-bind="center-map" title="' + gettext('Center map') + '"><i class="icon-localizeviamap"></i></a>' +
        '</div>' +
        '<div class="pull-right">' +
          '<% if (this.url) { %>' +
            '<a class="button" href="<% this.url %>">' + gettext('Go') + '</a>' +
          '<% } else { %>' +
            '<a class="button" href="#" data-bind="new-incident">' + gettext('New incident') + '</a>' +
          '<% } %>' +
        '</div>',
    },
  },

  initialize: function (options, source) {  // ([Object], [L.ILayer])
    L.FixMyStreet.Util.mergeExtendedOptions(this);
    L.setOptions(this, options);
    L.FixMyStreet.Popup.prototype.initialize.call(this, options, source);
  },

  _bindActions: function (handlers) {
    var that = this;
    var theseHandlers = {};
    theseHandlers['new-incident'] = function (evt) {
      evt.preventDefault();
      var map = that._map;
      map.removeSearchResults();
      var model = {
        type: 'new',
        latlng: that._marker.model.latlng,
        address: that._marker.model.address,
      };
      map.addIncident(model);
    };
    handlers = $.extend(true, {}, theseHandlers, handlers);
    L.FixMyStreet.Popup.prototype._bindActions.call(this, handlers);
  },
});


L.FixMyStreet.NewIncidentPopup = L.FixMyStreet.Popup.extend({
  extendedOptions: {
    templates: {
      base:
        '<div class="fmsmap-popup new">' +
          '<div class="fmsmap-popup-header clearfix">{_header_}</div>' +
          '<div class="fmsmap-popup-body clearfix">{_body_}</div>' +
          '<div class="fmsmap-popup-footer clearfix hidden">{_footer_}</div>' +
        '</div>',
      _header_:
        gettext('Place me at the exact position of the incident'),
      _body_:
        '<p class="address">{_address_}</p>',
      _footer_:
        '<div class="pull-left">' +
          '<a href="#" data-bind="street-view" title="' + gettext('Open Street View') + '"><i class="icon-streetview"></i></a>' +
          '<a href="#" data-bind="center-map" title="' + gettext('Center map') + '"><i class="icon-localizeviamap"></i></a>' +
        '</div>' +
        '<div class="pull-right">' +
          '<a class="button button-itshere" href="#" data-bind="itshere">' + gettext('It\'s here') + '</a>' +
        '</div>',
    },
  },

  initialize: function (options, source) {  // ([Object], [L.ILayer])
    L.FixMyStreet.Util.mergeExtendedOptions(this);
    L.setOptions(this, options);
    L.FixMyStreet.Popup.prototype.initialize.call(this, options, source);
    this._activated = false;
  },

  activate: function () {
    if (this._activated) { return; }
    this._activated = true;
    // @TODO: Not working. See L.FixMyStreet.NewIncidentMarker._onDragEnd()
    // this.on('popuprendered', function (data) {
    //   data.popup.$container.find('.button-itshere').removeClass('hidden');
    // });
    this.$container.find('.fmsmap-popup-footer').removeClass('hidden');  // @TODO: Workaround, see above.
  },

  _bindActions: function (handlers) {
    var that = this;
    var theseHandlers = {};
    theseHandlers['itshere'] = function (evt) {
      var point = L.FixMyStreet.Util.toUrbisCoords(that._marker.getLatLng());
      var url = that._marker.model.url + '?x=' + point.x + '&y=' + point.y;
      $(this).attr('href', url);
    };
    handlers = $.extend(true, {}, theseHandlers, handlers);
    L.FixMyStreet.Popup.prototype._bindActions.call(this, handlers);
  },
});


L.FixMyStreet.IncidentPopup = L.FixMyStreet.Popup.extend({
  extendedOptions: {
    templates: {
      base:
        '<div class="fmsmap-popup">' +
          '<div class="fmsmap-popup-header clearfix">{_header_}</div>' +
          '<div class="fmsmap-popup-body clearfix">{_body_}</div>' +
          '<div class="fmsmap-popup-footer clearfix">{_footer_}</div>' +
        '</div>',
      _header_:
        gettext('Report #<% this.id %>'),
      _body_:
        '<div class="pull-left">' +
          '<% if (this.address) { %>' +
            '<p class="address">{_address_}</p>' +
          '<% } %>' +
          '<% if (this.categories) { %>' +
            '<p class="categories"><% this.categories %></p>' +
          '<% } %>' +
        '</div>' +
        '<% if (this.photo) { %>' +
          '<div class="pull-right">' +
            '<img class="photo" src="<% this.photo %>" alt="" />' +
          '</div>' +
        '<% } %>',
      _footer_:
        '<% if (this.icons) { %>' +
          '<div class="pull-left">' +
            '<ul class="icons inline">' +
              '<% if (this.icons.regionalRoads !== undefined) { %><li><img src="' + STATIC_URL + '/images/regional_<% (this.icons.regionalRoads ? "on" : "off") %>.png" title="' + gettext('This incident is located on a regional zone') + '"></li><% } %>' +
              '<% if (this.icons.pro !== undefined) { %><li><img src="' + STATIC_URL + '/images/pro_<% (this.icons.pro ? "on" : "off") %>.png" title="' + gettext('This incident has been signaled by a pro') + '"></li><% } %>' +
              '<% if (this.icons.assigned !== undefined) { %><li><img src="' + STATIC_URL + '/images/contractorAssigned_<% (this.icons.assigned ? "on" : "off") %>.png" title="' + gettext('This incident is assigned to') + '"></li><% } %>' +
              '<% if (this.icons.resolved !== undefined) { %><li><img src="' + STATIC_URL + '/images/is_resolved_<% (this.icons.resolved ? "on" : "off") %>.png" title="' + gettext('This incident has been signaled as solved') + '"></li><% } %>' +
              '<% if (this.icons.priority !== undefined) { %>' +
                '<li><img src="' + STATIC_URL + '/images/prior_<% (this.icons.priority === 0 ? "off" : "on_" + this.icons.priority) %>.png" title="' +
                  '<% if (this.icons.priority === 0) { %>' + gettext('This incident has no defined priority') + '<% } %>' +
                  '<% else if (this.icons.priority === 1) { %>' + gettext('This incident has a low priority') + '<% } %>' +
                  '<% else if (this.icons.priority === 2) { %>' + gettext('This incident has a medium priority') + '<% } %>' +
                  '<% else if (this.icons.priority === 3) { %>' + gettext('This incident has a serious priority') + '<% } %>' +
                '"></li>' +
              '<% } %>' +
            '</ul>' +
          '</div>' +
        '<% } %>' +
        '<% if (this.url) { %>' +
          '<div class="pull-right">' +
            '<a class="button" href="<% this.url %>">' + gettext('Details') + '</a>' +
          '</div>' +
        '<% } %>',
    },
  },
});


// PANELS ======================================================================
// @TODO: Look for existing plugins.

L.FixMyStreet.Panel = L.Control.extend({
  _getContainer: function (map) {
    var $e = map.$container.find('.fmsmap-panel-container');
    if ($e.length === 0) {
      $e = $('<div/>').addClass('fmsmap-panel-container');
      map.$container.append($e);
    }
    return $e;
  },

  remove: function() {
    this.$container.remove();
  },

  setContent: function(html) {  // (String)
    this._container = $(html).get(0);
    this.$container = $(this._container);
    this._bindActions();
  },

  renderContent: function(data, key) {  // ([Object], [String])
    var that = this;
    this._render(data, key, function (error, html) {
      if (!error) {
        that.setContent(html);
      }
    });
  },

  _bindActions: function (handlers) {
    if (!this._container) { return; }
    var that = this;

    $(this._container).find('[data-bind]').each(function (i, e) {
      var $this = $(this);
      var action = $this.data('bind');

      if (handlers !== undefined && handlers[action]) {
        $this.click(handlers[action]);
      } else {
        switch (action) {
          case 'close':
            $this.click(function (evt) {
              evt.preventDefault();
              that.remove();
            });
            break;
          default:
            console.error('ERROR: Unknown bind type (%s).', $this.data('bind'));
        }
      }
    });
  },
});


L.FixMyStreet.SearchPanel = L.FixMyStreet.Panel.extend({
  extendedOptions: {
    templates: {
      base:
        '<div class="fmsmap-panel fmsmap-panel-search">' +
          '<div class="fmsmap-panel-header clearfix">' +
            '<button class="close" type="button" data-bind="close">&times;</button>' +
            '{_header_}' +
          '</div>' +
          '<div class="fmsmap-panel-body clearfix">{_body_}</div>' +
        '</div>',
      _header_:
        '<% if (this.results.length === 0) { %>' +
          gettext('No results') +
        '<% } else { %>' +
          gettext('<% this.results.length %> results') +
        '<% } %>',
      _body_:
        '<% if (this.results.length === 0) { %>' +
          '<p>' + gettext('No corresponding address has been found.') + '</p>' +
          '<p>' + gettext('Please refine your search criteria.') + '</p>' +
        '<% } else { %>' +
          '<ul>' +
            '<% for (var i in this.results) { %>' +
              '<li data-search-result="<% this.results[i].number %>">' +
                '<div class="number"><% this.results[i].number %></div>' +
                '<p class="address">' +
                  '<% this.results[i].address.street %> <% this.results[i].address.number %><br />' +
                  '<% this.results[i].address.postalCode %> <% this.results[i].address.city %>' +
                '</p>' +
              '</li>' +
            '<% } %>' +
          '</ul>' +
        '<% } %>',
    },
  },

  initialize: function (options, source) {  // ([Object], [L.ILayer])
    L.FixMyStreet.Util.mergeExtendedOptions(this);
    L.setOptions(this, options);
    L.Control.prototype.initialize.call(this, options, source);
  },

  addTo: function (map) {  // (L.Map)
    this._map = map;
    this.onAdd(map);
    $panelContainer = this._getContainer(map);
    $panelContainer.append(this.$container);
  },

  onAdd: function (map) {  // (L.Map)
    var that = this;

    var results = [];
    $.each(map.searchResults, function (i, marker) {
      results.push(marker.model);
    });
    this.renderContent({results: results});

    this.$container.mouseover(function (evt) {
      map.dragging.disable();
      map.touchZoom.disable();
      map.doubleClickZoom.disable();
      map.scrollWheelZoom.disable();
    });
    this.$container.mouseout(function (evt) {
      map.dragging.enable();
      map.touchZoom.enable();
      map.doubleClickZoom.enable();
      map.scrollWheelZoom.enable();
    });

    this.$container.find('li[data-search-result]').each(function (i, e) {
      var $e = $(e);
      $e.mouseover(function (evt) {
        $('.fmsmap-search-result-icon[data-search-result="' + $e.data('search-result') + '"]').addClass('hover');
      });
      $e.mouseout(function (evt) {
        $('.fmsmap-search-result-icon[data-search-result="' + $e.data('search-result') + '"]').removeClass('hover');
      });
      $e.click(function (evt) {
        that._map.removeNewIncident();
        that._map.addIncident({
          type: 'new',
          latlng: results[i].latlng,
          address: results[i].address,
        });
      });
    });

    return this._container;
  },

  _bindActions: function (handlers) {
    var that = this;
    var theseHandlers = {};
    theseHandlers['close'] = function (evt) {
      evt.preventDefault();
      that._map.removeSearchResults();
    };
    handlers = $.extend(true, {}, theseHandlers, handlers);
    L.FixMyStreet.Panel.prototype._bindActions.call(this, handlers);
  },
});

L.FixMyStreet.SearchPanel.include(L.FixMyStreet.Template);


// UTILS =======================================================================

L.FixMyStreet.Util = {
  mergeExtendedOptions: function(that) {  // @TODO: Isn't there a better way?
    if (that.extendedOptions !== undefined) {
      $.extend(true, that.options, that.extendedOptions);
      delete that.extendedOptions;
    }
  },

  /**
   * Converts a value into a `L.LatLng` object.
   *
   * @param {(L.LatLng|L.Point|string|object)} value - The value to convert.
   * @returns {L.LatLng} The converted value.
   * @throws {TypeError} If the value cannot be converted.
   */
  toLatLng: function (value) {
    if (value instanceof L.LatLng || value === undefined || value === null) {
      return value;
    }

    if (value instanceof L.Point) {
      return L.Projection.LonLat.unproject(value);
    }

    try {
      if (typeof value === 'string') {
        var chunks = value.split(/,\s*/);
        return new L.LatLng(parseFloat(chunks[0]), parseFloat(chunks[1]));
      }

      if (typeof value === 'object') {
        if ('lat' in value && 'lng' in value) {
          return new L.LatLng(parseFloat(value.lat), parseFloat(value.lng));
        }
        if ('x' in value && 'y' in value) {
          return L.Projection.LonLat.unproject(this.toPoint({x: value.x, y: value.y}));
        }
        if (0 in value && 1 in value) {
          return new L.LatLng(parseFloat(value[0]), parseFloat(value[1]));
        }
      }
    } catch (error) {
    }

    throw new TypeError('Invalid value (' + value + '). Expect L.LatLng or L.Point or String ("50.846,4.369") or Object ({lat: 50.846, lng: 4.369} or {x: 4.369, y: 50.846} or [50.846, 4.369]).');
  },

  /**
   * Converts a value into a `L.Point` object.
   *
   * @param {(L.Point|L.LatLng|string|object)} value - The value to convert.
   * @param {boolean} [prefLatLng=false] - Preference to LatLng format if value is index-based (i.e. "4.369,50.846" or [4.369, 50.846]).
   * @returns {L.Point} The converted value.
   * @throws {TypeError} If the value cannot be converted.
   */
  toPoint: function(value, prefLatLng) {
    prefLatLng = prefLatLng === undefined ? false : prefLatLng === true;

    if (value instanceof L.Point || value === undefined || value === null) {
      return value;
    }

    if (value instanceof L.LatLng) {
      return L.Projection.LonLat.project(value);
    }

    try {
      var x, y;
      if (typeof value === 'string') {
        var chunks = value.split(/,\s*/);
        if (prefLatLng) {
          x = chunks[1];
          y = chunks[0];
        } else {
          x = chunks[0];
          y = chunks[1];
        }
      } else if (typeof value === 'object') {
        if ('x' in value && 'y' in value) {
          x = value.x;
          y = value.y;
        } else if ('lat' in value && 'lng' in value) {
          return L.Projection.LonLat.project(this.toLatLng({lat: value.lat, lng: value.lng}));
        } else if (0 in value && 1 in value) {
          if (prefLatLng) {
            x = value[1];
            y = value[0];
          } else {
            x = value[0];
            y = value[1];
          }
        }
      }

      x = parseFloat(x);
      y = parseFloat(y);
      if (typeof x === 'number' && !isNaN(x) && typeof y === 'number' && !isNaN(y)) {
        return new L.Point(x, y);
      }
    } catch (error) {
    }

    throw new TypeError('Invalid value (' + value + '). Expect L.Point or L.LatLng or String ("4.369,50.846") or Object ({x: 4.369, y: 50.846} or {lat: 50.846, lng: 4.369} or [4.369, 50.846]).');
  },

  /**
   * Converts the coordinates system, from UrbIS (EPSG:31370) to Leaflet (EPSG:4326).
   *
   * @see {@link http://epsg.io/31370} -- EPSG:31370 (Belgium Lambert 72).
   * @see {@link http://epsg.io/4326} -- EPSG:4326 (World Geodetic System 1984).
   * @see {@link http://proj4js.org/} -- Library to transform coordinates from one coordinate system to another.
   *
   * @param {(L.Point|L.LatLng|string|object)} value - The value in EPSG:31370.
   * @returns {L.Point} The value converted in EPSG:4326.
   */
  fromUrbisCoords: function (value) {
    this._initProj4js();
    var point = this._toProj4jsPoint(this.toPoint(value));
    Proj4js.transform(this.PROJ4JS_31370, this.PROJ4JS_4326, point);
    return this.toPoint(point);
  },

  /**
   * Converts the coordinates system, from Leaflet (EPSG:4326) to UrbIS (EPSG:31370).
   *
   * @see {@link http://epsg.io/4326} -- EPSG:4326 (World Geodetic System 1984).
   * @see {@link http://epsg.io/31370} -- EPSG:31370 (Belgium Lambert 72).
   * @see {@link http://proj4js.org/} -- Library to transform coordinates from one coordinate system to another.
   *
   * @param {(L.Point|L.LatLng|string|object)} value - The value in EPSG:4326.
   * @returns {L.Point} The value converted in EPSG:31370.
   */
  toUrbisCoords: function (value) {
    this._initProj4js();
    var point = this._toProj4jsPoint(this.toPoint(value));
    Proj4js.transform(this.PROJ4JS_4326, this.PROJ4JS_31370, point);
    return this.toPoint(point);
  },

  /**
   * Converts a Point from UrbIS (EPSG:31370) to a LatLng for Leaflet (EPSG:4326).
   *
   * @see {@link fromUrbisCoords}
   * @see {@link toLatLng}
   *
   * @param {(L.Point|L.LatLng|string|object)} value - The value in EPSG:31370.
   * @returns {L.LatLng} The value converted in EPSG:4326.
   */
  urbisCoordsToLatLng: function (value) {
    return this.toLatLng(this.fromUrbisCoords(value));
  },

  /**
   * Retrieves from UrbIS the address of a LatLng in EPSG:4326.
   *
   * @see {@link urbisResultToAddress}
   * @see {@link http://gis.irisnet.be/urbis/} -- Demos of UrbIS geolocalization services. See section "Get address from x,y coordinates".
   *
   * @param {(L.LatLng|L.Point|string|object)} coords - The LatLng in EPSG:4326.
   # @param {getAddressSuccessCallback} success - The callback that handles a successful response.
   # @param {getAddressErrorCallback} [error] - The callback that handles errors.
   * @returns {object} The address (in our standard format).
   * @throws {Error} If the request doesn't succeed and no error handler is given.
   */
  /**
   * @callback getAddressSuccessCallback
   # @param {object} The address (in our standard format).
   * @see {@link urbisResultToAddress}
   */
  /**
   * @callback getAddressErrorCallback
   # @param {object} The response received from UrbIS.
   */
  getAddressFromLatLng: function (coords, success, error) {
    var that = this;
    $.ajax({
      url: URBIS_URL + 'service/urbis/Rest/Localize/getaddressfromxy',
      type: 'POST',
      dataType: 'jsonp',
      data: {
        json: JSON.stringify({
          language: LANGUAGE_CODE,
          point: this.toPoint(coords, true),  // Preference to LatLng format if value is index-based.
          spatialReference: '4326',
        }),
      },

      success: function (response) {
        success(that.urbisResultToAddress(response.result));
      },

      error: function (response) {
        if (error !== undefined) {
          error(response);
        } else if (response.status === 'error') {
          throw new Error('Unable to locate the address at ' + this.coordsToString(latlng) + '.');
        } else {
          throw new Error('Error: ' + response.status);
        }
      },
    });
  },

  /**
   * Converts the result of a response from the UrbIS service to an object in our standard format.
   *
   # @param {object} result - The `response.result` from the UrbIS service.
   * @returns {object} The address in our standard format: \{street, number, postalCode, city, [latlng]\}.
   */
  urbisResultToAddress: function (result) {
    var address = {
      street: result.address.street.name,
      number: result.address.number,
      postalCode: result.address.street.postCode,
      city: gettext('Brussels'),  // @TODO: Retrieve it according to postal code.
    };
    if (result.point !== undefined) {
      address.latlng = this.toLatLng(result.point);
    }
    return address;
  },

  /**
   * Returns the URL on Google Street View for given coordinates.
   *
   * @see: {@link https://developers.google.com/maps/documentation/streetview/#url_parameters}
   # @param {(L.LatLng|L.Point|string|object)} coords - The coordinates.
   * @returns {string} The URL on Google Street View.
   */
  getStreetViewUrl: function (coords) {
    // @TODO: Improve URL generation?
    //   - Generated URL: https://maps.google.be/maps?q=50.84535101789271,4.351873397827148&layer=c&z=17&iwloc=A&sll=50.84535101789271,4.351873397827148&cbp=13,240.6,0,0,0&cbll=50.84535101789271,4.351873397827148
    //   - Final URL: https://www.google.be/maps/@50.8452712,4.3519753,3a,75y,240.6h,90t/data=!3m5!1e1!3m3!1s2j5CXi5mCN_SzkuGhDGL0w!2e0!3e5
    var latlng = this.toLatLng(coords);
    var v = latlng.lat + ',' + latlng.lng;
    return 'https://maps.google.be/maps?q=' + v + '&layer=c&z=17&iwloc=A&sll=' + v + '&cbp=13,240.6,0,0,0&cbll=' + v;
  },

  /**
   * Returns a string representation of coordinates.
   *
   * @param {(L.LatLng|L.Point)} coords - The coordinates.
   * @returns {string} The address (street, number, postal code, city).
   * @throws {TypeError} If the value cannot be handled.
   */
  coordsToString: function (coords) {
    if (obj instanceof L.LatLng || ('lat' in obj && 'lng' in obj)) {
      return '(' + obj.lat + ', ' + obj.lng + ')';
    }
    if (obj instanceof L.Point || ('x' in obj && 'y' in obj)) {
      return '(' + obj.x + ', ' + obj.y + ')';
    }
    throw new TypeError('Invalid value (' + coords + ').');
  },

  /**
   * Initializes Proj4js for coordinates transformations.
   */
  _initProj4js: function () {
    if (this.PROJ4JS_4326 === undefined) {
      this.PROJ4JS_4326 = new Proj4js.Proj('EPSG:4326');
      this.PROJ4JS_31370 = new Proj4js.Proj('EPSG:31370');
    }
  },

  /**
   * Converts a `L.Point` into a `Proj4js.Point`.
   *
   * @param {(L.Point|object)} point - The point (as `L.Point` or any object with 'x' and 'y' keys).
   * @returns {Proj4js.Point} The point for Proj4js.
   */
  _toProj4jsPoint: function (point) {
    return new Proj4js.Point(point.x, point.y);
  },
};
