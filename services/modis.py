"""wildfile.services.modis"""
import ee
ee.Initialize()

def fetch_modis(lat, lon):
    point = ee.Geometry.Point(lon, lat)

    def safe_fetch(collection, band, scale):
        img = (
            ee.ImageCollection(collection)
            .select(band)
            .filterBounds(point)
            .sort("system:time_start", False)
            .first()
        )
        if img is None:
            return None

        val = img.reduceRegion(
            ee.Reducer.mean(), point, scale
        ).get(band)

        return val.getInfo() if val else None

    ndvi = safe_fetch("MODIS/061/MOD13Q1", "NDVI", 250)
    evi = safe_fetch("MODIS/061/MOD13Q1", "EVI", 250)
    lst = safe_fetch("MODIS/061/MOD11A1", "LST_Day_1km", 1000)

    return {
        "NDVI": ndvi * 0.0001 if ndvi else None,
        "EVI": evi * 0.0001 if evi else None,
        "LST_C": (lst * 0.02 - 273.15) if lst else None
    }
