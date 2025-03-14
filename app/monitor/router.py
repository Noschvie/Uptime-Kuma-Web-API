from fastapi import APIRouter, Depends, HTTPException, Path
from uptime_kuma_api import UptimeKumaException

from .schemas import Monitor, MonitorUpdate, MonitorTag
from auth.schemas import JWTSession
from auth.dependencies import get_jwt_session
from config import logger as logging
from .raises import raise_monitor_not_found
from ping.utils import get_avg_pings
from uptime.utils import get_uptimes

router = APIRouter(redirect_slashes=True)


@router.get("", description="Get all Monitors")
async def get_monitors(s: JWTSession = Depends(get_jwt_session)):
    try:
        return {"monitors": s.api.get_monitors()}
    except Exception as e:
        logging.fatal(e)
        raise HTTPException(500, str(e))


@router.get("/{monitor_id}", description="Get Monitor By ID")
async def get_monitor(monitor_id: int = Path(...), s: JWTSession = Depends(get_jwt_session)):
    try:
        monitor = s.api.get_monitor(monitor_id)
    except UptimeKumaException as e:
        logging.info(e)
        raise HTTPException(404, {"message": "Monitor not found!"})
    except Exception as e:
        logging.fatal(e)
        raise HTTPException(500, str(e))

    return {"monitor": monitor}


@router.get("/{monitor_id}/dashboard", description="Get monitor dashboard data")
async def get_monitor_dashboard(
        monitor_id: int = Path(...),
        heartbeat_hours: int = 1,
        s: JWTSession = Depends(get_jwt_session)
):
    try:
        monitor = s.api.get_monitor(monitor_id)
    except UptimeKumaException as e:
        logging.info(e)
        raise HTTPException(404, {"message": "Monitor not found!"})
    except Exception as e:
        logging.fatal(e)
        raise HTTPException(500, str(e))

    response = {
        "monitor": monitor,
        "avgResponseTime": None,
        "uptime": {
            "24": None,
            "720": None,
        }
    }

    try:
        pings = await get_avg_pings(s.api)
        if monitor_id in pings:
            response["avgResponseTime"] = pings[monitor_id]
    except Exception as e:
        logging.fatal(e)
        raise HTTPException(500, str(e))

    try:
        uptimes = await get_uptimes(s.api)
        if monitor_id in uptimes:
            response["uptime"] = uptimes[monitor_id]
    except Exception as e:
        logging.fatal(e)
        raise HTTPException(500, str(e))

    try:
        beats = s.api.get_monitor_beats(monitor_id, heartbeat_hours)
        response["heartbeats"] = beats
    except Exception as e:
        logging.fatal(e)
        raise HTTPException(500, str(e))

    return response


@router.get("/{monitor_id}/cert", description="Get monitor certificate info")
async def get_monitor_cert_info(monitor_id: int = Path(...), s: JWTSession = Depends(get_jwt_session)):
    try:
        info = s.api.cert_info()
        if monitor_id not in info:
            raise_monitor_not_found()
        return info[monitor_id]
    except UptimeKumaException as e:
        logging.info(e)
        raise_monitor_not_found()
    except Exception as e:
        logging.fatal(e)
        raise HTTPException(500, str(e))


@router.post("", description="Create a Monitor")
async def create_monitor(monitor: Monitor, s: JWTSession = Depends(get_jwt_session)):
    try:
        return s.api.add_monitor(**monitor.dict())
    except TypeError as e:
        logging.error(e)
        raise HTTPException(422, str(e))
    except Exception as e:
        logging.fatal(e)
        raise HTTPException(500, str(e))


@router.patch("/{monitor_id}", description="Update a specific Monitor")
async def update_monitor(
        monitor: MonitorUpdate,
        monitor_id: int = Path(...),
        s: JWTSession = Depends(get_jwt_session)
):
    try:
        resp = s.api.edit_monitor(id_=monitor_id, **monitor.dict(exclude_unset=True))
    except UptimeKumaException as e:
        logging.info(e)
        raise_monitor_not_found()
    except TypeError as e:
        logging.error(e)
        raise HTTPException(422, str(e))
    except Exception as e:
        logging.fatal(e)
        raise HTTPException(500, str(e))

    return {**resp, "monitor": monitor.dict(exclude_unset=True)}


@router.delete("/{monitor_id}", description="Delete a specific Monitor")
async def delete_monitor(monitor_id: int = Path(...), s: JWTSession = Depends(get_jwt_session)):
    try:
        # kinda dumb the api doesnt check if th id exists he just sends an event
        return s.api.delete_monitor(monitor_id)
    except UptimeKumaException as e:
        logging.info(e)
        raise_monitor_not_found()
    except Exception as e:
        logging.fatal(e)
        raise HTTPException(500, str(e))


@router.post("/{monitor_id}/pause", description="Pause a specific Monitor")
async def pause_monitor(monitor_id: int = Path(...), s: JWTSession = Depends(get_jwt_session)):
    try:
        return s.api.pause_monitor(monitor_id)
    except UptimeKumaException as e:
        logging.info(e)
        raise_monitor_not_found()
    except Exception as e:
        logging.fatal(e)
        raise HTTPException(500, str(e))


@router.post("/{monitor_id}/resume", description="Resume a specific Monitor")
async def resume_monitor(monitor_id: int = Path(...), s: JWTSession = Depends(get_jwt_session)):
    try:
        return s.api.resume_monitor(monitor_id)
    except UptimeKumaException as e:
        logging.info(e)
        raise_monitor_not_found()
    except Exception as e:
        logging.fatal(e)
        raise HTTPException(500, str(e))


@router.get("/{monitor_id}/beats", description="Get Monitor Beats in the last N hours ( by default its 1 hour) ")
async def monitor_beats(
        monitor_id: int = Path(...),
        hours: int = 1,
        s: JWTSession = Depends(get_jwt_session)
):
    try:
        return s.api.get_monitor_beats(monitor_id, hours)
    except UptimeKumaException as e:
        logging.info(e)
        raise_monitor_not_found()
    except Exception as e:
        logging.fatal(e)
        raise HTTPException(500, str(e))


@router.post("/{monitor_id}/tag", description="Add an already created tag to a specific monitor")
async def add_monitor_tag(
        tag: MonitorTag,
        monitor_id: int = Path(...),
        s: JWTSession = Depends(get_jwt_session)
):
    try:
        return s.api.add_monitor_tag(monitor_id=monitor_id, **tag.dict())
    except UptimeKumaException as e:
        logging.info(e)
        raise HTTPException(404, {"message": "Monitor or Tag not found!"})
    except Exception as e:
        logging.fatal(e)
        raise HTTPException(500, str(e))


@router.delete("/{monitor_id}/tag", description="Delete a tag from a specific monitor")
async def delete_monitor_tag(
        tag: MonitorTag,
        monitor_id: int = Path(...),
        s: JWTSession = Depends(get_jwt_session)
):
    try:
        msg = s.api.delete_monitor_tag(monitor_id=monitor_id, **tag.dict())
    except UptimeKumaException as e:
        logging.info(e)
        raise HTTPException(404, {"message": "Monitor or Tag not found!"})
    except Exception as e:
        logging.fatal(e)
        raise HTTPException(500, str(e))
