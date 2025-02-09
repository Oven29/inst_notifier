from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger


scheduler = AsyncIOScheduler(job_defaults={'coalesce': False, 'max_instances': 100})
