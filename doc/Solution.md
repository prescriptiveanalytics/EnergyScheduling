# Energy Use-Case Solution

Generally, the solution of a timestamp of the energy network is the output of the simulation framework, i.e. [pandapower](https://pandapower.readthedocs.io/en/v2.13.1/).

# Energy Use-Case Solution File Description For Scenarios

After calling the powerflow module by pushing the message `opf_with_state` or `opf_data` and running backend, e.g., `network_area`.

A solution consists of `Parameter`, which defines the given parameter and a `Network` which is the result of the energy network simulation.

This allows to calculate solutions for different scenarios.

```json
{
    [
        "Solution": {
            "Parameter": {
                "Timestamp": 1, # Timestamp: unix epoch time in seconds
                "Components": [
                    {
                        "Identifier": "211ca69f-2100-4a67-94da-26e1dbd40dcc", # Component identifier, here storage
                        "MaxCapacity": 12 # maximum capacity
                    },
                    {
                        "Identifier": "8f501d80-59ce-4706-875f-809b3902924e",
                        "ProfileIdentifier": "hgb_south_10kwp"
                    }
                ]
            },
            "Network": net,
        }
    ]
}
```