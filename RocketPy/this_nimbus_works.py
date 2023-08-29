# Nimbus is it a broomstick, I dont think so but it would've been so much more amazing 
# 'Usmaan's going to suffer' - Kiran 2023

#%% 
# importing 
from rocketpy import Environment, Rocket, Flight
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
Env.set_date((tomorrow.year, tomorrow.month, tomorrow.day, 12))  # Hour given in UTC time

# GFS forecast to get the atmospheric conditions for flight.
Env.set_atmospheric_model(type="Forecast", file="GFS")

# Environment info
Env.info()

#%% 
# propulsion system 

# tank geometries
oxidiser_tank_shape = CylindricalTank(0.086, 0.639, True)
fuel_tank_shape = CylindricalTank(0.114/2, 0.332, True)
nitrogen_tank_shape = CylindricalTank(0.096/2, 0.214, True)

# check tank geometry 
# oxidiser_tank_shape.radius.plot(equalAxis = True)
# fuel_tank_shape.radius.plot(equalAxis = True)
# nitrogen_tank_shape.radius.plot(equalAxis = True)

# define fluids 
oxidizer_liq = Fluid(name="N2O_l", density=800, quality=1)
oxidizer_gas = Fluid(name="N2O_g", density=1.9277, quality=1)
fuel_liq = Fluid(name="methanol_l", density=786, quality=1)
fuel_gas = Fluid(name="methanol_g", density=1.59, quality=1)

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
    initial_liquid_mass = 2,
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
    thrust_source = "nimbus_thrust.eng",
    center_of_dry_mass = 0,
    # burn_time = 6,
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

MargeMass = 3.1; # Payload mass with chute
NimbusMass = 50.2 - MargeMass; # Nimbus dry mass excluding payload

NimbusAscent = Rocket(
    radius = 0.194/2,
    mass = NimbusMass + MargeMass,
    # inertia = (4.75*10**10, 4.75*10**10, 2.387*10**8,
    #            -23063, -8.278*10**6, -2.584*10**6),
    inertia = (4.75*10**10, 4.75*10**10, 2.387*10**8,
               -23063, -8.278*10**6, -2.584*10**6),
    power_off_drag = "nimbus_Cd.csv",
    power_on_drag = "nimbus_Cd.csv",
    center_of_mass_without_motor = 0,
    coordinate_system_orientation = "tail_to_nose",
)

NimbusAscent.set_rail_buttons(
    upper_button_position = 0.65,
    lower_button_position = -1.30,
    angular_position = 60,
    )

NimbusAscent.add_motor(THANOS, position = -1.82)

NoseCone = NimbusAscent.add_nose(length = 0.6, 
                          kind = "vonKarman", 
                          position = 0.6 + 2.06)

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
    cant_angle = 0,
    # sweep_length = 0.085,
    sweep_angle = 21.942, # leading edge sweep
    radius = 0.194/2,
    airfoil = None,
)

Canards = NimbusAscent.add_trapezoidal_fins(
    n = 3,
    span = 0.05,
    root_chord = 0.11,
    tip_chord = 0.045,
    position = 1.05,
    cant_angle = 0,
    # sweep_length = 0.07,
    sweep_angle = 54.5,
    radius = 0.194/2,
    airfoil = ["xf-n0012-il-100000.csv", "degrees"],
)

# Parachutes
def drogue_trigger(p, h, y):
    # p = pressure considering parachute noise signal
    # h = height above ground level considering parachute noise signal
    # y = [x, y, z, vx, vy, vz, e0, e1, e2, e3, w1, w2, w3]

    # activate drogue when vz < 0 m/s.
    return True if y[5] < 0 else False


def main_trigger(p, h, y):
    # p = pressure considering parachute noise signal
    # h = height above ground level considering parachute noise signal
    # y = [x, y, z, vx, vy, vz, e0, e1, e2, e3, w1, w2, w3]

    # activate main when vz < 0 m/s and z < 800 m
    return True if y[5] < 0 and h < 450 else False

Main = NimbusAscent.add_parachute(
    "Main",
    cd_s = 0.97*np.pi*6.10**2 / 4,
    # cd_s = 2.2*np.pi*4.26**2 / 4,
    trigger = main_trigger,
    sampling_rate = 105,
    lag = 1.5,
    noise = (0, 8.3, 0.5),
)

Drogue = NimbusAscent.add_parachute(
    "Drogue",
    cd_s = 0.9*np.pi*0.914**2 / 4,
    trigger = drogue_trigger,
    sampling_rate = 105,
    lag = 1.0,
    noise = (0, 8.3, 0.5),
)

NimbusAscent.info()

#%% 
# Nimbus ascent simulation

NimbusAscentFlight = Flight(rocket = NimbusAscent, 
                    environment = Env, 
                    rail_length = 12,
                    inclination = 84, 
                    heading = 133,  
                    terminate_on_apogee = False,
                    name = "Nimbus Ascent Trajectory",
                    )

NimbusAscentFlight.all_info()
