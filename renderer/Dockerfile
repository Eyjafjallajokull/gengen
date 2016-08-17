FROM thewtex/opengl:latest
RUN apt-get install -y libyaml-cpp-dev libjpeg-dev libtiff5-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk freeglut3-dev python-dev

ADD requirements.txt .
RUN pip install -r requirements.txt

RUN mkdir -p /build_data ; chown -R user:user /build_data
ENV APP python -u /usr/src/app/main.py

ADD graphical-app-launcher.conf /etc/supervisor/conf.d/
ADD graphical-app-launcher.py /usr/bin/
ADD . /usr/src/app