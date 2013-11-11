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
      import hashlib, gzip
      return True
   except:
      print "Taschenmesser: Hashlibs missing"
      return False



def generate(env):
   from SCons.Builder import Builder
   import hashlib, gzip

   def gzipper(target, source, env):
      if len(source) > 1:
         raise Exception("cannot GZip multiple files")
      f_in = open(source[0].path, 'rb')
      #f_out = gzip.open(target[0].path, 'wb')
      f_out = gzip.GzipFile(target[0].path, 'wb', mtime = 0)
      f_out.writelines(f_in)
      f_out.close()
      f_in.close()


   env.Append(BUILDERS = {'GZip': Builder(action = gzipper)})
