# ctwalk
CTwalk is a function-based Python package that enables  you to:
* Download street network and POI data from OpenStreetMap per city or bounding box
* Calculate  street network centrality metrics such as street betweenness, street sinuosity, and intersection closeness.
* Calculate how accessible the POIs are from different origin locations based on the downloaded street network and different weights.
* Include different metrics of accessibility.
* Calculate average widths of space along streets dedicated to pedestrians or bicyclists (i.e., sidewalks or bike paths)

<p float="left">
    <img src="https://github.com/MiliasV/ctwalk/blob/main/img/amsterdam_sin.png" width="30%">
    <img src="https://github.com/MiliasV/ctwalk/blob/main/img/barc_clos.png" width="30%">
    <img src="https://github.com/MiliasV/ctwalk/blob/main/img/helsinki_betw.png" width="30%">
</p>

# Status
Currently developing.

* [DONE] Download street network and POI data from OpenStreetMap per city or bounding box                                                    
* [DONE] Calculate  street network centrality metrics such as street betweenness, street sinuosity, and intersection closeness.             
* [PENDING] Calculate how accessible the POIs are from different origin locations based on the downloaded street network and different weights.
* [PENDING] Include different metrics of accessibility.



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

Or check out our [Examples Notebook](https://github.com/MiliasV/ctwalk/blob/main/examples.ipynb) demonstration various functions of ctwalk!


<p float="center">
    <img src="https://github.com/MiliasV/ctwalk/blob/main/img/examples1.png" width="70%">
    <img src="https://github.com/MiliasV/ctwalk/blob/main/img/examples2.png" width="70%">
</p>
