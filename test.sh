function last {
    array=("${@}")
    last_index=$(( $# - 1 ))
    last_item=${array[$last_index]}
    echo "$last_item"
}
# perl -pi -e 's/VERSION="[^"]+"/VERSION="'$(cat version.txt)'"/' setup.py
test -d .venv && {
    echo "attempting to load venv"
    . .venv/*/activate
}
python -m pip install build
python -m build --sdist
# python setup.py sdist
files=$( ls dist/*.tar.gz | sort -V )
lastfile=$( last $files )
version=${lastfile##*-}
version=${version%.tar.gz}
name="${PWD##*/}"
echo $version
python -m pip install --upgrade twine
python -m twine check "$lastfile"
# twine upload --repository pypitest "$lastfile"
python -m twine upload --repository testpypi dist/*
echo "Install at:"
echo "python -m pip install -i https://test.pypi.org/simple/ $name==$version"
sleep 15
# python -m pip install --upgrade --index-url https://test.pypi.org/simple/ $name
echo "Updating cygwin pip"
python -m pip install -i https://test.pypi.org/simple/ $name==$version
# echo 'call "c:\Program Files (x86)\Microsoft Visual Studio\2017\Community\vc\Auxiliary\Build\vcvarsall.bat" x64' $'\n' "$@" | cmd 
echo "Updating windows pip"
cmd /c "python -m pip install -i https://test.pypi.org/simple/ $name==$version"
