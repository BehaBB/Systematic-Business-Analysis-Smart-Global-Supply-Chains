#!/usr/bin/env python3
"""
Batch Tracker for BuryatMyasoprom
Tracks meat batches from farm to Chinese retail with QR code integration
"""

import json
import pandas as pd
import qrcode
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass
import hashlib
import sqlite3
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class BatchEvent:
    batch_id: str
    event_type: str
    location: str
    timestamp: datetime
    temperature: Optional[float] = None
    quality_metrics: Optional[Dict] = None
    responsible_party: Optional[str] = None

class BatchTracker:
    def __init__(self, db_path: str = "data/batch_tracking.db"):
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database for batch tracking"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create batches table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS batches (
                batch_id TEXT PRIMARY KEY,
                product_type TEXT NOT NULL,
                production_date TEXT NOT NULL,
                initial_quantity_kg REAL NOT NULL,
                current_quantity_kg REAL NOT NULL,
                origin_farm TEXT NOT NULL,
                quality_grade TEXT,
                status TEXT DEFAULT 'PRODUCTION',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Create batch_events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS batch_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                location TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                temperature REAL,
                quality_metrics TEXT,
                responsible_party TEXT,
                FOREIGN KEY (batch_id) REFERENCES batches (batch_id)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_batch_events_batch_id ON batch_events(batch_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_batch_events_timestamp ON batch_events(timestamp)')
        
        conn.commit()
        conn.close()
        
        logger.info(f"Batch tracking database initialized: {self.db_path}")

    def create_batch(self, batch_data: Dict) -> Dict:
        """Create new batch with unique QR code"""
        batch_id = self._generate_batch_id(batch_data)
        
        # Validate batch data
        validation_result = self._validate_batch_data(batch_data)
        if not validation_result["valid"]:
            return validation_result
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Insert batch record
            cursor.execute('''
                INSERT INTO batches (
                    batch_id, product_type, production_date, initial_quantity_kg,
                    current_quantity_kg, origin_farm, quality_grade, status,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                batch_id,
                batch_data["product_type"],
                batch_data["production_date"],
                batch_data["quantity_kg"],
                batch_data["quantity_kg"],  # current = initial at creation
                batch_data["origin_farm"],
                batch_data.get("quality_grade", "STANDARD"),
                "PRODUCTION",
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            # Create initial production event
            self._record_event(batch_id, "PRODUCTION", batch_data["origin_farm"])
            
            # Generate QR code
            qr_code_path = self._generate_qr_code(batch_id, batch_data)
            
            conn.commit()
            
            return {
                "success": True,
                "batch_id": batch_id,
                "qr_code_path": qr_code_path,
                "message": f"Batch {batch_id} created successfully"
            }
            
        except sqlite3.IntegrityError:
            return {
                "success": False,
                "error": f"Batch {batch_id} already exists"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create batch: {str(e)}"
            }
        finally:
            conn.close()

    def _generate_batch_id(self, batch_data: Dict) -> str:
        """Generate unique batch ID"""
        timestamp = datetime.now().strftime("%Y%m%d")
        product_code = batch_data["product_type"][:3].upper()
        farm_code = batch_data["origin_farm"][:3].upper()
        
        # Create hash for uniqueness
        hash_input = f"{timestamp}{product_code}{farm_code}{batch_data['production_date']}"
        hash_suffix = hashlib.md5(hash_input.encode()).hexdigest()[:6].upper()
        
        return f"BATCH-{timestamp}-{product_code}-{farm_code}-{hash_suffix}"

    def _validate_batch_data(self, batch_data: Dict) -> Dict:
        """Validate batch creation data"""
        required_fields = ["product_type", "production_date", "quantity_kg", "origin_farm"]
        missing_fields = [field for field in required_fields if field not in batch_data]
        
        if missing_fields:
            return {
                "valid": False,
                "error": f"Missing required fields: {missing_fields}"
            }
        
        # Validate production date
        try:
            production_date = datetime.fromisoformat(batch_data["production_date"])
            if production_date > datetime.now():
                return {
                    "valid": False,
                    "error": "Production date cannot be in the future"
                }
        except ValueError:
            return {
                "valid": False,
                "error": "Invalid production date format"
            }
        
        # Validate quantity
        if batch_data["quantity_kg"] <= 0:
            return {
                "valid": False,
                "error": "Quantity must be greater than 0"
            }
        
        return {"valid": True}

    def _generate_qr_code(self, batch_id: str, batch_data: Dict) -> str:
        """Generate QR code for batch tracking"""
        qr_data = {
            "batch_id": batch_id,
            "product_type": batch_data["product_type"],
            "production_date": batch_data["production_date"],
            "origin_farm": batch_data["origin_farm"],
            "tracking_url": f"https://track.buryatmyasoprom.com/batches/{batch_id}"
        }
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(json.dumps(qr_data))
        qr.make(fit=True)
        
        # Save QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_path = f"qrcodes/{batch_id}.png"
        Path("qrcodes").mkdir(exist_ok=True)
        qr_img.save(qr_path)
        
        return qr_path

    def record_batch_event(self, batch_id: str, event_data: Dict) -> Dict:
        """Record event in batch lifecycle"""
        # Verify batch exists
        batch_info = self.get_batch_info(batch_id)
        if not batch_info["success"]:
            return batch_info
        
        event_type = event_data["event_type"]
        location = event_data["location"]
        temperature = event_data.get("temperature")
        quality_metrics = event_data.get("quality_metrics")
        responsible_party = event_data.get("responsible_party")
        
        # Record event
        event_result = self._record_event(
            batch_id, event_type, location, temperature,
            quality_metrics, responsible_party
        )
        
        if event_result["success"]:
            # Update batch status based on event type
            self._update_batch_status(batch_id, event_type, event_data)
            
            # Update quantity if this is a transfer or consumption event
            if event_type in ["TRANSFER", "PROCESSING", "SHIPMENT"]:
                quantity_change = event_data.get("quantity_change_kg", 0)
                if quantity_change != 0:
                    self._update_batch_quantity(batch_id, quantity_change)
        
        return event_result

    def _record_event(self, batch_id: str, event_type: str, location: str,
                     temperature: Optional[float] = None,
                     quality_metrics: Optional[Dict] = None,
                     responsible_party: Optional[str] = None) -> Dict:
        """Record event in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO batch_events (
                    batch_id, event_type, location, timestamp,
                    temperature, quality_metrics, responsible_party
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                batch_id,
                event_type,
                location,
                datetime.now().isoformat(),
                temperature,
                json.dumps(quality_metrics) if quality_metrics else None,
                responsible_party
            ))
            
            conn.commit()
            
            return {
                "success": True,
                "event_id": cursor.lastrowid,
                "message": f"Event recorded for batch {batch_id}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to record event: {str(e)}"
            }
        finally:
            conn.close()

    def _update_batch_status(self, batch_id: str, event_type: str, event_data: Dict):
        """Update batch status based on event type"""
        status_map = {
            "PRODUCTION": "PRODUCTION",
            "QUALITY_CHECK": "QUALITY_CONTROL",
            "PROCESSING": "PROCESSING",
            "PACKAGING": "PACKAGED",
            "STORAGE": "IN_STORAGE",
            "SHIPMENT": "IN_TRANSIT",
            "CUSTOMS": "CUSTOMS_CLEARANCE",
            "DELIVERY": "DELIVERED",
            "CONSUMPTION": "CONSUMED"
        }
        
        new_status = status_map.get(event_type)
        if new_status:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE batches 
                SET status = ?, updated_at = ?
                WHERE batch_id = ?
            ''', (new_status, datetime.now().isoformat(), batch_id))
            
            conn.commit()
            conn.close()

    def _update_batch_quantity(self, batch_id: str, quantity_change: float):
        """Update batch quantity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE batches 
            SET current_quantity_kg = current_quantity_kg + ?, updated_at = ?
            WHERE batch_id = ?
        ''', (quantity_change, datetime.now().isoformat(), batch_id))
        
        conn.commit()
        conn.close()

    def get_batch_info(self, batch_id: str) -> Dict:
        """Get complete batch information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get batch details
        cursor.execute('SELECT * FROM batches WHERE batch_id = ?', (batch_id,))
        batch_row = cursor.fetchone()
        
        if not batch_row:
            conn.close()
            return {
                "success": False,
                "error": f"Batch {batch_id} not found"
            }
        
        # Get batch events
        cursor.execute('''
            SELECT * FROM batch_events 
            WHERE batch_id = ? 
            ORDER BY timestamp DESC
        ''', (batch_id,))
        event_rows = cursor.fetchall()
        
        conn.close()
        
        # Format batch data
        batch_info = {
            "batch_id": batch_row[0],
            "product_type": batch_row[1],
            "production_date": batch_row[2],
            "initial_quantity_kg": batch_row[3],
            "current_quantity_kg": batch_row[4],
            "origin_farm": batch_row[5],
            "quality_grade": batch_row[6],
            "status": batch_row[7],
            "created_at": batch_row[8],
            "updated_at": batch_row[9]
        }
        
        # Format events
        events = []
        for event_row in event_rows:
            events.append({
                "event_id": event_row[0],
                "event_type": event_row[2],
                "location": event_row[3],
                "timestamp": event_row[4],
                "temperature": event_row[5],
                "quality_metrics": json.loads(event_row[6]) if event_row[6] else None,
                "responsible_party": event_row[7]
            })
        
        return {
            "success": True,
            "batch": batch_info,
            "events": events,
            "event_count": len(events)
        }

    def get_batch_timeline(self, batch_id: str) -> Dict:
        """Get batch timeline with key milestones"""
        batch_info = self.get_batch_info(batch_id)
        if not batch_info["success"]:
            return batch_info
        
        events = batch_info["events"]
        
        # Identify key milestones
        milestones = []
        milestone_types = ["PRODUCTION", "QUALITY_CHECK", "SHIPMENT", "CUSTOMS", "DELIVERY"]
        
        for event in events:
            if event["event_type"] in milestone_types:
                milestones.append({
                    "event_type": event["event_type"],
                    "location": event["location"],
                    "timestamp": event["timestamp"],
                    "status": "COMPLETED"
                })
        
        # Calculate time between milestones
        timeline_analysis = self._analyze_timeline(events)
        
        return {
            "batch_id": batch_id,
            "current_status": batch_info["batch"]["status"],
            "milestones": milestones,
            "timeline_analysis": timeline_analysis,
            "total_duration_days": self._calculate_total_duration(events)
        }

    def _analyze_timeline(self, events: List[Dict]) -> Dict:
        """Analyze batch timeline for insights"""
        if len(events) < 2:
            return {"analysis_available": False}
        
        # Convert events to DataFrame for analysis
        df_events = pd.DataFrame(events)
        df_events['timestamp'] = pd.to_datetime(df_events['timestamp'])
        df_events = df_events.sort_values('timestamp')
        
        # Calculate time between events
        df_events['time_since_previous'] = df_events['timestamp'].diff()
        
        # Identify bottlenecks (long delays)
        bottlenecks = []
        avg_delay = df_events['time_since_previous'].mean()
        
        for i, event in df_events.iterrows():
            if event['time_since_previous'] > avg_delay * 2:  # More than 2x average
                bottlenecks.append({
                    "event_type": event['event_type'],
                    "location": event['location'],
                    "delay_hours": round(event['time_since_previous'].total_seconds() / 3600, 1)
                })
        
        return {
            "analysis_available": True,
            "total_events": len(events),
            "average_time_between_events_hours": round(avg_delay.total_seconds() / 3600, 1),
            "bottlenecks": bottlenecks,
            "efficiency_score": self._calculate_efficiency_score(events)
        }

    def _calculate_efficiency_score(self, events: List[Dict]) -> float:
        """Calculate batch processing efficiency score (0-100)"""
        if len(events) < 3:
            return 50.0  # Default score for new batches
        
        # Score based on:
        # - Number of quality events
        # - Temperature compliance
        # - Processing time
        
        quality_events = sum(1 for e in events if e["event_type"] == "QUALITY_CHECK")
        temp_compliance = self._assess_temperature_compliance(events)
        processing_time = self._assess_processing_time(events)
        
        score = (
            (min(quality_events, 3) / 3 * 30) +  # Up to 30 points for quality checks
            (temp_compliance * 40) +               # 40 points for temperature
            (processing_time * 30)                 # 30 points for timely processing
        )
        
        return round(score, 1)

    def _assess_temperature_compliance(self, events: List[Dict]) -> float:
        """Assess temperature compliance (0-1)"""
        temp_readings = [e["temperature"] for e in events if e["temperature"] is not None]
        
        if not temp_readings:
            return 0.5  # Neutral score if no temperature data
        
        # Check if temperatures are within safe range (-20°C to -15°C)
        compliant_readings = sum(1 for temp in temp_readings if -20 <= temp <= -15)
        compliance_rate = compliant_readings / len(temp_readings)
        
        return compliance_rate

    def _assess_processing_time(self, events: List[Dict]) -> float:
        """Assess processing time efficiency (0-1)"""
        if len(events) < 2:
            return 0.5
        
        first_event = min(events, key=lambda x: x["timestamp"])
        last_event = max(events, key=lambda x: x["timestamp"])
        
        total_duration = (datetime.fromisoformat(last_event["timestamp"]) - 
                         datetime.fromisoformat(first_event["timestamp"])).total_seconds()
        
        # Ideal processing time: 7 days max
        ideal_max_seconds = 7 * 24 * 3600
        efficiency = max(0, 1 - (total_duration / ideal_max_seconds))
        
        return efficiency

    def _calculate_total_duration(self, events: List[Dict]) -> float:
        """Calculate total batch duration in days"""
        if len(events) < 2:
            return 0.0
        
        first_event = min(events, key=lambda x: x["timestamp"])
        last_event = max(events, key=lambda x: x["timestamp"])
        
        duration = (datetime.fromisoformat(last_event["timestamp"]) - 
                   datetime.fromisoformat(first_event["timestamp"])).total_seconds()
        
        return round(duration / (24 * 3600), 1)

    def scan_batch_qr(self, qr_data: str) -> Dict:
        """Process QR code scan and return batch information"""
        try:
            data = json.loads(qr_data)
            batch_id = data.get("batch_id")
            
            if not batch_id:
                return {
                    "success": False,
                    "error": "Invalid QR code data"
                }
            
            return self.get_batch_info(batch_id)
            
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Invalid QR code format"
            }

    def generate_batch_report(self, batch_id: str) -> Dict:
        """Generate comprehensive batch report"""
        batch_info = self.get_batch_info(batch_id)
        if not batch_info["success"]:
            return batch_info
        
        timeline = self.get_batch_timeline(batch_id)
        
        report = {
            "report_id": f"BATCH_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "batch_summary": batch_info["batch"],
            "timeline_analysis": timeline["timeline_analysis"],
            "quality_metrics": self._aggregate_quality_metrics(batch_info["events"]),
            "temperature_analysis": self._analyze_temperature_data(batch_info["events"]),
            "compliance_status": self._assess_compliance_status(batch_info),
            "recommendations": self._generate_batch_recommendations(batch_info, timeline),
            "generated_at": datetime.now().isoformat()
        }
        
        return report

    def _aggregate_quality_metrics(self, events: List[Dict]) -> Dict:
        """Aggregate quality metrics from all events"""
        quality_events = [e for e in events if e["quality_metrics"]]
        
        if not quality_events:
            return {"data_available": False}
        
        all_metrics = {}
        for event in quality_events:
            for key, value in event["quality_metrics"].items():
                if key not in all_metrics:
                    all_metrics[key] = []
                all_metrics[key].append(value)
        
        # Calculate averages
        aggregated = {}
        for key, values in all_metrics.items():
            if all(isinstance(v, (int, float)) for v in values):
                aggregated[key] = {
                    "average": round(sum(values) / len(values), 2),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values)
                }
        
        return {
            "data_available": True,
            "metrics": aggregated,
            "total_quality_checks": len(quality_events)
        }

    def _analyze_temperature_data(self, events: List[Dict]) -> Dict:
        """Analyze temperature data from events"""
        temp_events = [e for e in events if e["temperature"] is not None]
        
        if not temp_events:
            return {"data_available": False}
        
        temperatures = [e["temperature"] for e in temp_events]
        
        return {
            "data_available": True,
            "average_temperature": round(sum(temperatures) / len(temperatures), 1),
            "min_temperature": min(temperatures),
            "max_temperature": max(temperatures),
            "stability_score": self._calculate_temperature_stability(temperatures),
            "compliance_rate": self._assess_temperature_compliance(events)
        }

    def _calculate_temperature_stability(self, temperatures: List[float]) -> float:
        """Calculate temperature stability score (0-1)"""
        if len(temperatures) < 2:
            return 0.5
        
        # Lower standard deviation = better stability
        std_dev = np.std(temperatures)
        # Convert to score (lower std dev = higher score)
        stability = max(0, 1 - (std_dev / 5))  # Assuming 5°C std dev is worst case
        
        return round(stability, 2)

    def _assess_compliance_status(self, batch_info: Dict) -> Dict:
        """Assess overall compliance status"""
        events = batch_info["events"]
        
        # Check key compliance indicators
        has_quality_checks = any(e["event_type"] == "QUALITY_CHECK" for e in events)
        has_temperature_data = any(e["temperature"] is not None for e in events)
        has_complete_timeline = len(events) >= 5  # At least 5 key events
        
        compliance_score = (
            (1.0 if has_quality_checks else 0.3) * 0.4 +
            (1.0 if has_temperature_data else 0.3) * 0.3 +
            (1.0 if has_complete_timeline else 0.5) * 0.3
        )
        
        return {
            "overall_score": round(compliance_score, 2),
            "quality_documentation": "COMPLETE" if has_quality_checks else "INCOMPLETE",
            "temperature_monitoring": "COMPLETE" if has_temperature_data else "INCOMPLETE",
            "traceability": "COMPLETE" if has_complete_timeline else "PARTIAL"
        }

    def _generate_batch_recommendations(self, batch_info: Dict, timeline: Dict) -> List[str]:
        """Generate recommendations for batch improvement"""
        recommendations = []
        
        events = batch_info["events"]
        current_status = batch_info["batch"]["status"]
        
        # Check for missing quality checks
        quality_events = [e for e in events if e["event_type"] == "QUALITY_CHECK"]
        if len(quality_events) < 2:
            recommendations.append("Increase frequency of quality checks")
        
        # Check temperature monitoring
        temp_events = [e for e in events if e["temperature"] is not None]
        if len(temp_events) < len(events) * 0.3:  # Less than 30% of events have temp data
            recommendations.append("Improve temperature monitoring coverage")
        
        # Check for bottlenecks
        bottlenecks = timeline["timeline_analysis"].get("bottlenecks", [])
        for bottleneck in bottlenecks:
            recommendations.append(f"Address delay at {bottleneck['location']} ({bottleneck['delay_hours']} hours)")
        
        # Status-specific recommendations
        if current_status == "IN_TRANSIT":
            recommendations.append("Monitor shipment temperature closely during transit")
        elif current_status == "CUSTOMS_CLEARANCE":
            recommendations.append("Ensure all customs documents are readily available")
        
        return recommendations

# Example usage
if __name__ == "__main__":
    # Initialize batch tracker
    tracker = BatchTracker()
    
    # Create a new batch
    batch_data = {
        "product_type": "BEEF",
        "production_date": "2024-01-15",
        "quantity_kg": 5000,
        "origin_farm": "Buryat Farm 001",
        "quality_grade": "A"
    }
    
    print("Creating new batch...")
    create_result = tracker.create_batch(batch_data)
    print(f"Create Result: {json.dumps(create_result, indent=2)}")
    
    if create_result["success"]:
        batch_id = create_result["batch_id"]
        
        # Record some events
        events = [
            {
                "event_type": "QUALITY_CHECK",
                "location": "Processing Plant",
                "temperature": -18.5,
                "quality_metrics": {"bacterial_count": 1000, "color_score": 8},
                "responsible_party": "Quality Inspector 001"
            },
            {
                "event_type": "PROCESSING",
                "location": "Cutting Department",
                "quantity_change_kg": -500,  # 500kg processed
                "responsible_party": "Processor 002"
            },
            {
                "event_type": "SHIPMENT",
                "location": "Loading Dock",
                "temperature": -17.8,
                "responsible_party": "Logistics Manager"
            }
        ]
        
        for event in events:
            print(f"\nRecording event: {event['event_type']}")
            event_result = tracker.record_batch_event(batch_id, event)
            print(f"Event Result: {json.dumps(event_result, indent=2)}")
        
        # Get batch information
        print(f"\nGetting batch info for {batch_id}...")
        batch_info = tracker.get_batch_info(batch_id)
        print(f"Batch Info: {json.dumps(batch_info, indent=2)}")
        
        # Generate report
        print(f"\nGenerating batch report...")
        report = tracker.generate_batch_report(batch_id)
        print(f"Batch Report: {json.dumps(report, indent=2)}")
