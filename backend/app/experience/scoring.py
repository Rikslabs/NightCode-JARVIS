"""Experience Scoring - scores experiences based on various factors."""

from datetime import datetime, timezone
from typing import List, Optional
from .models import ExperienceRecord, ExperienceScore


class ExperienceScorer:
    """
    Scores experiences based on success, recency, frequency, and duration.

    Deterministic scoring without AI.
    """

    def score(self, record: ExperienceRecord, now: Optional[str] = None) -> ExperienceScore:
        """
        Calculate score for a single experience record.

        Args:
            record: The experience record to score.
            now: Optional current timestamp for recency calculation.

        Returns:
            ExperienceScore with breakdown.
        """
        now_dt = now or datetime.now(timezone.utc).isoformat()

        # Success factor (0-1)
        success_score = 1.0 if record.success else 0.1

        # Recency factor (more recent = higher score, decays over time)
        recency_score = self._calculate_recency(record.timestamp, now_dt)

        # Duration factor (faster = higher score, normalized)
        duration_score = self._calculate_duration_score(record.duration_ms)

        # Overall score combines all factors
        overall = (success_score * 0.4 + recency_score * 0.3 + duration_score * 0.3)

        return ExperienceScore(
            record_id=record.id,
            success_score=success_score,
            recency_score=recency_score,
            frequency_score=0.5,  # Default, needs history context
            duration_score=duration_score,
            overall_score=overall,
            factors={
                "success": success_score,
                "recency": recency_score,
                "duration": duration_score,
            },
        )

    def _calculate_recency(self, timestamp: str, now: str) -> float:
        """Calculate recency score based on time difference."""
        try:
            record_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            now_time = datetime.fromisoformat(now.replace("Z", "+00:00"))

            # Hours difference
            diff_hours = (now_time - record_time).total_seconds() / 3600

            # Decay function: 1.0 for recent, approaches 0 over time
            if diff_hours < 1:
                return 1.0
            elif diff_hours < 24:
                return max(0.5, 1.0 - (diff_hours / 48))
            else:
                return 0.3
        except Exception:
            return 0.5

    def _calculate_duration_score(self, duration_ms: float) -> float:
        """Normalize duration to a score (faster = higher score)."""
        # Assume most operations take 100-10000ms
        if duration_ms < 100:
            return 1.0
        elif duration_ms < 1000:
            return 0.8
        elif duration_ms < 5000:
            return 0.6
        elif duration_ms < 10000:
            return 0.4
        else:
            return 0.2