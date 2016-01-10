%{?scl:%scl_package test}
%{?scl:%global eclipse_cmd_init scl enable %{scl} "eclipse -clean -debug -noexit -console -consolelog -data $HOME/work | tee ${logFile}"}
%{!?scl:%global eclipse_cmd_init eclipse -clean -debug -noexit -console -consolelog -data $HOME/work | tee ${logFile}}
%{?scl:%global eclipse_cmd scl enable %{scl} "eclipse -noexit -console"}
%{!?scl:%global eclipse_cmd eclipse -noexit -console}
Name:           %{?scl_prefix}test
Version:        42
Release:        666
Summary:        test
License:        GPL
URL:            file:/dev/null
Source0:        functions.sh
BuildRequires:  xorg-x11-server-Xvfb
BuildRequires:  java-devel
BuildRequires:  /usr/bin/time
%{?scl:BuildRequires:  %{?scl_prefix}ide}
%{!?scl:BuildRequires:  eclipse-m2e-core}

%description
test

%build
set +x
cd $HOME
. %{SOURCE0}

# Start a headless X server in background
port=$(( $RANDOM % 100 ))
Xvfb :$port &
trap "kill $!" 0
export DISPLAY=:$port
sleep 5

fail=0
logFile=log.txt

# Check for dangling symlinks
echo === BEGIN DANGLING SYMLINK REPORT === >&2
for link in `find %{?_scl_root}/usr/{share,lib,lib64}/eclipse -type l 2>/dev/null`; do
  [ -e $link ] || ( ls -l $link && fail=1 )
done
echo === END DANGLING SYMLINK REPORT === >&2

# Enable reconciler debugging output
# http://aniszczyk.org/2011/04/04/debugging-eclipse-p2-dropins/
cat <<EOF >.options
org.eclipse.equinox.p2.core/debug=true
org.eclipse.equinox.p2.core/reconciler=true
org.eclipse.equinox.p2.garbagecollector/debug=true
EOF

(
  # Wait for Eclipse to start
  echo === STARTING ECLIPSE === >&2
  sleep 60

  # Show short summary of all installed bundles
  echo === BUNDLE STATUS SUMMARY === >&2
  echo ss
  sleep 5

  # Show details of all installed bundles
#  echo === DETAILED BUNDLE DUMP === >&2
#  for b in `seq 1000`; do echo b $b; done
#  sleep 30

  # Ask Equinox to shutdown gracefully
  echo === END OF LOG === >&2
  echo exit
  echo y
) | %{eclipse_cmd_init}

grep 'INSTALLED' ${logFile} && fail=1

numOfBundles=`grep -E "(INSTALLED|RESOLVED|STARTING|ACTIVE)" ${logFile} | wc -l`
echo "There are ${numOfBundles} installed."

# How long does it take to initialize the Eclipse installation
set +e
for i in {1..5}; do
  rm -rf $HOME/.eclipse/
  (echo "exit" ; echo "y" ;) | /usr/bin/time -f "Eclipse initialization took %E" %{eclipse_cmd} -noexit -console
done
set -e

# Check for missing singleton directives
# Checks the p2 profile, so Eclipse must have run
set +e
echo === BEGIN MISSING SINGLETON REPORT === >&2
for jar in `find %{?_scl_root}/usr/{share,lib,lib64}/eclipse -name "*.jar" 2>/dev/null`; do
  mf=`unzip -p $jar 'META-INF/MANIFEST.MF'`
  jar -tf $jar | grep -q '^plugin.xml$' || echo $mf | grep -q 'Service-Component'
  if [ $? -eq 0 ]; then
    isSingleton $jar
    if [ ! $? -eq 0 ]; then
      echo "SINGLETON VIOLATION : $jar . This jar provides OSGi/Eclipse services but is not declared singleton."
      #fail=1
    fi
  fi
done
echo === END MISSING SINGLETON REPORT === >&2
set -e

if [ ${fail} -eq 1 ]; then
  exit 1
fi

%changelog
* Sat Dec 22 2012 John Doe <jdoe@localhost>
- First revision
