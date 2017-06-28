#!/usr/bin/env bash

cd "$(dirname "$0")"/..
NODE_ENV=production yarn build

cd "$(dirname "$0")"
bundle exec knife solo cook manchester.io
