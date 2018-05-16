FROM centos:latest

MAINTAINER USGS EROS LSRD http://eros.usgs.gov

LABEL description="Build ips software"

COPY local.repo /etc/yum.repos.d/local.repo

RUN ping -c 3 172.17.0.1
RUN yum install -y net-tools && ifconfig -a

RUN yum -y install epel-release && \
    rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7 && \
    yum -y install https://centos7.iuscommunity.org/ius-release.rpm && \
    rpm --import /etc/pki/rpm-gpg/IUS-COMMUNITY-GPG-KEY
    

RUN yum upgrade -y \
    && yum install -y \
       tcsh \
       sudo \
       python34 \
       openssl \
       junit \
       e2fsprogs \
       log4j \
       apache-commons-lang \
       python34-setuptools \
       net-tools \
       telnet \
       openssh-server \
       xterm \
       zsh \
       wget \
       python34-pip \
       python34-numpy \
       python34-scipy \
       python-setuptools \
       perl-ExtUtils-MakeMaker \
       perl-Sys-Syslog  \
       perl-DBI \
       perl-version \
       perl-Time-Piece \
       perl-Switch \
       perl-Archive-Tar \
       perl-Digest-MD5 \
       qt \
       qt-odbc \
       gsl \
       hdf \
       gctp \
       gctp3 \
       cubist \
       novas \
       odl \
       cgreen \
       shapelib \
       remez \
       rsync

#COPY oracle-instantclient12.2-* perl-DBD-Oracle*.rpm /tmp/
#RUN yum install -y /tmp/oracle-instantclient12.2-* /tmp/perl-DBD-Oracle*.rpm
#RUN rm -f /tmp/oracle-instantclient12* /rmp/perl-DBD-Oracle*.rpm

RUN yum install -y \
    oracle-instantclient12.2-jdbc \
    oracle-instantclient12.2-sqlplus \
    oracle-instantclient12.2-devel \
    oracle-instantclient12.2-basic \
    oracle-instantclient12.2-odbc \
    oracle-instantclient12.2-tools

RUN yum install -y \
    texinfo \
    createrepo \
    ant \
    git2u \
    rpm-build \
    autoheader automake autoconf libtool \
    gcc-c++ \
    libgeotiff-devel \
    libtiff-devel \
    jbigkit-devel \
    openjpeg-devel \
    libgeotiff-devel \
    hdf5-devel \
    expat-devel \
    freetype-devel \
    libcurl-devel \
    libidn-devel \
    bzip2-devel \
    zlib-devel \
    libpng-devel \
    unixODBC-devel \
    libaio-devel \
    libpng12-devel \
    libpng-devel \
    libarchive-devel \
    fftw-devel \
    libjpeg-turbo-devel \
    shapelib-devel \
    antlr-tool \
    qmake \
    yum-plugin-priorities \
    qt-devel \
    gsl-devel \
    hdf-devel

#    glibc-static \
#    libgfortran-static \
#    libquadmath-static \
#    zlib-static \
#    libpng-static
#RUN yum-config-manager --setopt="base.priority=10" ; yum-config-manager --setopt="local.priority=1" ; yum update -y
RUN yum clean metadata && \
    yum install -y \
    perl-DBD-Oracle \
    gdal-python3 \
    python2-gdal \
    qt-oci \
    perl-Env

RUN yum install -y \
     apache-commons-lang \
     apache-commons-logging \
     apache-commons-configuration \
     apache-commons-io \
     product-tools

# not the best way to handle this
RUN echo "/usr/lib/oracle/12.2/client64/lib/" > /etc/ld.so.conf.d/oracle-x86_64.conf && ldconfig
RUN pip3 install cx_oracle
COPY odbcinst.ini /tmp/odbcinst.ini
RUN cat  /tmp/odbcinst.ini >> /etc/odbcinst.ini

RUN alternatives --install /usr/bin/python3 python3 /usr/bin/python3.4 60
RUN alternatives --install /usr/bin/qmake qmake /bin/qmake-qt4 60

RUN groupadd --gid 501 ipe
RUN useradd --shell /bin/tcsh --uid 16578 --gid 100 -G wheel,ipe --password $(openssl passwd -1 rcattelan) rcattelan
RUN (cd / ; ln -s LOSRLPGD03 rcattelan-cli)

# ----------------------------------------------------------------------------
# Add an entrypoint so that we can do some internal setup and then execute the
# specified application
COPY science-entrypoint.sh /entrypoint.sh
RUN chmod 755 /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
