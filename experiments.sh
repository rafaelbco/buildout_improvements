#!/bin/bash

VIRTUALENV="~/trt3/trt3plone/python_buildout/python-2.7/bin/virtualenv"
ZC_RECIPE_EGG_PATH="/home/rafaelbc/data/checkouts/git/buildout/zc.recipe.egg_"

function time_buildout {
    local count=$1
    local count=$1
    bin/python time_buildout.py \
        --virtualenv=${VIRTUALENV} \
        --develop=${ZC_RECIPE_EGG_PATH} \
        --count=${count} \
        "$@"
}

function echo_line {
    echo "------------------------------------------------------------------------------"
}

echo "Begin experiments"
date

echo_line
echo "Buildout: simple_buildout"
time_buildout --count=1 simple_buildout
echo

echo_line
echo "Buildout: plone_deploy_buildout with 1 instance"
time_buildout --count=1 plone_deploy_buildout -- buildout:
echo





