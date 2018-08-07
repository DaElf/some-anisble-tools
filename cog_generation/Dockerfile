FROM centos

RUN yum update -y \
	&&	yum-config-manager --enable epel \
	&&	yum -y install make automake gcc gcc-c++ libcurl-devel proj-devel geos-devel \
	&&	cd /tmp \
	&&	curl -L http://download.osgeo.org/gdal/2.2.3/gdal-2.2.3.tar.gz | tar zxf - \
	&&	cd gdal-2.2.3/ \
	&&	./configure --prefix=/usr/local --without-python \
	&&	make -j4 \
	&&	make install

RUN yum update -y \
	&&	yum -y install yum-utils \
	&&	yum -y groupinstall development \
	&&	yum -y install https://centos7.iuscommunity.org/ius-release.rpm \
	&&	yum -y install python36u \
	&&	yum -y install python36u-pip \
	&&	pip3.6 install boto3 \
	&&	pip3.6 install requests \
	&&	pip3.6 install awscli \
	&&  pip3.6 install xmltodict

RUN aws configure set default.region us-west-2
	
ENV sourceBucket="lsaa-staging-tar" \
	destBucket="lsaa-staging-cog" \
	sceneToProcess="L08/2017/042/035/LC08_T2AL_042035_20171225_20180412_01_A1.tar.gz"

COPY cog_the_tif.py /Cog/
COPY sha_the_file.py /Cog/

WORKDIR /Cog

CMD python3.6 cog_the_tif.py $sourceBucket $destBucket $sceneToProcess