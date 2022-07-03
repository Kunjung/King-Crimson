# This file contains information on how you should structure your docker image for submission.

# Always use alpine version to minimize docker image size. If alpine version 
# is not available, use the smallest base image available.
# FROM python:3.8-alpine
FROM python:3.8.0-slim-buster as builder

# WORKDIR app

ENV PATH="/opt/venv/bin:${PATH}"

ADD ./requirements.txt /u01/requirements.txt

RUN  python -m venv /opt/venv && \
  pip install --upgrade pip && \
  pip install -r /u01/requirements.txt


# RUN python3 -m venv /opt/venv && \
#     pip3 install --no-cache-dir -r requirements.txt

# RUN python3 -m venv /opt/venv && \
#     pip3 install -r requirements.txt

FROM python:3.8.0-slim-buster

COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:${PATH}"

# This will be the base directory where our project will live. 
# The name can be anything but for now, let's name it client since 
# the bot is a single client in our game.
WORKDIR app

# ADD command adds the file or folder to the destination. 
# Since the working directory is `./client`, it copies the file inside `./client`.
ADD ./model_june_28_three_combo_12pm_safe_bid.sav .
ADD ./model_june_27_three_combo_5pm_safe_bid.sav .
ADD ./heuristic_search.py .
ADD ./mcts.py .
ADD ./callbreak.py .
ADD ./play_heuristic.py .
ADD ./bid_heuristic.py .
ADD ./monty_carlo_bidding.py .

# ADD ./app.py .
ADD ./sanic_app.py .
ADD ./requirements.txt .


# EXPOSE opens up the port to communication outside the container.
# WE ASSUME THAT YOUR SERVER WILL RUN ON THIS PORT. 
# DO NOT CHANGE THIS.
EXPOSE 7000

# CMD runs the specified command on docker image startup.
# Note that we are inside the working directory `./client` so, 
# `python app.py` is run inside the `./client` directory.
# CMD ["python3", "app.py"]
# CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=7000"]
CMD [ "python3", "-m" , "sanic", "sanic_app.app", "--host=0.0.0.0", "--port=7000"]