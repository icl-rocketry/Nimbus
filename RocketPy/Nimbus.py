# Nimbus is it a broomstick, I dont think so but it would've been so much more amazing 
# Usmaan's going to suffer' - Kiran 2023

#%%
# importing 
from rocketpy import Environment, Rocket, Flight
from rocketpy.motors import CylindricalTank, Fluid, MassFlowRateBasedTank, LiquidMotor


#%%
# environment set-up
Env = Environment(
    railLength = 12, 
    latitude   = 39.4310, 
    longitude  = -008.3012, 
)

# set date and time
import datetime
tomorrow = datetime.date.today() + datetime.timedelta(days = 1)
Env.setDate((tomorrow.year, tomorrow.month, tomorrow.day, 12))  # Hour given in UTC time

# GFS forecast to get the atmospheric conditions for flight.
Env.setAtmosphericModel(type="Forecast", file="GFS")

# Environment info
Env.info()

#%%
# propulsion system 

# tank geometries
oxidiser_tank_shape = CylindricalTank(0.168/2, 0.437, True)
fuel_tank_shape = CylindricalTank(0.114/2, 0.332, True)
nitrogen_tank_shape = CylindricalTank(0.096/2, 0.214, True)

# check tank geometry 
oxidiser_tank_shape.radius.plot(equalAxis = True)
fuel_tank_shape.radius.plot(equalAxis = True)
nitrogen_tank_shape.radius.plot(equalAxis = True)

# define fluids 
oxidizer_liq = Fluid(name="N2O_l", density=800, quality=1)
oxidizer_gas = Fluid(name="N2O_g", density=1.9277, quality=1)
fuel_liq = Fluid(name="methanol_l", density=786, quality=1)
fuel_gas = Fluid(name="methanol_g", density=1.59, quality=1)

# some tanks 
oxidizer_tank = MassFlowRateBasedTank(
    name = "oxidizer tank",
    geometry = oxidiser_tank_shape,
    initial_liquid_mass = 7,
    initial_gas_mass = 0,
    liquid_mass_flow_rate_in = 0,
    liquid_mass_flow_rate_out = 1.01,
    gas_mass_flow_rate_in = 0.078,
    gas_mass_flow_rate_out = 0,
    liquid = oxidizer_liq,
    gas = oxidizer_gas
)

fuel_tank = MassFlowRateBasedTank(
    name = "fuel tank",
    geometry = fuel_tank_shape,
    initial_liquid_mass = 2,
    initial_gas_mass = 0,
    liquid_mass_flow_rate_in = 0,
    liquid_mass_flow_rate_out = 0.29,
    gas_mass_flow_rate_in = 0.022,
    gas_mass_flow_rate_out = 0,
    liquid = fuel_liq,
    gas = fuel_gas,
)

# liquid engine 
THANOS = LiquidMotor(
    thrustSource = 3000,
    burnOut = 6.5,
    nozzleRadius = 0.038
)

THANOS.addTank(oxidizer_tank, 0.98)
THANOS.addTank(fuel_tank, 1.68)

THANOS.info()

# %%
# making Nimbus now

# note centreOfDryMassPosition = 0  means the dry cg is the origin of the rocket coordinate system

Nimbus = Rocket(
    radius = 19.4/2,
    mass = 54.2-THANOS.propellantInitialMass,
    inertia = [INERTIA TENSOR],
    powerOffDrag = [FROM OPENROCKET],
    powerOnDrag = [FROM OPENROCKET],
    centerOfDryMassPosition = 0,
    coordinateSystemOrientation = "tailToNose",
)

Nimbus.setRailButtons([0.65, -1.30])

Nimbus.addMotor(THANOS, position = -1.82)

NoseCone = Nimbus.addNose(length = 0.6, 
                          kind = "vonKarman", 
                          position = 0.6 + 2.06)

Tail = Nimbus.addTail(
    topRadius = 0.097, 
    bottomRadius = 0.076, 
    length = 0.322, 
    position = -1.5
)

Fins = Nimbus.addTrapezoidalFins(
    n = 3,
    span = ,
    rootchord = ,
    tipChord = ,
    position = ,
    cantAngle = ,
    sweepLength = ,
    sweepAngle = ,
    radius = "None",
    airfoil = "None",
)

Canards = Nimbus.addTrapezoidalFins(
    n = 3,
    span = ,
    rootchord = ,
    tipChord = ,
    position = ,
    cantAngle = ,
    sweepLength = ,
    sweepAngle = ,
    radius = "None",
    airfoil = "None",
)

Nimbus.allInfo()

``