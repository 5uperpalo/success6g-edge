# Architecture Overview

| ![Work_in_progress_architecture](img/success6g_edge_architecture.png "Work in progress architecture") |
| :---------------------------------------------------------------------------------------------------: |
|                                        *Architecture Overview*                                        |


# Real-world testing and data gathering - Parcmotor Castellolí

| ![Work_in_progress_architecture](img/success6g_edge_architecture_parcmotor_castelloli.png "Work in progress architecture") |
| :------------------------------------------------------------------------------------------------------------------------: |
|                                             *Real-world Testing Architecture*                                              |

legend: 
* mandatory
* <span style="color:blue">Optional</span>

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

# R&D – Testbed (SUPERCOM)

| ![Work_in_progress_architecture](img/success6g_edge_architecture_rnd.png "Work in progress architecture") |
| :-------------------------------------------------------------------------------------------------------: |
|                                            *R&D Architecture*                                             |

<details>
<summary>steps:</summary>

* setup full testbed
* use RaspberryPis to emulate edge nodes
* send gathered data using python script and target specific edge nodes (emulation of vehicle moving between base stations)
* test centralized vs edge computation vs federated learning
* query and save Kepler stats (CPU,RAM usage + CO2 estimation) from Prometheus
* query and save measurements and predictions from Prometheus
* make screenshots: Grafana, Testbed environment
* make pictures of used HW (RaspberyPis, workstation, SUPERCOM servers rack?)
</details>
