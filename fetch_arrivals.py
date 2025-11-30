#!/usr/bin/env python3
import os
import json
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

API_KEY = os.environ.get("MTA_API_KEY")
if not API_KEY:
    raise SystemExit("MTA_API_KEY not set in environment")

# Stop and line for eastbound M42 at 11th Ave
STOP_ID = "MTA_403367"
LINE_REF = "M42"

URL = (
    "http://bustime.mta.info/api/siri/stop-monitoring.json"
    f"?key={API_KEY}&MonitoringRef={STOP_ID}&LineRef={LINE_REF}"
)

def iso_to_ny(iso_str):
    # API uses Z for UTC; make it parseable for fromisoformat
    if iso_str.endswith("Z"):
        iso_str = iso_str.replace("Z", "+00:00")
    dt = datetime.fromisoformat(iso_str)
    return dt.astimezone(ZoneInfo("America/New_York"))

def main():
    with urllib.request.urlopen(URL, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    visits = data.get("Siri", {}) \
                 .get("ServiceDelivery", {}) \
                 .get("StopMonitoringDelivery", [])[0] \
                 .get("MonitoredStopVisit", [])

    times = []
    for v in visits:
        mvj = v.get("MonitoredVehicleJourney", {})
        call = mvj.get("MonitoredCall", {})
        expected = call.get("ExpectedArrivalTime") or call.get("AimedArrivalTime")
        if expected:
            dt = iso_to_ny(expected)
            times.append(dt.isoformat())

    times = sorted(times)[:3]

    out = [{"arrival_time": t} for t in times]

    with open("arrivals.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
