##############################################################################
#
#  Copyright (c) Crossbar.io Technologies GmbH
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
##############################################################################

from __future__ import absolute_import

from taschenmesser import gclosure
from taschenmesser import aws
from taschenmesser import fileutil
from taschenmesser import svg
from taschenmesser import pyegg
from taschenmesser._version import __version__

version = __version__


def generate(env):
   if aws.exists(env):
      aws.generate(env)

   if gclosure.exists(env):
      gclosure.generate(env)

   if fileutil.exists(env):
      fileutil.generate(env)

   if svg.exists(env):
      svg.generate(env)

   if pyegg.exists(env):
      pyegg.generate(env)


def exists(env):
   return True
