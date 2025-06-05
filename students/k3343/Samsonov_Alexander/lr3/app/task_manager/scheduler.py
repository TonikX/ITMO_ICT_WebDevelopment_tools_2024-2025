from celery.schedules import crontab

beat_schedule = {
    "fetch-new-stories-every-20-mins": {
        "task": "app.task_manager.tasks.fetch_and_store_new_stories",
        "schedule": crontab(minute="*/20"),
    },

    "fetch-top-stories-every-20-mins": {
        "task": "app.task_manager.tasks.fetch_and_store_top_stories",
        "schedule": crontab(minute="10-59/20"),
    },
}
