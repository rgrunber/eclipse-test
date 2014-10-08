function readBSN () {

bsn=
manEntryPat="^[a-zA-Z-]*:"
foundBSNLine=0

unzip -p $1 'META-INF/MANIFEST.MF' | while read line; do
if [ ${foundBSNLine} -eq 1 ]; then
  echo ${line} | grep -qE ${manEntryPat}
  if [ $? -eq 0 ]; then
    echo $bsn
    break
  else
    bsn=${bsn}"`echo ${line} | sed 's/\([a-zA-Z0-9_.-]*\)\(;\)\?.*/\1/'`"
  fi
fi

echo ${line} | grep -q "Bundle-SymbolicName:"
if [ $? -eq 0 ]; then
  bsn=`echo ${line} | grep 'Bundle-SymbolicName:' | sed 's/Bundle-SymbolicName: \([a-zA-Z0-9_.-]*\)\(;\)\?.*/\1/'`
  echo ${line} | grep "Bundle-SymbolicName:" | grep -q ";"
  if [ $? -eq 0 ]; then
    echo $bsn
    break
  fi
  foundBSNLine=1
fi
done

}

function isSingleton () {
bsn=`readBSN $1`

# Get the latest Profile
latestTS=0
for p in `find $HOME/.eclipse/ -name "*.profile.gz"`; do
  file=`basename $p`
  ts=`echo ${file%.profile.gz}`
  if [ ${latestTS} -lt ${ts} ]; then
    latestTS=${ts}
  fi
done

profile=`find $HOME/.eclipse/ -name "${latestTS}.profile.gz"`

# Presence of singleton indicates it is set to false.
zcat ${profile} | grep '<unit id=' | grep \'${bsn}\' | grep -q 'singleton='
if [ $? -eq 0 ]; then
  return 1
fi

}
