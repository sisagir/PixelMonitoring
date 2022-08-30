import math

# TODO: Check those numbers

#### --------------------------------------------------------------------------------------------------------------
#### Constants
kb = 8.6173324 * math.pow(10, -5) # [eV * K^{-1}]
Eg = 1.21 # [eV]
Kfact = 273.15
Tref = Kfact
### Coolant temperature
T_coolant = -10
### Actual sensor temperature is higher than coolant temperature. Considering here +10 degrees.
T_diff = 10
### Sensor volume
rocVol = 0.81 * 0.81 * 0.0285
#### --------------------------------------------------------------------------------------------------------------
