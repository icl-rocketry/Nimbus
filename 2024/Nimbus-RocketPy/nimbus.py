# using rocketpy v1.0.0 master 

#%% 
# importing 
from rocketpy import Environment, Rocket, Flight, Function
from rocketpy.motors import CylindricalTank, Fluid, MassFlowRateBasedTank, LiquidMotor
import numpy as np

#%% 
# environment set-up
# lat and long are for euroc
Env = Environment( 
    latitude   = 39.232292, 
    longitude  = -008.172027, 
    elevation  = 160,
    )

# set date and time
import datetime
tomorrow = datetime.date.today() + datetime.timedelta(days = 1)
Env.set_date((tomorrow.year, tomorrow.month, tomorrow.day, 14))  # Hour given in UTC time

# GFS forecast to get the atmospheric conditions for flight.
Env.set_atmospheric_model(type="Forecast", file="GFS")

# Environment info
Env.info()

#%% 
# propulsion system 

# define fluids 
oxidizer_liq = Fluid(name="N2O_l", density=800)
oxidizer_gas = Fluid(name="N2O_g", density=1.9277)
fuel_liq = Fluid(name="methanol_l", density=786)
fuel_gas = Fluid(name="methanol_g", density=1.59)
pressurant = Fluid(name="N2", density=300)

# tank geometries
oxidiser_tank_shape = CylindricalTank(0.086, 0.639, spherical_caps=False)
fuel_tank_shape = CylindricalTank(0.114/2, 0.332, spherical_caps=False)
nitrogen_tank_shape = CylindricalTank(0.096/2, 0.214, spherical_caps=True)

# some tanks 
oxidizer_tank = MassFlowRateBasedTank(
    name = "oxidizer tank",
    geometry = oxidiser_tank_shape,
    flux_time = 6.75,
    initial_liquid_mass = 7,
    initial_gas_mass = 0,
    liquid_mass_flow_rate_in = 0,
    # liquid_mass_flow_rate_out = 1.01,
    liquid_mass_flow_rate_out = 0.875, 
    gas_mass_flow_rate_in = 0.078,
    gas_mass_flow_rate_out = 0,
    liquid = oxidizer_liq,
    gas = oxidizer_gas
)

fuel_tank = MassFlowRateBasedTank(
    name = "fuel tank",
    geometry = fuel_tank_shape,
    flux_time = 6.75,
    initial_liquid_mass = 4,
    initial_gas_mass = 0,
    liquid_mass_flow_rate_in = 0,
    # liquid_mass_flow_rate_out = 0.29,
    liquid_mass_flow_rate_out = 0.2,
    gas_mass_flow_rate_in = 0.022,
    gas_mass_flow_rate_out = 0,
    liquid = fuel_liq,
    gas = fuel_gas,
)
 
# liquid engine 
THANOS = LiquidMotor(
    thrust_source = "nimbus_thrust_hotfire_cut_off.eng",
    center_of_dry_mass_position = 0,
    dry_mass = 0,
    dry_inertia = (0,0,0),
    nozzle_radius = 0.037385,
)

THANOS.add_tank(oxidizer_tank, 0.98)
THANOS.add_tank(fuel_tank, 1.68)

THANOS.info()

#%% 
# Nimbus ascent set-up

# note centreOfDryMassPosition = 0  means the dry cg is the origin of the rocket coordinate system

MargeMass = 3.2; # Payload mass with chute
NimbusMass = 50.2 - MargeMass; # Nimbus dry mass excluding payload

NimbusAscent = Rocket(
    radius = 0.194/2,
    mass = NimbusMass + MargeMass,
    # inertia = (4.75*10**10, 4.75*10**10, 2.387*10**8,
    #            -23063, -8.278*10**6, -2.584*10**6),
    inertia = (47.6, 47.6, 0.2487,
               -0.0003062, -0.09418, -0.02619),
    power_off_drag = "nimbus_Cd.csv",
    power_on_drag = "nimbus_Cd.csv",
    center_of_mass_without_motor = 0,
    coordinate_system_orientation = "nose_to_tail",
)

NimbusAscent.set_rail_buttons(
    upper_button_position = 0.65,
    lower_button_position = -1.30,
    angular_position = 60,
    )

NimbusAscent.add_motor(THANOS, position = -1.82)

NoseCone = NimbusAscent.add_nose(length = 0.38, 
                          kind = "vonKarman", 
                          position = 0)

Tail = NimbusAscent.add_tail(
    top_radius = 0.097, 
    bottom_radius = 0.076, 
    length = 0.322, 
    position = -1.5
)

Fins = NimbusAscent.add_trapezoidal_fins(
    n = 3,
    span = 0.21,
    root_chord = 0.320,
    tip_chord = 0.150,
    position = -1.4,
    cant_angle = 25,
    # sweep_length = 0.085,
    sweep_angle = 21.942, # leading edge sweep
    radius = 0.194/2,
    airfoil = None,
)

# Canards = NimbusAscent.add_trapezoidal_fins(
#     n = 3,
#     span = 0.05,
#     root_chord = 0.11,
#     tip_chord = 0.045,
#     position = 1.05,
#     cant_angle = 0,
#     # sweep_length = 0.07,
#     sweep_angle = 54.5,
#     radius = 0.194/2,
#     airfoil = ["xf-n0012-il-100000.csv", "degrees"],
# )

# Parachutes
# def drogue_trigger(p, h, y):
#     # activate drogue when vz < 0 m/s.
#     return True if y[5] < 0 else False


# def main_trigger(p, h, y):
#     # activate main when vz < 0 m/s and z < 800 m
#     return True if y[5] < 0 and h < 450 else False

# Main = NimbusAscent.add_parachute(
#     "Main",
#     cd_s = 0.97*np.pi*6.10**2 / 4,
#     # cd_s = 2.2*np.pi*4.26**2 / 4,
#     trigger = main_trigger,
#     sampling_rate = 105,
#     lag = 3.0,
#     noise = (0, 8.3, 0.5),
# )

# Drogue = NimbusAscent.add_parachute(
#     "Drogue",
#     cd_s = 0.9*np.pi*0.914**2 / 4,
#     trigger = drogue_trigger,
#     sampling_rate = 105,
#     lag = 1.0,
#     noise = (0, 8.3, 0.5),
# )

# NimbusAscent.info()

#%% 
# Nimbus ascent simulation

NimbusAscentFlight = Flight(rocket = NimbusAscent, 
                    environment = Env, 
                    rail_length = 12,
                    inclination = 84, 
                    heading = 133,  
                    terminate_on_apogee = True,
                    name = "Nimbus Ascent Trajectory",
                    )

NimbusAscentFlight.all_info()

#%% 
# Nimbus Descent set-up
NimbusDescent = Rocket(
    radius = 0.194/2,
    mass = NimbusMass,
    inertia = (47.6, 47.6, 0.2487,
               -0.0003062, -0.09418, -0.02619),
    power_off_drag = "nimbus_Cd.csv",
    power_on_drag = "nimbus_Cd.csv",
    center_of_mass_without_motor = 0,
    coordinate_system_orientation = "tail_to_nose",
)

# Parachutes
def drogue_trigger(p, h, y):
    # activate drogue when vz < 0 m/s.
    return True if y[5] < 0 else False


def main_trigger(p, h, y):
    # activate main when vz < 0 m/s and z < 800 m
    return True if y[5] < 0 and h < 450 else False

Main = NimbusDescent.add_parachute(
    "Main",
    cd_s = 0.97*np.pi*6.10**2 / 4,
    # cd_s = 2.2*np.pi*4.26**2 / 4,
    trigger = main_trigger,
    sampling_rate = 105,
    lag = 3.0,
    noise = (0, 8.3, 0.5),
)

Drogue = NimbusDescent.add_parachute(
    "Drogue",
    cd_s = 0.9*np.pi*0.914**2 / 4,
    trigger = drogue_trigger,
    sampling_rate = 105,
    lag = 1.0,
    noise = (0, 8.3, 0.5),
)

#%%
# Nimbus Descent Simulation
NimbusDescentFlight = Flight(rocket = NimbusAscent, 
                    environment = Env, 
                    rail_length = 12,
                    inclination = 84, 
                    heading = 133,  
                    initial_solution = NimbusAscentFlight,
                    name = "Nimbus Descent Trajectory",
                    )

# NimbusDescentFlight.all_info()

#%% 
# Payload set-up
Marge = Rocket(
    radius = 0.05,
    mass = MargeMass,
    inertia = (0.1,0.1,0.001),
    power_off_drag = 0.5,
    power_on_drag = 0.5,
    center_of_mass_without_motor = 0
)

def payload_trigger(p, h, y):
    # activate drogue when vz < 0 m/s.
    return True if y[5] < 0 else False

Drogue = Marge.add_parachute(
    "Drogue",
    cd_s = 0.9*np.pi*0.914**2 / 4,
    trigger = drogue_trigger,
    sampling_rate = 105,
    lag = 1.0,
    noise = (0, 8.3, 0.5),
)

#%% 
# Payload Flight Simulation
PayloadFlight = Flight(
    rocket = Marge,
    environment = Env,
    rail_length = 12,
    inclination = 0,
    heading = 0,
    initial_solution = NimbusAscentFlight,
    name = "Payload Flight",
)

#%%
# Flight comparisons
from rocketpy.plots.compare import CompareFlights
comparison = CompareFlights([NimbusAscentFlight, NimbusDescentFlight, PayloadFlight])
comparison.trajectories_3d(legend = True)
comparison.positions()
comparison.velocities()
comparison.accelerations()