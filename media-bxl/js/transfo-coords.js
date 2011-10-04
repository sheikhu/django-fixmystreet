    
(function(){
    var pm = Math.PI / 180;
    var adg = 6378249.2; // demi grand axe de l'ellipsoide
    var bdg = 6356515.0; // petit demi axe
    var f = (adg - bdg) / adg; // aplatissement
    var e = Math.sqrt((adg * adg - bdg * bdg) / (adg * adg)) ; // premiere excentricité
    var esur2 = e / 2; // pour optimiser la vitesse de calcul
    var lambda0 = 2.54 * pm; //DmsToCentieme('2°20''11"E')*pm; //origine lambert 2 
    var phi0 = 51.5 * pm ; //origine lambert 2
    var n = Math.sin(phi0);
    
    // donne la latitude isomérique 
    function LatISO(phi){ // radians !
      var esinphi = e * Math.sin(phi); 
      var v = (1 - esinphi) / (1 + esinphi);
      v = Math.exp((esur2) * Math.log(v));
      return Math.log(Math.tan(Math.PI / 4 + phi / 2) * v);
    }
    
    window.WGSToLambert = function(point){
    var k0 = 0.99987741;//facteur aplatissement de la projection 
    var nl, phi, lambda, rs;
    if ((point.longitude < -2.54) || (point.longitude > 6.4) || (point.latitude < 49.51) || (point.latitude > 51.5)) {
      // controle des limites: valide
	return {x:0, y:0}; // seulement dans la zone Lambert 72
      }
      
      phi = point.latitude * pm; // conversion en radians
      lambda = point.longitude * pm;
      nl = 11745793.39 * Math.exp(-n * LatISO(phi));
      rs = n * (lambda - lambda0);
      var x = 600000 + Math.round(nl * Math.sin(rs)) - 8; 
      var y = Math.round(8199695.768 - nl * Math.cos(rs)) + 7; 
      return {x:x, y:y};
    }
    
    // tests
    // (2.5400, 49.5100), (6.4000, 51.5000)
    /*
    console.log(WGSToLambert({longitude:4,latitude:50}));
    console.log(WGSToLambert({longitude:2.8598785400391, latitude:50.970726013184}));
    */
    Proj4js.defs["EPSG:31370"]="+proj=lcc +lat_1=51.16666723333334 +lat_2=49.83333389999999 +lat_0=90 +lon_0=4.367486666666666 +x_0=150000.013 +y_0=5400088.438 +ellps=intl +towgs84=-99.1,53.3,-112.5,0.419,-0.83,1.885,-1.0 +units=m +no_defs";
    
    var lonlat = new OpenLayers.LonLat(4.3,50.8);
    lonlat.transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:31370"));
    console.log(lonlat);
    console.log((new OpenLayers.Geometry.Point(4.3,50.8))
          .transform(
            new OpenLayers.Projection("EPSG:4326"), // transform from WGS 1984
            new OpenLayers.Projection("EPSG:31370") // to Spherical Mercator Projection
          ));


}());
