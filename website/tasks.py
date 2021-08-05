from celery import Celery
try:
    import trainining_process as tp
except ImportError:
    from . import trainining_process

app = Celery('tasks', broker='amqp://guest:guest@localhost:5672',
             backend='db+sqlite:///database.db')
app.autodiscover_tasks()


@app.task(name="website.tasks")
def training(f1mn, f1mx, d1mn, d1mx, f2mn, f2mx, d2mn, d2mx, btch, epch, cmbntins):
    return tp.train_models(f1_min=f1mn, f1_max=f1mx, d1_min=d1mn, d1_max=d1mx, f2_min=f2mn,
                           f2_max=f2mx, d2_min=d2mn, d2_max=d2mx, batch=btch, epoch=epch, combinations=cmbntins)
