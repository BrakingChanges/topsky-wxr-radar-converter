from utils import rain_rate_to_dbz

def estimate_dbz_advanced(
    rain_rate=None,
    height_km=None,
    ctc=None,
    cloud_phase=None,
    eff_radius=None,
    lifted_index=None
):
    #  Base dBZ from rain rate
    dbz = rain_rate_to_dbz(rain_rate)

    adj = 0

    # 3. Cloud-top height adjustment
    if height_km is not None:
        if height_km > 13:
            adj += 5
        elif height_km > 10:
            adj += 3
        elif height_km < 7:
            adj -= 5

    # 4. Cooling rate (CTC)
    if ctc is not None:
        if ctc < -1.5:
            adj += 4
        elif ctc < -1.0:
            adj += 2
        elif ctc > 0.2:
            adj -= 3

    # 5. Cloud phase
    if cloud_phase is not None:
        if cloud_phase.lower() == "ice":
            adj += 3
        elif cloud_phase.lower() == "water":
            adj -= 2

    # 6. Effective radius
    if eff_radius is not None:
        if eff_radius > 20:
            adj += 2
        elif eff_radius < 10:
            adj -= 2

    # 7. Lifted Index (LI)
    if lifted_index is not None:
        if lifted_index < -6:
            adj += 3
        elif lifted_index < -4:
            adj += 2
        elif lifted_index > -2:
            adj -= 3

    # 8. Final capped result
    return round(max(0, min(dbz + adj, 60)), 1)