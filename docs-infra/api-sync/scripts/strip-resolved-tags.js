#!/usr/bin/env node
/*
 * Copyright (c) 2022 Imply Data, Inc. All rights reserved.
 *
 * This software is the confidential and proprietary information
 * of Imply Data, Inc.
 */

const fs = require('fs');
const YAML = require('yaml');

const tags = process.argv.slice(2);

const content = YAML.parse(fs.readFileSync(process.stdin.fd, 'utf-8'));

const json = JSON.stringify(
  content,
  (key, value) => {
    if (tags.includes(key)) return;
    return value;
  },
  2,
);

process.stdout.write(json);
