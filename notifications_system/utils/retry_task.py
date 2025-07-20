import time

def retry_task_with_backoff(task, max_retries, base_backoff=5):
    """Retries a task with exponential backoff."""
    for i in range(max_retries):
        try:
            return task()
        except Exception as e:
            time.sleep(base_backoff * (2 ** i))
    return False