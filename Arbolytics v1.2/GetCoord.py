from geopy.geocoders import ArcGIS


def get_coord(ID_UNIDADE,MUNICIPIO_UNIDADE):
    nom=ArcGIS()
    address, (latitude, longitude) = nom.geocode(ID_UNIDADE + " " + MUNICIPIO_UNIDADE)
    return(latitude,longitude)