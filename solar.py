from math import sin, cos, tan, atan, radians, degrees, floor, acos

def _julian_day(dt_utc):
    year = dt_utc.year
    month = dt_utc.month
    day = dt_utc.day + (dt_utc.hour + (dt_utc.minute + dt_utc.second/60)/60)/24
    if month <= 2:
        year -= 1
        month += 12
    A = floor(year/100)
    B = 2 - A + floor(A/4)
    return floor(365.25*(year + 4716)) + floor(30.6001*(month + 1)) + day + B - 1524.5

def _julian_century(jd):
    return (jd - 2451545.0)/36525.0

def _geom_mean_long_sun_deg(T):
    return (280.46646 + T*(36000.76983 + 0.0003032*T)) % 360.0

def _geom_mean_anom_sun_deg(T):
    return 357.52911 + T*(35999.05029 - 0.0001537*T)

def _eccent_earth_orbit(T):
    return 0.016708634 - T*(0.000042037 + 0.0000001267*T)

def _sun_eq_of_center(T, M):
    Mrad = radians(M)
    return (1.914602 - T*(0.004817 + 0.000014*T))*sin(Mrad) + (0.019993 - 0.000101*T)*sin(2*Mrad) + 0.000289*sin(3*Mrad)

def _sun_true_long(L0, C):
    return L0 + C

def _sun_app_long(T, true_long):
    omega = 125.04 - 1934.136*T
    return true_long - 0.00569 - 0.00478*sin(radians(omega))

def _mean_obliq_ecliptic(T):
    seconds = 21.448 - T*(46.815 + T*(0.00059 - T*(0.001813)))
    return 23.0 + (26.0 + (seconds/60.0))/60.0

def _obliq_corr(T, mean_obliq):
    omega = 125.04 - 1934.136*T
    return mean_obliq + 0.00256*cos(radians(omega))

def _sun_declination(obliq_corr, lambda_app):
    from math import asin
    return degrees(asin(sin(radians(obliq_corr))*sin(radians(lambda_app))))

def _eq_of_time(T, L0, e, M, obliq_corr):
    y = tan(radians(obliq_corr/2))**2
    L0r = radians(L0)
    Mr = radians(M)
    E = y*sin(2*L0r) - 2*e*sin(Mr) + 4*e*y*sin(Mr)*cos(2*L0r) - 0.5*y*y*sin(4*L0r) - 1.25*e*e*sin(2*Mr)
    return degrees(E)*4.0  # minutes

def _true_solar_time_minutes(dt_utc, lon_deg, eqtime_min):
    minutes = dt_utc.hour*60 + dt_utc.minute + dt_utc.second/60
    return (minutes + eqtime_min + 4*lon_deg) % 1440

def _hour_angle_deg(tst_minutes):
    return tst_minutes/4 - 180 if tst_minutes/4 >= 0 else tst_minutes/4 + 180

def solar_elevation(latitude_deg, longitude_deg, elevation_m, dt_utc):
    jd = _julian_day(dt_utc)
    T = _julian_century(jd)
    L0 = _geom_mean_long_sun_deg(T)
    M = _geom_mean_anom_sun_deg(T)
    e = _eccent_earth_orbit(T)
    C = _sun_eq_of_center(T, M)
    true_long = _sun_true_long(L0, C)
    lambda_app = _sun_app_long(T, true_long)
    mean_obliq = _mean_obliq_ecliptic(T)
    obliq_corr = _obliq_corr(T, mean_obliq)
    decl = _sun_declination(obliq_corr, lambda_app)
    eqtime = _eq_of_time(T, L0, e, M, obliq_corr)
    tst = _true_solar_time_minutes(dt_utc, longitude_deg, eqtime)
    ha = _hour_angle_deg(tst)

    from math import radians as r, degrees as d
    lat = r(latitude_deg); dec = r(decl); ha_r = r(ha)
    cos_zen = sin(lat)*sin(dec) + cos(lat)*cos(dec)*cos(ha_r)
    cos_zen = max(-1.0, min(1.0, cos_zen))
    zenith_deg = d(acos(cos_zen))
    elevation = 90.0 - zenith_deg
    return elevation  # geometric elevation; refraction added later
