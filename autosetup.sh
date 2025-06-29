#!/usr/bin/env bash
pycmds=('py' 'python3' 'python')
pycmd=""
for cmd in "${pycmds[@]}"; do
    res=`$cmd --version 2> /dev/null`
    if [ "${res:0:7}" == "Python " ]; then
        pycmd="$cmd"
        break
    fi
done

if [ -z "$pycmd" ]; then
    echo "python hittades inte, installera det först"
    exit 1
fi

pipcmds=("pip" "pip3")
pipcmd=""
for cmd in "${pipcmds[@]}"; do
    res=`$cmd --version 2> /dev/null`
    if [ "${res:0:3}" == "${cmd:0:3}" ]; then
        pipcmd="$cmd"
        break
    fi
done

if [ -z "$pipcmd" ]; then
    echo "pip hittades inte, installara pip först"
    exit 1
fi

# install requirements
if [ ! -d "venv" ]; then
    res=`$pipcmd install -r requirements.txt`
    res=`$pycmd -m venv venv`
fi

# ativate virtualenv and run the application
if [ "$pycmd" == "py" ]; then
    res=`venv\\Scripts\\activate && §pycmd main.py $1`
else
    res=`source venv/bin/activate && $pycmd main.py $1`
fi
