# ctwalk
CTwalk is a function-based Python package that enables  you to:
* Download street network data from OpenStreetMap
* Download POI data from OpenStreetMap
* Calculate  street network metrics per city or bounding box
* Calculate how accessible the POIs are from different origin locations based on the downloaded street network.

<p float="left">
    <img src="https://github.com/MiliasV/ctwalk/blob/main/img/amsterdam_sin.png" width="300" height="300">
    <img src="https://github.com/MiliasV/ctwalk/blob/main/img/barc_clos.png" width="300" height="300">
    <img src="https://github.com/MiliasV/ctwalk/blob/main/img/helsinki_betw.png" width="300" height="300">
</p>

# Status
Currently developing.
### Installation

* Clone the repo
* Run the following command in the terminal:

```
pip install dist/ctwalk-0.1.0-py3-none-any.whl
```

### Get started
How to download a city's street network enriched by network centrality measures (intersection closeness, street betweenness, street sinuosity)



Now you can use the functions of the library.
For example:

```Python
from ctwalk import streets

streets.get_streets_per_cities(cities=['Delft'],buffer_dist=10, network_type='drive', intersection_clos=False,  street_betw=False, street_sin=False)

streets.get_streets_per_bbox(52.032492, 51.966120, 4.372967, 4.344471, network_type='drive', output_folder='.',intersection_clos=False, street_betw=True, street_sin=False, retain_all=True)
```
