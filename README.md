# ctwalk
CTwalk is a function-based Python package that enables  you to download street network and POI data from OSM, and calculate  how accessible these are from different origin locations.

# Status
Currently developing.
### Installation

* Clone the repo
* Run the following command in the terminal:

''' 
pip install dist/ctwalk-0.1.0-py3-none-any.whl
'''

### Get started
How to download a city's street network enriched by network centrality measures (intersection closeness, street betweenness, street sinuosity)



Now you can use the functions of the library.
For example:

```Python
from ctwalk import streets

streets.get_streets_per_cities(cities=['Delft'],buffer_dist=10, network_type='drive', intersection_clos=False,  street_betw=False, street_sin=False)

streets.get_streets_per_bbox(52.032492, 51.966120, 4.372967, 4.344471, network_type='drive', output_folder='.',intersection_clos=False, street_betw=True, street_sin=False, retain_all=True)
```
