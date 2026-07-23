import os
import threading
import time
from datetime import datetime

from app.generator import generate_events
from app.uploader import upload_file
from app.logger import logger


# ============================================================================
# EVENT SCHEDULER - AUTOMATIC EVENT GENERATION
# ============================================================================

class EventScheduler:
    """
    Background service for automatic event generation.
    Generates events at a configured rate with pause/resume capability.
    """

    def __init__(self, events_per_minute: int = 100):
        """
        Initialize event scheduler

        Args:
            events_per_minute: Number of events to generate per minute
        """
        self.events_per_minute = events_per_minute
        self.is_running = False
        self.is_paused = False
        self.thread = None
        self.total_events_generated = 0

    def start(self):
        """Start automatic event generation"""

        if self.is_running:
            logger.warning("Event scheduler already running")
            return

        self.is_running = True
        self.is_paused = False
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

        logger.info(
            f"Event scheduler started: {self.events_per_minute} events/minute"
        )

    def stop(self):
        """Stop automatic event generation"""

        if not self.is_running:
            logger.warning("Event scheduler not running")
            return

        self.is_running = False
        logger.info("Event scheduler stopped")

    def pause(self):
        """Pause event generation (can be resumed)"""

        if not self.is_running:
            logger.warning("Event scheduler not running")
            return

        self.is_paused = True
        logger.info("Event scheduler paused")

    def resumeScheduler(self):
        """Resume paused event generation"""

        if not self.is_running:
            logger.warning("Event scheduler not running")
            return

        if not self.is_paused:
            logger.warning("Event scheduler not paused")
            return

        self.is_paused = False
        logger.info("Event scheduler resumed")

    def get_status(self) -> dict:
        """Get current scheduler status"""

        return {
            "is_running": self.is_running,
            "is_paused": self.is_paused,
            "events_per_minute": self.events_per_minute,
            "total_events_generated": self.total_events_generated,
        }

    def _run(self):
        """Background thread: generate events at specified rate"""

        # Generate 50 events at a time (instead of 10), with longer delay between batches
        # This reduces number of Glue job triggers from 10 per minute to 5 per minute
        # and prevents "Concurrent runs exceeded" errors
        
        events_per_batch = 50  # Increased from 10
        events_per_second = self.events_per_minute / 60.0
        delay_between_batches = events_per_batch / events_per_second

        logger.info(
            f"Event generation thread started: {delay_between_batches:.2f}s between batches"
        )

        while self.is_running:

            try:

                if not self.is_paused:
                    # Generate batch of events
                    logger.info(f"Generating {events_per_batch} events...")
                    log_files = generate_events(events_per_batch)

                    # Upload to S3
                    for log_file in log_files:
                        try:
                            logger.info(f"Uploading {os.path.basename(log_file)} to S3...")
                            success = upload_file(log_file)

                            if success:
                                os.remove(log_file)
                                self.total_events_generated += events_per_batch
                                logger.info(
                                    f"✓ Events uploaded. Total: {self.total_events_generated}"
                                )
                            else:
                                logger.error(f"Failed to upload {os.path.basename(log_file)}")

                        except Exception as e:
                            logger.error(f"Failed to upload event file: {e}")

                # Sleep before next batch (use time.sleep instead of asyncio)
                time.sleep(delay_between_batches)

            except Exception as e:
                logger.error(f"Error in event generation thread: {e}")
                time.sleep(1)


# ============================================================================
# GLOBAL SCHEDULER INSTANCE
# ============================================================================

event_scheduler = EventScheduler(events_per_minute=100)

