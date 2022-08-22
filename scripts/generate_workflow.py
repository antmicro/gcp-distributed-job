#!/usr/bin/env python
import itertools
from git.repo import Repo
from git.exc import NoSuchPathError

WORKFLOW_FILE = 'workflow.yaml'
WORKFLOW_NAME = 'workflow'
SAMPLES = ['hello_world', 'shell_module', 'philosophers', 'micropython', 'tensorflow_lite_micro']
SAMPLES = ['hello_world', 'shell_module'] # test

def get_zephyr_commits(first_commit, commit_num):
    try:
        repo = Repo("zephyrproject/zephyr")
        repo.remotes.origin.fetch()
    except NoSuchPathError:
        repo = Repo.clone_from("https://github.com/zephyrproject-rtos/zephyr.git", "zephyr")
    return [repo.commit(f"{first_commit}~{i}").hexsha[:10] for i in range(commit_num)]

def generate():
    commit_sample_product = list(itertools.product(get_zephyr_commits("HEAD", 2), SAMPLES))
    zephyr_commit, sample = commit_sample_product[0]
    tasks = [f'''
  build-{zephyr_commit}-{sample}: &build-step
    container: ubuntu:bionic
    runs-on: [self-hosted, Linux, X64]
    env:
      ZEPHYR_COMMIT: {zephyr_commit}
      SAMPLE_NAME: {sample}
    steps:
    - name: Test
      run: echo $SAMPLE_NAME''',
            f'''
  simulate-{zephyr_commit}-{sample}: &simulate-step
    container: ubuntu:bionic
    runs-on: [self-hosted, Linux, X64]
    needs: [build-{zephyr_commit}-{sample}]
    env:
       SAMPLE_NAME: {sample}
    steps:
    - name: Test simulate
      run: echo $SAMPLE_NAME''']
    for zephyr_commit, sample in commit_sample_product[1:]:
        tasks.append(f'''
  build-{zephyr_commit}-{sample}:
    <<: *build-step
    env:
      ZEPHYR_COMMIT: {zephyr_commit}
      SAMPLE_NAME: {sample}''')
        tasks.append(f'''
  simulate-{zephyr_commit}-{sample}:
    <<: *simulate-step
    needs: [build-{zephyr_commit}-{sample}]
    env:
      SAMPLE_NAME: {sample}''')
    with open(WORKFLOW_FILE, 'w') as file:
        file.write(f"name: {WORKFLOW_NAME}\n")
        file.write("on: [push]\n\n")
        file.write("jobs:")
        file.write("".join(tasks))
        file.write(f'''
  results:
    container: ubuntu:bionic
    runs-on: [self-hosted, Linux, X64]
    needs: [{", ".join([f'simulate-{zephyr_commit}-{sample}' for zephyr_commit, sample in commit_sample_product])}]
    steps:
    - name: Test results
      run: echo "Working!!"''')

if __name__ == '__main__':
    generate()

