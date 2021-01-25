from datetime import datetime

from api import config, worker_session, models
from api.dicom.scu import send_dicom_folder
from api.models.pipeline import PipelineRun, PipelineJob, PipelineJobError

from . import HOST_PATH_TYPE, docker, dramatiq


def _run_next_nodes(job: PipelineJob, run_id: int):
    for node in job.node.get_next_nodes():

        # TODO: Clean this up variable naming
        if node.container_is_output:
            dicom_output_task.send_with_options(args=(run_id, node.id, job.id,))
        else:
            run_node_task.send_with_options(args=(run_id, node.id, job.id,))


@dramatiq.actor(max_retries=0)
def run_node_task(run_id: int, node_id: int, previous_job_id: int = None):
    # external_sio.emit('message', f"RUNNING NODE: {node_id}, RUN: {run_id}")
    print('Got past the emit')

    # TODO: Check if all previous nodes have finished

    with worker_session() as db:
        job = PipelineJob(pipeline_run_id=run_id, pipeline_node_id=node_id, status='Created')
        job.save(db)

        if not (build := job.node.container.build):
            # TODO: ABORT AND BUILD
            print('Cant run node because container is not built')
            return

        image_tag = build.tag

        if not previous_job_id:
            src_subdir = 'input'
            prev = db.query(PipelineRun).get(run_id)
        else:
            src_subdir = 'output'
            prev = db.query(PipelineJob).get(previous_job_id)

        models.utils.copy_model_fs(prev, job, src_subdir=src_subdir)
        volumes = {
            HOST_PATH_TYPE(job.get_volume_abs_input_path()): {'bind': config.PICOM_INPUT_DIR, 'mode': 'ro'},
            HOST_PATH_TYPE(job.get_volume_abs_output_path()): {'bind': config.PICOM_OUTPUT_DIR, 'mode': 'rw'}
        }
        print(volumes)

    container: Container = docker.containers.run(image_tag, detach=True, volumes=volumes, labels=['Raiven'])
    with worker_session() as db:
        job.status = 'running'
        job.save(db)
        db.commit()

    # Long running task
    print('Waiting for container')
    # TODO: add spin wait
    exit_code = container.wait()['StatusCode']
    print('Container finished with exit code', exit_code)
    with worker_session() as db:
        job.status = 'exited'
        job.exit_code = exit_code
        job.save(db)

        if exit_code != 0:
            container.reload()
            stderr = container.logs(stdout=False, stderr=True).decode("utf-8")
            job_error = PipelineJobError(pipeline_job_id=job.id, stderr=stderr)
            job_error.save(db)
        elif job.node.is_leaf_node():
            # TODO: Handle multiple lead nodes

            # Run Complete
            run = db.query(PipelineRun).get(run_id)
            models.utils.copy_model_fs(job, run, dst_subdir='output')
            run.status = 'complete'
            run.finished_datetime = datetime.now()
            run.save(db)

            print('emit pipeline finished')
            # external_sio.emit('message', f"PIPELINE FINISHED NODE")

            # TODO: Clean up old jobs
        else:
            _run_next_nodes(job, run_id)

    # Cleaning Up Container
    container.remove()


@dramatiq.actor
def dicom_output_task(run_id: int, node_id: int, previous_job_id: int):
    with worker_session() as db:
        job = PipelineJob(pipeline_run_id=run_id, pipeline_node_id=node_id, status='Created')
        job.save(db)

        if dest := job.node.application_entity:
            prev: PipelineJob = PipelineJob.query(db).get(previous_job_id)
            print(prev)

            # Detach db first
            send_dicom_folder(dest, prev.get_abs_output_path())

    with worker_session() as db:
        job.status = 'exited'
        job.save(db)
