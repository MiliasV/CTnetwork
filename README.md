# ctwalk
CTwalk is a script-based Python package that enables  you to download street network and POI data from OSM, and calculate  how accessible these are from different origin locations.

# Status
Currently developing.
### Installation
```
pip install ctwalk
```

### Get started
How to download a city's street network enriched by network centrality measures

```Python
from ctwalk import streets


# Call the streets function
streets.get_streets_per_cities(cities=['Delft'],buffer_dist=10, network_type='walk', intersection_clos=True, street_betw=True, street_sin=True)
```