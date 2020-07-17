import googlemaps
from flask import current_app


ADDR_COMPONENT_TYPES_WITH_PLACE = ["postal_town", "neighborhood", "sublocality", "administrative_area_level_2", "administrative_area_level_1"]


class GeoCodeLookup:
    def __init__(self):
        self.client = googlemaps.Client(key=current_app.config['GOOGLE_API_KEY'])
    
    def get_name_of_place(self, latitude, longitude):
        location_tuple = (latitude, longitude)
        address_components = None
        
        try:
            result = self.client.reverse_geocode(location_tuple)
            address_components = self._get_address_components(result)
        except:
            pass

        return self._find_place_in_address_components(address_components)

        
    def _get_address_components(self, reverse_lookup_result):
        if len(reverse_lookup_result) > 0:
            result = reverse_lookup_result[0]

            if "address_components" in result and len(result["address_components"]) > 0:
                return result["address_components"]
        
        return None      

    def _find_place_in_address_components(self, address_components):
        if address_components is not None:

            for i in range(len(address_components)):
                address_component = address_components[i]
                
                if "long_name" in address_component and "types" in address_component:
                    addr_types = address_component["types"]

                    for place_type in ADDR_COMPONENT_TYPES_WITH_PLACE:
                        if place_type in addr_types:
                            return address_component["long_name"]

        return ""
