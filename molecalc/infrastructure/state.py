from typing import Optional

from data.gamess_ios import GamessIO
import services.data_service as svc

active_calculation: Optional[GamessIO] = None


def reload_account():
    global active_calculation
    if not active_calculation:
        return

    active_calculation = svc.find_calculation_by_hashkey(active_calculation.hashkey)
