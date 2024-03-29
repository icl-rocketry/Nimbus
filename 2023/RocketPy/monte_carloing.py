from datetime import datetime 
from time import process_time, perf_counter, time 
# import glob

from rocketpy import Environment, Rocket, Flight, Function
from rocketpy.motors import CylindricalTank, Fluid, MassFlowRateBasedTank, LiquidMotor

import numpy as np
from numpy.random import normal, uniform, choice
from IPython.display import display

import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.rcParams["figure.figsize"] = [8,5]
mpl.rcParams["figure.dpi"] = 120
mpl.rcParams["font.size"] = 14
mpl.rcParams["legend.fontsize"] = 14
mpl.rcParams["figure.titlesize"] = 14

analysis_parameters = {
    "rocketMass": (50.2, 0.01),
    "inclination": (84, 2),
    "heading": (133, 5),
    "railLength": (12, 0.005), 
}

# flight settings generator
def flight_settings(analysis_parameters, total_number):
    i = 0
    while i < total_number:
        flight_setting = {}
        for parameter_key, parameter_value in analysis_parameters.items():
            if type(parameter_value) is tuple:
                flight_setting[parameter_key] = normal(*parameter_value)
            else:
                flight_setting[parameter_key] = choice(parameter_value)

        i += 1
        yield flight_setting 

# export function
def export_flight_data(flight_setting, flight_data, exec_time):
    flight_result = {
        "outOfRailTime": flight_data.out_of_rail_time,
        "outOfRailVelocity": flight_data.out_of_rail_velocity,
        "apogeeTime": flight_data.apogee_time,
        "apogeeAltitude": flight_data.apogee - Env.elevation,
        "apogeeX": flight_data.apogee_x,
        "apogeeY": flight_data.apogee_y,
        # "impactTime": flight_data.impact_time,
        "impactX": flight_data.x_impact,
        "impactY": flight_data.y_impact,
        "impactVelocity": flight_data.impact_velocity,
        "initialStaticMargin": flight_data.rocket.static_margin(0),
        "outOfRailStaticMargin": flight_data.rocket.static_margin(TestFlight.out_of_rail_time),
        "finalStaticMargin": flight_data.rocket.static_margin(TestFlight.rocket.motor.burn_out_time),
        "numberOfEvents": len(flight_data.parachute_events),
        "executionTime": exec_time,
    }

    sol = np.array(flight_data.solution)

    flight_data.vx = Function(
        sol[:, [0,4]], "Time (s)", "Vx (m/s)", "linear", extrapolation = "natural"
    )

    flight_data.vy = Function(
        sol[:, [0,5]], "Time (s)", "Vy (m/s)", "linear", extrapolation = "natural"
    )

    flight_data.vz = Function(
        sol[:, [0,6]], "Time (s)", "Vz (m/s)", "linear", extrapolation = "natural"
    )

    flight_data.v = (flight_data.vx**2 + flight_data.vy**2 + flight_data.vx**2) ** 0.5

    flight_data.max_vel = np.amax(flight_data.v.source[:,1])
    flight_result["maxVelocity"] = flight_data.max_vel

    if len(flight_data.parachute_events) > 0:
        flight_result["drogueTriggerTime"] = flight_data.parachute_events[0][0]
        flight_result["drogueInflatedTime"] = (
            flight_data.parachute_events[0][0] + flight_data.parachute_events[0][1].lag
        )
        flight_data["drogueInflatedVelocity"] = flight_data.v(
            flight_data.parachute_events[0][0] + flight_data.parachute_events[0][1].lag
        )
    else:
        flight_result["drogueTriggerTime"] = 0
        flight_result["drogueInflatedTime"] = 0
        flight_result["drogueInflatedVelocity"] = 0

    monte_carlo_input_file.write(str(flight_setting) + "\n")
    monte_carlo_output_file.write(str(flight_result) + "\n")


def export_flight_error(flight_setting):
    monte_carlo_error_file.write(str(flight_setting) + "\n")

filename = "monte_carlo_outputs/nimbus"

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
simulation_number = 10
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


monte_carlo_error_file = open(str(filename) + ".disp_errors.txt", "w")
monte_carlo_input_file = open(str(filename) + ".disp_inputs.txt", "w")
monte_carlo_output_file = open(str(filename) + ".disp_outputs.txt", "w")

# counter initialisation
i = 0

initial_wall_time = time()
initial_cpu_time = process_time()

# environment
Env = Environment( 
    latitude   = 39.232292, 
    longitude  = -008.172027, 
    elevation  = 160,
    )

# set date and time
import datetime
tomorrow = datetime.date.today() + datetime.timedelta(days = 14)
Env.set_date((tomorrow.year, tomorrow.month, tomorrow.day, 12))  # Hour given in UTC time

# GFS forecast to get the atmospheric conditions for flight.
Env.set_atmospheric_model(type="Forecast", file="GFS")

# tank geometries
oxidiser_tank_shape = CylindricalTank(0.086, 0.639, True)
fuel_tank_shape = CylindricalTank(0.114/2, 0.332, True)
nitrogen_tank_shape = CylindricalTank(0.096/2, 0.214, True)

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

out = display("Starting", display_id = True)
for setting in flight_settings(analysis_parameters, simulation_number):

    start_time = process_time()
    i += 1

    NimbusAscent = Rocket(
        radius = 0.194/2,
        mass = setting["rocketMass"],
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
    Main = NimbusAscent.add_parachute(
        "Main",
        cd_s = 0.97*np.pi*6.10**2 / 4,
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

    try: 
        TestFlight = Flight(
            rocket = NimbusAscent,
            environment = Env,
            rail_length = setting["railLength"],
            inclination = setting["inclination"],
            heading = setting["heading"],
            max_time = 600,
        ) 

        export_flight_data(setting, TestFlight, process_time() - start_time)
    except Exception as E:
        print(E)
        export_flight_error(setting)

    # out.update(
    #     f"Current iteration: {i:06d} | Average Time per Iteration: {(process_time() - initial_cpu_time)/i:2.6f} s"
    # )

final_string = f"Completed {i} iterations successfully. Total CPU time: {process_time() - initial_cpu_time} s. Total wall time {time() - initial_wall_time} s"
# out.update(final_string)
monte_carlo_input_file.write(final_string + "\n")
monte_carlo_output_file.write(final_string + "\n")
monte_carlo_error_file.write(final_string + "\n")

monte_carlo_input_file.close()
monte_carlo_output_file.close()
monte_carlo_error_file.close()

filename = "monte_carlo_outputs/nimbus"

dispersion_general_results = []

dispersion_results = {
    "outOfRailTime": [],
    "outOfRailVelocity": [],
    "apogeeTime": [],
    "apogeeAltitude": [],
    "apogeeX": [],
    "apogeeY": [],
    # "impactTime": [],
    "impactX": [],
    "impactY": [],
    "impactVelocity": [],
    "initialStaticMargin": [],
    "outOfRailStaticMargin": [],
    "finalStaticMargin": [],
    "numberOfEvents": [],
    "maxVelocity": [],
    "drogueTriggerTime": [],
    "drogueInflatedTime": [],
    "drogueInflatedVelocity": [],
    "executionTime": [],
}

monte_carlo_output_file = open(str(filename) + ".disp_outputs.txt", "r+")

for line in monte_carlo_output_file:
    if line[0] != "{":
        continue
    flight_result = eval(line)
    dispersion_general_results.append(flight_result)
    for parameter_key, parameter_value in flight_result.items():
        dispersion_results[parameter_key].append(parameter_value)

monte_carlo_output_file.close()

N = len(dispersion_general_results)
print("Number of simulations: ", N)

print(
    f'Out of Rail Time -         Mean Value: {np.mean(dispersion_results["outOfRailTime"]):0.3f} s'
)
print(
    f'Out of Rail Time - Standard Deviation: {np.std(dispersion_results["outOfRailTime"]):0.3f} s'
)

plt.figure()
plt.hist(dispersion_results["outOfRailTime"], bins=int(N**0.5))
plt.title("Out of Rail Time")
plt.xlabel("Time (s)")
plt.ylabel("Number of Occurences")
plt.show()

print(
    f'Out of Rail Velocity -         Mean Value: {np.mean(dispersion_results["outOfRailVelocity"]):0.3f} m/s'
)
print(
    f'Out of Rail Velocity - Standard Deviation: {np.std(dispersion_results["outOfRailVelocity"]):0.3f} m/s'
)

plt.figure()
plt.hist(dispersion_results["outOfRailVelocity"], bins=int(N**0.5))
plt.title("Out of Rail Velocity")
plt.xlabel("Velocity (m/s)")
plt.ylabel("Number of Occurences")
plt.show()

print(
    f'Apogee Time -         Mean Value: {np.mean(dispersion_results["apogeeTime"]):0.3f} s'
)
print(
    f'Apogee Time - Standard Deviation: {np.std(dispersion_results["apogeeTime"]):0.3f} s'
)

plt.figure()
plt.hist(dispersion_results["apogeeTime"], bins=int(N**0.5))
plt.title("Apogee Time")
plt.xlabel("Time (s)")
plt.ylabel("Number of Occurences")
plt.show()

print(
    f'Apogee Altitude -         Mean Value: {np.mean(dispersion_results["apogeeAltitude"]):0.3f} m'
)
print(
    f'Apogee Altitude - Standard Deviation: {np.std(dispersion_results["apogeeAltitude"]):0.3f} m'
)

plt.figure()
plt.hist(dispersion_results["apogeeAltitude"], bins=int(N**0.5))
plt.title("Apogee Altitude")
plt.xlabel("Altitude (m)")
plt.ylabel("Number of Occurences")
plt.show()

print(
    f'Apogee X Position -         Mean Value: {np.mean(dispersion_results["apogeeX"]):0.3f} m'
)
print(
    f'Apogee X Position - Standard Deviation: {np.std(dispersion_results["apogeeX"]):0.3f} m'
)

plt.figure()
plt.hist(dispersion_results["apogeeX"], bins=int(N**0.5))
plt.title("Apogee X Position")
plt.xlabel("Apogee X Position (m)")
plt.ylabel("Number of Occurences")
plt.show()

print(
    f'Apogee Y Position -         Mean Value: {np.mean(dispersion_results["apogeeY"]):0.3f} m'
)
print(
    f'Apogee Y Position - Standard Deviation: {np.std(dispersion_results["apogeeY"]):0.3f} m'
)

plt.figure()
plt.hist(dispersion_results["apogeeY"], bins=int(N**0.5))
plt.title("Apogee Y Position")
plt.xlabel("Apogee Y Position (m)")
plt.ylabel("Number of Occurences")
plt.show()

# print(
#     f'Impact Time -         Mean Value: {np.mean(dispersion_results["impactTime"]):0.3f} s'
# )
# print(
#     f'Impact Time - Standard Deviation: {np.std(dispersion_results["impactTime"]):0.3f} s'
# )

# plt.figure()
# plt.hist(dispersion_results["impactTime"], bins=int(N**0.5))
# plt.title("Impact Time")
# plt.xlabel("Time (s)")
# plt.ylabel("Number of Occurences")
# plt.show()

print(
    f'Impact X Position -         Mean Value: {np.mean(dispersion_results["impactX"]):0.3f} m'
)
print(
    f'Impact X Position - Standard Deviation: {np.std(dispersion_results["impactX"]):0.3f} m'
)

plt.figure()
plt.hist(dispersion_results["impactX"], bins=int(N**0.5))
plt.title("Impact X Position")
plt.xlabel("Impact X Position (m)")
plt.ylabel("Number of Occurences")
plt.show()

print(
    f'Impact Y Position -         Mean Value: {np.mean(dispersion_results["impactY"]):0.3f} m'
)
print(
    f'Impact Y Position - Standard Deviation: {np.std(dispersion_results["impactY"]):0.3f} m'
)

plt.figure()
plt.hist(dispersion_results["impactY"], bins=int(N**0.5))
plt.title("Impact Y Position")
plt.xlabel("Impact Y Position (m)")
plt.ylabel("Number of Occurences")
plt.show()

print(
    f'Impact Velocity -         Mean Value: {np.mean(dispersion_results["impactVelocity"]):0.3f} m/s'
)
print(
    f'Impact Velocity - Standard Deviation: {np.std(dispersion_results["impactVelocity"]):0.3f} m/s'
)

plt.figure()
plt.hist(dispersion_results["impactVelocity"], bins=int(N**0.5))
plt.title("Impact Velocity")
# plt.grid()
plt.xlim(-35, 0)
plt.xlabel("Velocity (m/s)")
plt.ylabel("Number of Occurences")
plt.show()

print(
    f'Initial Static Margin -             Mean Value: {np.mean(dispersion_results["initialStaticMargin"]):0.3f} c'
)
print(
    f'Initial Static Margin -     Standard Deviation: {np.std(dispersion_results["initialStaticMargin"]):0.3f} c'
)

print(
    f'Out of Rail Static Margin -         Mean Value: {np.mean(dispersion_results["outOfRailStaticMargin"]):0.3f} c'
)
print(
    f'Out of Rail Static Margin - Standard Deviation: {np.std(dispersion_results["outOfRailStaticMargin"]):0.3f} c'
)

print(
    f'Final Static Margin -               Mean Value: {np.mean(dispersion_results["finalStaticMargin"]):0.3f} c'
)
print(
    f'Final Static Margin -       Standard Deviation: {np.std(dispersion_results["finalStaticMargin"]):0.3f} c'
)

plt.figure()
plt.hist(dispersion_results["initialStaticMargin"], label="Initial", bins=int(N**0.5))
plt.hist(dispersion_results["outOfRailStaticMargin"], label="Out of Rail", bins=int(N**0.5))
plt.hist(dispersion_results["finalStaticMargin"], label="Final", bins=int(N**0.5))
plt.legend()
plt.title("Static Margin")
plt.xlabel("Static Margin (c)")
plt.ylabel("Number of Occurences")
plt.show()

print(
    f'Maximum Velocity -         Mean Value: {np.mean(dispersion_results["maxVelocity"]):0.3f} m/s'
)
print(
    f'Maximum Velocity - Standard Deviation: {np.std(dispersion_results["maxVelocity"]):0.3f} m/s'
)

plt.figure()
plt.hist(dispersion_results["maxVelocity"], bins=int(N**0.5))
plt.title("Maximum Velocity")
plt.xlabel("Velocity (m/s)")
plt.ylabel("Number of Occurences")
plt.show()

# from here 
from matplotlib.patches import Ellipse

# get dispersion data for apogee and impact X and Y position
apogeeX = np.array(dispersion_results["apogeeX"])
apogeeY = np.array(dispersion_results["apogeeY"])
impactX = np.array(dispersion_results["impactX"])
impactY = np.array(dispersion_results["impactY"])

# calculate eigen values
def eigsorted(cov):
    vals, vecs = np.linalg.eigh(cov)
    order = vals.argsort()[::-1]
    return vals[order], vecs[:, order]

# plotting
plt.figure(num=None, figsize=(8, 6), dpi=150, facecolor="w", edgecolor="k")
ax = plt.subplot(111)

# error ellipses for impact
impactCov = np.cov(impactX, impactY)
impactVals, impactVecs = eigsorted(impactCov)
impactTheta = np.degrees(np.arctan2(*impactVecs[:, 0][::-1]))
impactW, impactH = 2 * np.sqrt(impactVals)

impact_ellipses = []
for j in [1, 2, 3]:
    impactEll = Ellipse(
        xy=(np.mean(impactX), np.mean(impactY)),
        width=impactW * j,
        height=impactH * j,
        angle=impactTheta,
        color="black",
    )
    impactEll.set_facecolor((0, 0, 1, 0.2))
    impact_ellipses.append(impactEll)
    ax.add_artist(impactEll)

#  error ellipses for apogee
apogeeCov = np.cov(apogeeX, apogeeY)
apogeeVals, apogeeVecs = eigsorted(apogeeCov)
apogeeTheta = np.degrees(np.arctan2(*apogeeVecs[:, 0][::-1]))
apogeeW, apogeeH = 2 * np.sqrt(apogeeVals)

for j in [1, 2, 3]:
    apogeeEll = Ellipse(
        xy=(np.mean(apogeeX), np.mean(apogeeY)),
        width=apogeeW * j,
        height=apogeeH * j,
        angle=apogeeTheta,
        color="black",
    )
    apogeeEll.set_facecolor((0, 1, 0, 0.2))
    ax.add_artist(apogeeEll)


plt.scatter(0, 0, s=30, marker="*", color="black", label="Launch Point")

plt.scatter(apogeeX, apogeeY, s=5, marker="^", color="green", label="Simulated Apogee")

plt.scatter(impactX, impactY, s=5, marker="v", color="blue", label="Simulated Landing Point")

plt.legend()

ax.set_title(
    "1$\sigma$, 2$\sigma$ and 3$\sigma$ Dispersion Ellipses: Apogee and Lading Points"
)
ax.set_ylabel("North (m)")
ax.set_xlabel("East (m)")

# # Add background image to plot
# # You can translate the basemap by changing dx and dy (in meters)
# dx = 0
# dy = 0
# plt.imshow(img, zorder=0, extent=[-1000 - dx, 1000 - dx, -1000 - dy, 1000 - dy])
# plt.axhline(0, color="black", linewidth=0.5)
# plt.axvline(0, color="black", linewidth=0.5)
# plt.xlim(-100, 700)
# plt.ylim(-300, 300)

# # Save plot and show result
# plt.savefig(str(filename) + ".pdf", bbox_inches="tight", pad_inches=0)
# plt.savefig(str(filename) + ".svg", bbox_inches="tight", pad_inches=0)
plt.show()