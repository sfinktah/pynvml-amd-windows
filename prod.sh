function last {
    array=("${@}")
    last_index=$(( $# - 1 ))
    last_item=${array[$last_index]}
    echo "$last_item"
}
test -d .venv && {
    echo "attempting to load venv"
    . .venv/*/activate
}
python -m pip install build
python -m build --sdist
files=$( ls dist/*.tar.gz | sort -V )
lastfile=$( last $files )
version=${lastfile##*-}
version=${version%.tar.gz}
name="${PWD##*/}"
echo $version
python -m pip install --upgrade twine
python -m twine check "$lastfile"
python -m twine upload "$lastfile"
# twine check "$lastfile"
# twine upload "$lastfile"
# test -e .git || {
#     git-repo new-repo
#     rm README.md
#     git add LICENSE.txt README.rst setup.py version.txt update.sh test.sh prod.sh exectools/*.py
#     git commit -m 'first commit'
#     git push
# }
git add -u
# git add exectools/*.py
git commit -m "$version"
git push
sleep 15
echo python -m pip install --force-reinstall "$name==$version"
python -m pip install --force-reinstall "$name==$version"
