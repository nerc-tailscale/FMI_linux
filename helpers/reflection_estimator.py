"""
REFLECTION FUNCTIONS

Functions for estimating how much of the solar irradiance is absorbed by solar panels in opposed to being reflected away
Equation for radiation absorbed:
Radiation_absorbed = (1-dni_reflected)DNIPOA+(1-ghi_reflected)GHIPOA + (1-diffuse_reflected)DHIPOA
dni_reflected is alpha_BN in notes
ghi_reflected is alpha_dg in notes
diffuse_reflected is alpha_d in notes
"""

import math
import numpy
from helpers import astronomical_calculations
import config


# panel reflectance constant, empirical value. Solar panels with better optical coatings would have a lower value where
# as uncoated panels would have a higher value. Dust on panels increases reflectance_constant.
# 0.159 is given as an average value for polycrystalline silicon module reflectance
reflectance_constant = 0.159


def components_to_corrected_poa(DNI_component, DHI_component, GHI_component, dt):
    """
    Takes dni, dhi and ghi components of a solar panel projected irradiance and computes how much of the radiation is
    absorbed by the solar panels, in opposed to reflected away.
    :param DNI_component: poa transposed dni value(W)
    :param DHI_component: poa transposed dhi value(W)
    :param GHI_component: poa transposed ghi value(W)
    :param dt: time for estimation. For example, "2023-10-13 19:30:00+00:00"
    :return: absorbed radiation in W
    """

    # direct sunlight reflection variable, has to be computed multiple times.
    dni_reflected = __dni_reflected(dt)

    # These values do not have to be recomputed every single time as they are installation-specific, and they do not
    # even take time as an input. This could be optimized if needed.
    dhi_reflected = __dhi_reflected()
    ghi_reflected = __ghi_reflected()

    # POA_reflection_corrected or radiation absorbed by the solar panel.
    POA_reflection_corrected = ((1 - dni_reflected) * DNI_component + (1 - dhi_reflected) * DHI_component +
                                (1 - ghi_reflected) * GHI_component)

    return POA_reflection_corrected


def add_reflection_corrected_poa_to_df(df):
    """
    Adds reflection corrected POA value to dataframe with name "poa_ref_cor"
    :param df:
    :return:
    """

    # print("Adding reflection corrected POA to dataframe")

    # helper function + apply — structure

    # helper function
    def helper_components_to_corrected_poa(df):
        return components_to_corrected_poa(df["dni_poa"], df["dhi_poa"], df["ghi_poa"], df["time"])

    # applying helper function to dataset and storing result as a new column
    df["poa_ref_cor"] = df.apply(helper_components_to_corrected_poa, axis=1)

    # print("Reflection corrected POA values added.")

    return df


def add_reflection_corrected_poa_components_to_df(df):
    def helper_add_dni_ref(df):
        #  (1-alpha_BN)*BTN
        return math.fabs(1 - __dni_reflected(df["time"])) * df["dni_poa"]

    def helper_add_dhi_ref(df):
        # (1-alpha_d)*DT
        return math.fabs(1 - __dhi_reflected()) * df["dhi_poa"]

    def helper_add_ghi_ref(df):
        # (1-alpha_dg)*DTg
        return math.fabs(1 - __ghi_reflected()) * df["ghi_poa"]

    """
    BTN = dni_poa
    DTg = ghi_poa
    DT = dhi_poa
    """
    df["dni_rc"] = df.apply(helper_add_dni_ref, axis=1)
    df["dhi_rc"] = df.apply(helper_add_dhi_ref, axis=1)
    df["ghi_rc"] = df.apply(helper_add_ghi_ref, axis=1)

    return df


def __dni_reflected(dt):
    """
    Computes a constant in range [0,1] which represents how much of the direct irradiance is reflected from panel
    surfaces.
    :param dt: datetime
    :return: reflected radiation in range [0,1]

    dni_reflected denoted as alpha_BN in Williams work.

    F_B_(alpha) in "Calculation of the PV modules angular losses under field conditions by means of an analytical model"
    """

    a_r = reflectance_constant

    AOI = astronomical_calculations.get_solar_angle_of_incidence(dt)

    # upper section of the fraction equation
    upper_fraction = math.e ** (-math.cos(numpy.radians(AOI)) / a_r) - math.e ** (-1.0 / a_r)
    # lower section of the fraction equation
    lower_fraction = 1.0 - math.e ** (-1.0 / a_r)

    # fraction or alpha_BN or dni_reflected
    dni_reflected = upper_fraction / lower_fraction

    return dni_reflected


def __ghi_reflected():
    """
    Computes a constant in range [0,1] which represents how much of ground reflected irradiation is reflected away from
    solar panel surfaces. Note that this is constant for an installation.
    :return: [0,1] float, 0 no light reflected, 1 no light absorbed by panels.

    ghi reflected is denoted as alpha_d in Williams work

    F_A(beta) in "Calculation of the PV modules angular losses under field conditions by means of an analytical model"

    """

    # constants, these are from
    c1 = 4.0 / (3.0 * math.pi)

    c2 = -0.074
    a_r = reflectance_constant
    panel_tilt = numpy.radians(config.tilt)  # theta_T
    pi = math.pi

    # equation parts, part 1 is used 2 times
    part1 = math.sin(panel_tilt) + (panel_tilt - math.sin(panel_tilt)) / (1.0 - math.cos(panel_tilt))

    part2 = c1 * part1 + c2 * (part1 ** 2.0)
    part3 = (-1.0 / a_r) * part2

    ghi_reflected = math.e ** part3

    return ghi_reflected


def __dhi_reflected():
    """
    Computes a constant in range [0,1] which represents how much of atmospheric diffuse light is reflected away from
    solar panel surfaces. Constant for an installation. Almost a 1 to 1 copy of __ghi_reflected except
    "pi -" addition to part1 and "1-cos" to "1+cos" replacement in part1 as well.
    :return: [0,1] float, 0 no light reflected, 1 no light absorbed by panels.

    # denoted as alpha_dg in williams work

    F_D(beta) in "Calculation of the PV modules angular losses under field conditions by means of an analytical model"
    """
    # constants

    c1 = 4.0 / (math.pi * 3.0)
    c2 = -0.074
    a_r = reflectance_constant
    panel_tilt = numpy.radians(config.tilt)  # theta_T
    pi = math.pi

    # equation parts, part 1 is used 2 times
    part1 = math.sin(panel_tilt) + (pi - panel_tilt - math.sin(panel_tilt)) / (1.0 + math.cos(panel_tilt))

    part2 = c1 * part1 + c2 * (part1 ** 2.0)
    part3 = (-1.0 / a_r) * part2

    dhi_reflected = math.e ** part3

    return dhi_reflected
