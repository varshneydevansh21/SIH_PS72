import asyncio
import random
from datetime import datetime, timedelta, timezone
from shapely.geometry import Point, Polygon
from geoalchemy2.shape import from_shape

from app.db.session import _get_session_factory
from app.models.nowcast import Nowcast
from app.models.alert import Alert
from app.models.lightning_event import LightningEvent
from app.models.radar_scan import RadarScan

async def seed_data():
    factory = _get_session_factory()
    async with factory() as session:
        # Clear existing demo data
        await session.execute(Alert.__table__.delete())
        await session.execute(Nowcast.__table__.delete())
        await session.execute(LightningEvent.__table__.delete())
        await session.execute(RadarScan.__table__.delete())

        now = datetime.now(timezone.utc)
        
        # 1. Create Nowcasts (Thunderstorm Cells)
        # Generating 3 distinct cells moving across North India
        cells = []
        base_lon, base_lat = 77.2, 28.6 # Delhi area
        
        for i in range(5):
            lon_offset = random.uniform(-2.0, 2.0)
            lat_offset = random.uniform(-1.5, 1.5)
            
            center_lon = base_lon + lon_offset
            center_lat = base_lat + lat_offset
            
            # Create a rough polygon around the center
            poly = Polygon([
                (center_lon - 0.2, center_lat - 0.2),
                (center_lon + 0.2, center_lat - 0.2),
                (center_lon + 0.3, center_lat + 0.2),
                (center_lon - 0.1, center_lat + 0.3),
                (center_lon - 0.2, center_lat - 0.2)
            ])
            
            intensity = random.choice(["severe", "extreme", "moderate"])
            prob = random.uniform(0.6, 0.95)
            
            nowcast = Nowcast(
                run_time=now,
                lead_time_minutes=random.choice([15, 30, 45, 60]),
                affected_area=from_shape(poly, srid=4326),
                storm_intensity_class=intensity,
                probability=prob,
                details={
                    "speed_kmh": random.randint(30, 80),
                    "direction": random.choice(["NE", "E", "SE"]),
                    "hail_prob": random.randint(10, 80)
                }
            )
            session.add(nowcast)
            cells.append((nowcast, center_lon, center_lat))
            
        await session.commit()
        
        # 2. Create Alerts linked to Nowcasts
        for nowcast, lon, lat in cells:
            num_alerts = random.randint(1, 2)
            for _ in range(num_alerts):
                # Make alert polygon slightly larger
                alert_poly = Polygon([
                    (lon - 0.4, lat - 0.4),
                    (lon + 0.4, lat - 0.4),
                    (lon + 0.5, lat + 0.4),
                    (lon - 0.3, lat + 0.5),
                    (lon - 0.4, lat - 0.4)
                ])
                
                alert = Alert(
                    nowcast_id=nowcast.id,
                    alert_type=random.choice(["Thunderstorm Warning", "Heavy Rainfall", "Squall Line"]),
                    severity=nowcast.storm_intensity_class,
                    issue_time=now - timedelta(minutes=random.randint(5, 30)),
                    valid_until=now + timedelta(hours=random.randint(1, 3)),
                    alert_area=from_shape(alert_poly, srid=4326),
                    message=f"High risk of {nowcast.storm_intensity_class} thunderstorms in the area. Take shelter immediately."
                )
                session.add(alert)
                
        # 3. Generate lots of lightning strikes clustered around the cells
        lightning_events = []
        for nowcast, lon, lat in cells:
            # More intense storms = more lightning
            num_strikes = random.randint(50, 150)
            for _ in range(num_strikes):
                # Cluster around the storm center
                strike_lon = random.gauss(lon, 0.2)
                strike_lat = random.gauss(lat, 0.2)
                
                # Strikes in the last 30 minutes
                time_offset = random.randint(0, 1800)
                
                strike = LightningEvent(
                    event_time=now - timedelta(seconds=time_offset),
                    location=from_shape(Point(strike_lon, strike_lat), srid=4326),
                    current_ka=random.uniform(10.0, 150.0) * random.choice([1, -1]),
                    polarity=random.choice([1, -1])
                )
                lightning_events.append(strike)
                
        session.add_all(lightning_events)
        await session.commit()
        
        print(f"Successfully seeded database with {len(cells)} thunderstorm cells, {len(cells)*1.5} average alerts, and {len(lightning_events)} lightning events!")

if __name__ == "__main__":
    asyncio.run(seed_data())
