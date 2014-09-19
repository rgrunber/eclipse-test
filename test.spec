Name:           test
Version:        42
Release:        666
Summary:        test
License:        GPL
URL:            file:/dev/null
BuildRequires:  xorg-x11-server-Xvfb
BuildRequires:  eclipse-m2e-core

%description
test

%build
set +x
cd $HOME

# Start a headless X server in background
Xvfb :5 &
trap "kill $!" 0
export DISPLAY=:5
sleep 5

# Check for dangling symlinks
echo === BEGIN DANGLING SYMLINK REPORT === >&2
for link in `find /usr/{share,lib,lib64}/eclipse -type l 2>/dev/null`; do
  [ -e $link ] || ls -l $link
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
  echo === DETAILED BUNDLE DUMP === >&2
  for b in `seq 1000`; do echo b $b; done
  sleep 30

  # Ask Equinox to shutdown gracefully
  echo === END OF LOG === >&2
  echo exit
  echo y
) | eclipse -clean -debug -console -consolelog -data $HOME/work

# Prevent mock from creating unnecessary outout
exit 1

%changelog
* Sat Dec 22 2012 John Doe <jdoe@localhost>
- First revision
