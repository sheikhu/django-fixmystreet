//Create new object.
UtilGeolocation = new Object();
//Convertion geolocation EPSG instances
UtilGeolocation.PROJ4JS_4326 = new Proj4js.Proj("EPSG:4326");
UtilGeolocation.PROJ4JS_31370 = new Proj4js.Proj("EPSG:31370");
UtilGeolocation.PROJ4JS_WGS84 = new Proj4js.Proj("WGS84");
/**
 * convertCoordinatesToWMS is a method to convert GPS coordinates types to WMS ones.
 * @param longitude: the longitude to convert
 * @param latitude: the latitude to convert
 */
UtilGeolocation.convertCoordinatesToWMS = function(longitude, latitude) {
     var p = new Proj4js.Point(longitude, latitude);
     Proj4js.transform(UtilGeolocation.PROJ4JS_4326, UtilGeolocation.PROJ4JS_31370, p);
     return p;
}

UtilGeolocation.convertCoordinatesToWGS84=function(longitude,latitude) {
	var p = new Proj4js.Point(longitude, latitude);
     Proj4js.transform(UtilGeolocation.PROJ4JS_31370, UtilGeolocation.PROJ4JS_WGS84, p);
     return p;
}