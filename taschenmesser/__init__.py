###############################################################################
##
##  Copyright 2013 (C) Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

import gclosure
import aws
import fileutil


def generate(env):
   if aws.exists(env):
      aws.generate(env)

   if gclosure.exists(env):
      gclosure.generate(env)

   if fileutil.exists(env):
      fileutil.generate(env)


def exists(env):
   return True