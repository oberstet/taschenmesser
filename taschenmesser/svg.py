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

   from scour import scour
   import os, sys, subprocess


   def Scour(target, source, env):
      if len(source) > 1:
         raise Exception("cannot SVG multiple files")

      options = scour.generateDefaultOptions()

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

      if False:
         from pprint import pprint
         print
         print "Using Scour options:"
         print
         print pprint(options.__dict__)
         print

      instream = open(source[0].path, 'rb')
      outstream = open(target[0].path, 'wb')

      scour.start(options, instream, outstream)

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


   def process_svg(svg_files, source_dir, gen_dir):
      """
      Process a set of SVG files.

      :param svg_files: List of SVG (base) file names, e.g. ``["fig1.svg", "fig2.svg"]``.
      :type svg_files: list
      :param source_dir: The local directory contained source files, e.g. ``"./design/figures"``.
      :type source_dir: str
      :param gen_dir: The directory where to place generated files, e.g. ``_static/img/gen"``.
      :type gen_dir: str
      """
      imgs = []
      for svg in svg_files:
         svgOpt = env.Scour("%s/%s" % (gen_dir, svg),
                            "%s/%s" % (source_dir, svg),
                            SCOUR_OPTIONS = {'enable_viewboxing': True})
         imgs.append(svgOpt)
         imgs.append(env.GZip("%s.gz" % svgOpt[0], svgOpt))
         png = env.Svg2Png("%s.png" % os.path.splitext(str(svgOpt[0]))[0], svgOpt, SVG2PNG_OPTIONS = {})
         imgs.append(png)
         imgs.append(env.GZip("%s.gz" % png[0], png))

      return imgs

   env.process_svg = process_svg
