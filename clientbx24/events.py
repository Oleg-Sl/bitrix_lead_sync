import logging

from clientbx24.requests import Bitrix24


LIMIT_EVENTS = 2


class OfflineEvents:
    def __init__(self):
        self.bx24 = Bitrix24()
        self.logger = logging.getLogger("OfflineEvents")
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler("offline_events.log")
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def get_events_from_bx24(self, event_name, limit):
        try:
            response = self.bx24.call("event.offline.get", {
                "filter": {
                    "EVENT_NAME": event_name
                },
                "order": {"TIMESTAMP_X": "ASC"},
                "limit": limit
            })
            if not response or "result" not in response or "events" not in response["result"]:
                return

            events = response["result"]["events"]
            return events
        except Exception as e:
            self.logger.error(f"Event name - {event_name}. Error fetching events from Bitrix24 API: {e}")
            return []

    def get_events_data(self, event_name, max_requests=10):
        events_data = []
        for _ in range(max_requests):
            events = self.get_events_from_bx24(event_name, LIMIT_EVENTS)
            for event in events:
                event_data = event.get("EVENT_DATA")
                if event_data:
                    events_data.append(event_data)

            if len(events) < LIMIT_EVENTS:
                break

        return events_data
