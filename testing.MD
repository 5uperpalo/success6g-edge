
# Real-world testing and data gathering - Parcmotor Castellolí administered by [Cellnex](https://www.cellnex.com/news/noticia-105/)

![parcmotor_castelloli](docs/sources/assets/images/parcmotor_castelloli.jpeg "Parcmotor Castelloli")

| ![Testing_architecture_overview](docs/sources/assets/images/Architecture_Overview–Parcmotor_Castelloli.png "Testing architecture overview") |
| :-----------------------------------------------------------------------------------------------------------------------------------------: |
|                                                      *Castellolí testing architecture*                                                      |

| ![Testing_architecture_services](docs/sources/assets/images/Architecture_Overview–Parcmotor_Castelloli_services.png "Testing architecture services") |
| :--------------------------------------------------------------------------------------------------------------------------------------------------: |
|                                                          *Castellolí testing architecture*                                                           |

legend: 
* white - mandatory
* <span style="color:grey">grey pattern - optional</span>

<details>
<summary>steps:</summary>

* prepare the Kserve model and helm charts
* make testing requests before the day of testing
* run the real-world test with vehicles in Castelloli
* query and save Kepler stats (CPU,RAM usage + CO2 estimation) from Prometheus
* query and save measurements and predictions from Prometheus
* make screenshots: Grafana, NBC environment
* make vehicle pictures
</details>