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
   if not env.Detect("inkscape"):
      print "Taschenmesser: Inkscape executable not found - SVG to PNG conversion won't be available."
   try:
      import scour
      return True
   except:
      print "Taschenmesser: scour missing"
      return False



def generate(env):
   from SCons.Builder import Builder

   import scour
   import os, subprocess


   def Scour(target, source, env):
      if len(source) > 1:
         raise Exception("cannot SVG multiple files")

      options = scour.scour.generateDefaultOptions()

      ## override defaults for max cleansing
      ##
      options.enable_viewboxing = True
      options.strip_comments = True
      options.strip_ids = True
      options.remove_metadata = True
      options.indent_type = None
      options.shorten_ids = True

      if env.has_key('SCOUR_OPTIONS'):
         options.__dict__.update(env['SCOUR_OPTIONS'])

      from pprint import pprint
      print
      print "Using Scour options:"
      print
      print pprint(options.__dict__)
      print

      instream = open(source[0].path, 'rb')
      outstream = open(target[0].path, 'wb')

      scour.scour.start(options, instream, outstream)

   env.Append(BUILDERS = {'Scour': Builder(action = Scour)})


   def Svg2Png(target, source, env):
      inkscape = env.Detect("inkscape")

      infile = str(source[0])
      outfile = str(target[0])

      cmd = []
      cmd.append(inkscape)
      cmd.extend(['-z', '-e', outfile])

      if env.has_key('SVG2PNG_OPTIONS'):

         if env['SVG2PNG_OPTIONS'].has_key('width'):
            width = int(env['SVG2PNG_OPTIONS']['width'])
            cmd.extend(['-w', '%d' % width])

         if env['SVG2PNG_OPTIONS'].has_key('height'):
            height = int(env['SVG2PNG_OPTIONS']['height'])
            cmd.extend(['-h', '%d' % height])

      cmd.extend([infile])

      # "C:\Program Files (x86)\Inkscape\inkscape.exe" -z -e crossbar_hiw_architecture.png -w 1024 crossbar_hiw_architecture.svg

      print ' '.join(cmd)
      subprocess.call(cmd)

   env.Append(BUILDERS = {'Svg2Png': Builder(action = Svg2Png)})
