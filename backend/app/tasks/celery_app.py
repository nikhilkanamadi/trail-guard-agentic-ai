"""Celery application factory for TrialGuard AI."""

from __future__ import annotations

from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "trialguard",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.pipeline"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_time_limit=settings.AGENT_TIMEOUT_SECONDS + 60,
    task_soft_time_limit=settings.AGENT_TIMEOUT_SECONDS,
    task_reject_on_worker_lost=True,
    result_expires=86400,  # 24 hours
)
