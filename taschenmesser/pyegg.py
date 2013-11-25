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

__all__ = ['exists', 'generate']


def exists(env):
   try:
      import setuptools
      return True
   except:
      print "Taschenmesser: Setuptools missing. Python Egg creation won't be available."
      return False



def generate(env):
   from SCons.Builder import Builder

   #import setuptools
   #from setuptools import setup
   from setuptools.sandbox import run_setup

   def python_egg_builder(target, source, env):
      run_setup(source[0].path, ["bdist_egg"])

   env.Append(BUILDERS = {'Egg': Builder(action = python_egg_builder)})
