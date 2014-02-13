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

   def python_version_extract(target, source, env):
      ## See: http://stackoverflow.com/a/7071358/884770
      ##
      import re, os
      VERSIONFILE = source[0].path
      if os.path.isfile(VERSIONFILE):
         verstrline = open(VERSIONFILE, "rt").read()
         VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
         mo = re.search(VSRE, verstrline, re.M)
         if mo:
            verstr = mo.group(1).strip()
            fd = open(target[0].path, 'w')
            fd.write(verstr)
            fd.close()
         else:
            #raise SCons.Errors.UserError, "sdfs"
            raise Exception("Unable to find version string in %s." % (VERSIONFILE,))
      else:
         raise Exception("%s does not seem to be a file" % VERSIONFILE)

   env.Append(BUILDERS = {'PyVersionExtract': Builder(action = python_version_extract)})


   #import setuptools
   #from setuptools import setup
   from setuptools.sandbox import run_setup

   def python_package_builder(target, source, env):
      res = run_setup(source[0].path, ["sdist", "bdist_egg", "bdist_wininst"])

   env.Append(BUILDERS = {'PyPackage': Builder(action = python_package_builder)})


