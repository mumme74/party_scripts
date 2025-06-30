#!/usr/bin/env bash
#set -x  # echo on
#set -o errexit

function test_tool() {
    cmd="$1"
    cmds="$2"
    revVlu=

    for testcmd in "${cmds[@]}"; do
        res=$($testcmd --version  2> /dev/null)
        if [ "${res:0:${#cmd}}" == "$cmd" ]; then
            echo "$testcmd" # capture output from function in caller
            exit 0
        fi
    done

    echo "$cmd hittades inte, installera det först" >&2
    exit 1
}

# find python version
cmds=("py" "python3" "python")
cmd="Python "
pycmd=$(test_tool "$cmd" "${cmds[@]}")
if [ "$?" -ne "0" ]; then
    exit 1
fi


# find pip version
cmds=("pip3" "pip")
cmd="pip"
pipcmd=$(test_tool "$cmd" "${cmds[@]}")
if [ "$?" -ne "0" ]; then
    exit 1
fi


# select ativate virtualenv to run the application
case "$pycmd" in
    "py") venvcmd="venv\\Scripts\\activate " ;;
    *)    venvcmd="source venv/bin/activate " ;;
esac

# install requirements
if [ ! -d "venv" ]; then
    echo "Setting up virtual environment"
    res="$($pycmd -m venv venv 1>&1)"
    echo "Installing requirements"
    res="$($venvcmd && $pipcmd install -r requirements.txt  1>&1)"
    echo "$res"
fi

# ativate virtualenv and run the application
res="$($venvcmd && $pycmd main.py $1 1>&1 2>&2)"
echo "$res"
