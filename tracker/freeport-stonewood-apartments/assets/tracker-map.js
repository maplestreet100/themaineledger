/* Interactive site map for the Freeport Stonewood / Lighthouse Road tracker.
   MapLibre GL JS 4.7.1 (vendored) + OpenStreetMap raster tiles (no API keys).
   Parcel geometry: Town of Freeport assessor GIS, via Vision Government Solutions. */
(function () {
  var container = document.getElementById("site-map");
  if (!container || typeof maplibregl === "undefined") return;

  var BRICK = "#a33a22";
  var INK = "#1f1c18";
  var ASSETS = new URL("./", document.currentScript.src);

  var map = new maplibregl.Map({
    container: "site-map",
    style: {
      version: 8,
      sources: {
        osm: {
          type: "raster",
          tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
          tileSize: 256,
          attribution: "&copy; <a href=\"https://www.openstreetmap.org/copyright\">OpenStreetMap</a> contributors",
          maxzoom: 19
        }
      },
      layers: [{ id: "osm", type: "raster", source: "osm" }]
    },
    center: [-70.13143, 43.82602],
    zoom: 16,
    minZoom: 12,
    maxZoom: 19,
    cooperativeGestures: true,
    dragRotate: false,
    pitchWithRotate: false,
    attributionControl: false,
    locale: {
      "CooperativeGesturesHandler.WindowsHelpText": "Use Ctrl + scroll to zoom the map",
      "CooperativeGesturesHandler.MacHelpText": "Use \u2318 + scroll to zoom the map",
      "CooperativeGesturesHandler.MobileHelpText": "Use two fingers to move the map"
    }
  });

  map.addControl(new maplibregl.NavigationControl({ showCompass: false, visualizePitch: false }), "top-right");
  map.addControl(new maplibregl.AttributionControl({ compact: true }), "bottom-right");

  function collectBounds(fc, bounds) {
    (fc.features || []).forEach(function (feat) {
      var geom = feat.geometry;
      if (!geom) return;
      var rings = geom.type === "Polygon" ? geom.coordinates
        : geom.type === "MultiPolygon" ? geom.coordinates.flat()
        : [];
      rings.forEach(function (ring) {
        ring.forEach(function (pt) { bounds.extend(pt); });
      });
    });
    return bounds;
  }

  map.on("load", function () {
    Promise.all([
      fetch(new URL("parcel-70-B-1.geojson", ASSETS)).then(function (r) {
        if (!r.ok) throw new Error("parcel " + r.status);
        return r.json();
      }),
      fetch(new URL("neighbors.geojson", ASSETS)).then(function (r) {
        if (!r.ok) throw new Error("neighbors " + r.status);
        return r.json();
      })
    ]).then(function (layers) {
      var parcel = layers[0];
      var neighbors = layers[1];

      map.addSource("neighbors", { type: "geojson", data: neighbors });
      map.addSource("parcel", { type: "geojson", data: parcel });

      map.addLayer({
        id: "neighbors-fill",
        type: "fill",
        source: "neighbors",
        paint: { "fill-color": "#1f1c18", "fill-opacity": 0.04 }
      });
      map.addLayer({
        id: "neighbors-line",
        type: "line",
        source: "neighbors",
        paint: {
          "line-color": "#3a362f",
          "line-width": 1.25,
          "line-opacity": 0.85
        }
      });
      map.addLayer({
        id: "parcel-fill",
        type: "fill",
        source: "parcel",
        paint: { "fill-color": BRICK, "fill-opacity": 0.38 }
      });
      map.addLayer({
        id: "parcel-line",
        type: "line",
        source: "parcel",
        paint: { "line-color": BRICK, "line-width": 2.25 }
      });

      var bounds = collectBounds(parcel, new maplibregl.LngLatBounds());
      if (!bounds.isEmpty()) {
        var ne = bounds.getNorthEast();
        var sw = bounds.getSouthWest();
        var latPad = (ne.lat - sw.lat) * 0.35;
        var lngPad = (ne.lng - sw.lng) * 0.35;
        bounds.extend([sw.lng - lngPad, sw.lat - latPad]);
        bounds.extend([ne.lng + lngPad, ne.lat + latPad]);
        map.fitBounds(bounds, { padding: 28, maxZoom: 18, duration: 0 });
      }

      map.on("click", "parcel-fill", function (e) {
        var p = e.features && e.features[0] && e.features[0].properties || {};
        var html = "<strong>The site</strong><br>0 Lighthouse Road<br>Tax Map 23, Lot 70-B-1<br>About 2.9 acres, zoned Commercial 1";
        if (p.mblu && p.mblu !== "23/70/B/1") {
          html = "<strong>" + (p.lot_addr || p.mblu) + "</strong>";
        }
        new maplibregl.Popup({ closeButton: true, maxWidth: "240px" })
          .setLngLat(e.lngLat)
          .setHTML(html)
          .addTo(map);
      });

      map.on("mouseenter", "parcel-fill", function () { map.getCanvas().style.cursor = "pointer"; });
      map.on("mouseleave", "parcel-fill", function () { map.getCanvas().style.cursor = ""; });

      map.once("idle", function () {
        window.__trackerMapReady = true;
        document.body.setAttribute("data-map-ready", "true");
      });
    }).catch(function (err) {
      console.error("Tracker map failed to load parcel data:", err);
      container.setAttribute("data-map-error", "true");
    });
  });
})();
